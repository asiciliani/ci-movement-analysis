"""
Idea C (13 Oct exploration): novelty / predictability of the improvisation, on two symbol sequences per duet:

  words    the 1-s pose vocabulary of describe_duets.py (k-means, K_WORDS = 10, refitted here exactly as there and
           checked against outputs/describe/vocabulary_usage.csv), one word every 0.5 s per dancer. Overlapping windows
           make consecutive words nearly copies, so the analysis uses the COLLAPSED sequence (runs of the same word
           merged): "what comes next when the movement changes". Sequences are cut at detection gaps.
  states   the duet state sequence of state_grammar.frame_states (apart / near / contact / share / floor), episodes
           >= 0.3 s, collapsed.

Measures (per duet, both dancers pooled)
  H1, H2      conditional entropy (bits) of the next symbol given the previous 1 / 2 symbols, plug-in with Miller-Madow
              correction. Absolute values are biased by sequence length, so every value is compared with surrogates of
              exactly the same length:
                shuffle    the runs permuted (symbol frequencies kept, sequential order destroyed)
                markov1    sequences generated from the duet's own first-order transition matrix (tests whether two
                           symbols of context predict more than one)
              predictability = H1(shuffle) - H1(observed); higher-order structure = H2(markov1) - H2(observed)
  held-out    leave-one-duet-out cross-entropy of order-0/1/2 Markov models (add-0.5 smoothing), bits per symbol (CI)
  novelty     share of the n-grams (n = 2, 3) in the second half of each sequence that never occurred in the first half,
              vs the same surrogates (a stationary Markov-1 process sets the expected rate of "new" combinations)
CI vs salsa: salsa renders are 60 s, so CI is cut into 60-s segments and every statistic is expressed relative to its own
surrogates. Salsa words use (a) the CI vocabulary and (b) a salsa-only vocabulary with the same K.

Outputs: outputs/novelty/{per_duet.csv, segments60.csv, heldout.csv, report.md, novelty.png}
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import explore_common as C

OUT = Path("outputs/novelty"); OUT.mkdir(parents=True, exist_ok=True)
COLS = ["trunk_tilt", "inverted", "knee_L", "knee_R", "hip_L", "hip_R", "elbow_L", "elbow_R", "arm_up_L", "arm_up_R",
        "level", "stance_width", "contact", "dist_bl", "rel_level", "motion"]
K_WORDS = 10
N_SURR = 300


# ----------------------------------------------------------------------------------------------- sequences
def features(vid):
    import describe_duets as DD
    row, ev, rg, F, tr = DD.clip_analysis(vid)
    F["fps"] = float(tr.meta["fps"])
    return F


def collapse(seq):
    out = []
    for x in seq:
        if not out or out[-1] != x:
            out.append(x)
    return out


def word_sequences(F: pd.DataFrame):
    """-> {video: [collapsed sequences (lists of ints), one per contiguous run of windows per dancer]}"""
    seqs = {}
    for (v, d), g in F.sort_values("frame").groupby(["video", "dancer"]):
        step = max(int(g.fps.iloc[0] / 2), 1)
        br = np.flatnonzero(np.diff(g.frame.to_numpy()) != step) + 1
        for part in np.split(g.word.to_numpy(), br):
            if len(part) >= 4:
                seqs.setdefault(v, []).append(collapse(part.tolist()))
    return seqs


def state_sequences(vid):
    from state_grammar import frame_states, runs
    st, fps = frame_states(vid)
    s = pd.Series(st)
    seqs = []
    # cut at undetected stretches longer than the 1-s bridge (state None)
    grp = s.isna().cumsum()
    for _, g in s[s.notna()].groupby(grp[s.notna()]):
        r = [x[0] for x in runs(g.to_numpy(), fps)]
        if len(r) >= 4:
            seqs.append(collapse(r))
    return seqs


# ----------------------------------------------------------------------------------------------- statistics
def H_mm(counter: Counter) -> float:
    n = sum(counter.values())
    if n == 0:
        return np.nan
    p = np.array(list(counter.values()), float) / n
    return float(-(p * np.log2(p)).sum() + (len(counter) - 1) / (2 * n * np.log(2)))


def cond_entropy(seqs, k):
    """H(X_t | X_{t-k..t-1}) = H(k+1-grams) - H(k-grams over the same positions), Miller-Madow."""
    joint, ctx = Counter(), Counter()
    for s in seqs:
        for i in range(k, len(s)):
            joint[tuple(s[i - k:i + 1])] += 1; ctx[tuple(s[i - k:i])] += 1
    if sum(joint.values()) < 10:
        return np.nan
    return H_mm(joint) - (H_mm(ctx) if k else 0.0)


def late_novelty(seqs, n):
    """Share of n-grams in the second half of each sequence never seen before in that duet (first halves pooled)."""
    first, second = set(), []
    for s in seqs:
        h = len(s) // 2
        first |= {tuple(s[i:i + n]) for i in range(0, h - n + 1)}
        second += [tuple(s[i:i + n]) for i in range(h, len(s) - n + 1)]
    seen = set(first); new = 0
    for g in second:
        new += g not in seen; seen.add(g)
    return new / len(second) if second else np.nan


def transition_matrix(seqs, symbols):
    idx = {s: i for i, s in enumerate(symbols)}; T = np.zeros((len(symbols), len(symbols)))
    for s in seqs:
        for a, b in zip(s[:-1], s[1:]):
            T[idx[a], idx[b]] += 1
    return T


def surrogate(seqs, kind, rng, symbols):
    if kind == "shuffle":          # permute the runs across all sequences of the duet, keep lengths; re-collapse
        pool = [x for s in seqs for x in s]; pool = [pool[i] for i in rng.permutation(len(pool))]
        bounds = np.cumsum([0] + [len(s) for s in seqs])
        starts = set(bounds[:-1].tolist())
        for _ in range(50):          # remove adjacent repeats by random swaps (collapsed sequences have none)
            bad = [i for i in range(1, len(pool)) if i not in starts and pool[i] == pool[i - 1]]
            if not bad:
                break
            for i in bad:
                j = int(rng.integers(len(pool))); pool[i], pool[j] = pool[j], pool[i]
        return [pool[a:b] for a, b in zip(bounds[:-1], bounds[1:])]
    T = transition_matrix(seqs, symbols) + 1e-9
    np.fill_diagonal(T, 0)
    cum = np.cumsum(T / T.sum(1, keepdims=True), axis=1)
    out = []
    for s in seqs:                   # same length, same first symbol, no self-transitions (collapsed)
        cur = symbols.index(s[0]); seq = [s[0]]
        for u in rng.random(len(s) - 1):
            cur = min(int(np.searchsorted(cum[cur], u * cum[cur, -1])), len(symbols) - 1); seq.append(symbols[cur])
        out.append(seq)
    return out


def measures(seqs):
    return dict(n_symbols=sum(len(s) for s in seqs), H0=cond_entropy(seqs, 0), H1=cond_entropy(seqs, 1), H2=cond_entropy(seqs, 2),
                nov2=late_novelty(seqs, 2), nov3=late_novelty(seqs, 3))


def analyse(args):
    key, seqs, seed = args
    rng = np.random.default_rng(seed)
    symbols = sorted({x for s in seqs for x in s}, key=str)
    obs = measures(seqs); row = dict(key=key, n_seqs=len(seqs), n_distinct=len(symbols), **obs)
    for kind in ("shuffle", "markov1"):
        S = pd.DataFrame([measures(surrogate(seqs, kind, rng, symbols)) for _ in range(N_SURR)])
        for m in ("H1", "H2", "nov2", "nov3"):
            x = S[m].dropna()
            if len(x) < 20 or not np.isfinite(obs[m]):
                continue
            row[f"{m}_{kind}"] = float(x.mean())
            row[f"{m}_{kind}_p_low"] = float((np.sum(x <= obs[m]) + 1) / (len(x) + 1))     # observed lower than surrogate
            row[f"{m}_{kind}_p_high"] = float((np.sum(x >= obs[m]) + 1) / (len(x) + 1))
    return row


def heldout(seq_by_duet, alpha=0.5):
    """Leave-one-duet-out cross-entropy (bits/symbol) of order-0/1/2 Markov models with additive smoothing."""
    symbols = sorted({x for ss in seq_by_duet.values() for s in ss for x in s}, key=str); V = len(symbols); rows = []
    for test in seq_by_duet:
        train = [s for d, ss in seq_by_duet.items() if d != test for s in ss]
        row = dict(video=test)
        for k in (0, 1, 2):
            cj, cc = Counter(), Counter()
            for s in train:
                for i in range(k, len(s)):
                    cj[tuple(s[i - k:i + 1])] += 1; cc[tuple(s[i - k:i])] += 1
            ll, n = 0.0, 0
            for s in seq_by_duet[test]:
                for i in range(2, len(s)):                         # same positions for every order
                    g = tuple(s[i - k:i + 1]); c = tuple(s[i - k:i])
                    ll += np.log2((cj[g] + alpha) / (cc[c] + alpha * V)); n += 1
            row[f"bits_order{k}"] = -ll / max(n, 1); row["n"] = n
        rows.append(row)
    return pd.DataFrame(rows)


def segments(seq_by_duet, seg_symbols):
    """Consecutive chunks of each duet's collapsed sequences (in their original order, long pieces split) holding
    ~seg_symbols symbols each, so that CI units have the same length as a salsa unit."""
    out = {}
    for d, ss in seq_by_duet.items():
        cur, n, i = [], 0, 0
        for s_ in ss:
            for j in range(0, len(s_), seg_symbols):
                part = s_[j:j + seg_symbols]
                if len(part) < 2:
                    continue
                cur.append(part); n += len(part)
                if n >= seg_symbols:
                    out[f"{d}#{i}"] = cur; cur, n, i = [], 0, i + 1
    return out


def phase_randomized_words(F, sc, km, rng, min_len=8):
    """Multivariate phase randomisation of each contiguous run of 1-s window features (same random phases for all 16
    standardised features: keeps every feature's autocorrelation and the cross-correlations, destroys anything
    non-linear), re-quantised with the same k-means. -> {video: collapsed sequences}. Tests whether the predictability of
    the next word is more than what any smooth multichannel signal cut into k-means cells would show."""
    seqs = {}
    for (v, d), g in F.sort_values("frame").groupby(["video", "dancer"]):
        step = max(int(g.fps.iloc[0] / 2), 1)
        br = np.flatnonzero(np.diff(g.frame.to_numpy()) != step) + 1
        Z = g["_Z"].tolist()
        for idx in np.split(np.arange(len(g)), br):
            if len(idx) < min_len:
                continue
            X = np.array([Z[i] for i in idx]); n = len(X)
            Fx = np.fft.rfft(X - X.mean(0), axis=0)
            ph = rng.uniform(0, 2 * np.pi, len(Fx)); ph[0] = 0
            if n % 2 == 0:
                ph[-1] = 0
            Xs = np.fft.irfft(Fx * np.exp(1j * ph)[:, None], n=n, axis=0) + X.mean(0)
            seqs.setdefault(v, []).append(collapse(km.predict(Xs).tolist()))
    return seqs


def runs_min(seq_by_duet, F, min_len=8):
    """Observed collapsed sequences restricted to runs of >= min_len windows (same runs as the phase surrogate)."""
    out = {}
    for (v, d), g in F.sort_values("frame").groupby(["video", "dancer"]):
        step = max(int(g.fps.iloc[0] / 2), 1)
        br = np.flatnonzero(np.diff(g.frame.to_numpy()) != step) + 1
        for part in np.split(g.word.to_numpy(), br):
            if len(part) >= min_len:
                out.setdefault(v, []).append(collapse(part.tolist()))
    return out


# ----------------------------------------------------------------------------------------------- main
def main():
    ci, salsa = C.ci_videos(), C.salsa_videos()
    cache = OUT / "features_cache.pkl"
    if cache.exists():
        F, Fs_ = pd.read_pickle(cache)
    else:
        with ProcessPoolExecutor(3) as ex:
            Fs = list(ex.map(features, ci + salsa))
        F = pd.concat(Fs[:len(ci)], ignore_index=True); Fs_ = pd.concat(Fs[len(ci):], ignore_index=True)
        pd.to_pickle((F, Fs_), cache)
    # CI vocabulary exactly as describe_duets.py
    X = F[COLS].copy(); X["dist_bl"] = X["dist_bl"].clip(upper=3); med = X.median(); X = X.fillna(med)
    sc = StandardScaler().fit(X); km = KMeans(K_WORDS, n_init=10, random_state=0).fit(sc.transform(X)); F["word"] = km.labels_
    usage = pd.crosstab(F.video, F.word, normalize="index").round(3)
    ref = pd.read_csv("outputs/describe/vocabulary_usage.csv", index_col=0)
    ref.columns = ref.columns.astype(int)
    repro = float(np.abs(usage.reindex_like(ref) - ref).max().max()) if set(ref.index) == set(usage.index) else np.nan
    print(f"[novelty] vocabulary reproduction: max |usage diff| vs outputs/describe = {repro:.3f}")
    Xs = Fs_[COLS].copy(); Xs["dist_bl"] = Xs["dist_bl"].clip(upper=3); Xs = Xs.fillna(med)
    Fs_["word"] = km.predict(sc.transform(Xs))
    Fo = Fs_.copy()
    Xo = Fo[COLS].copy(); Xo["dist_bl"] = Xo["dist_bl"].clip(upper=3); Xo = Xo.fillna(Xo.median())
    Fo["word"] = KMeans(K_WORDS, n_init=10, random_state=0).fit_predict(StandardScaler().fit_transform(Xo))
    sal_usage = pd.crosstab(Fs_.video, Fs_.word, normalize="index").round(3)

    W_ci, W_sa, W_so = word_sequences(F), word_sequences(Fs_), word_sequences(Fo)
    with ProcessPoolExecutor(3) as ex:
        S_ci = dict(zip(ci, ex.map(state_sequences, ci))); S_sa = dict(zip(salsa, ex.map(state_sequences, salsa)))
    # symbols per second of the collapsed word sequence, to cut CI into 60-s-equivalent segments
    sal_len = int(np.median([sum(len(s) for s in ss) for ss in W_sa.values()]))
    jobs = []
    for name, d in (("words_CI", W_ci), ("words_salsa_CIvocab", W_sa), ("words_salsa_ownvocab", W_so), ("states_CI", S_ci), ("states_salsa", S_sa)):
        jobs += [(f"{name}|{v}", ss, i) for i, (v, ss) in enumerate(d.items()) if ss]
    seg = segments(W_ci, sal_len)
    jobs += [(f"words_CI_seg|{k}", ss, 1000 + i) for i, (k, ss) in enumerate(seg.items())]
    with ProcessPoolExecutor(3) as ex:
        R = pd.DataFrame(list(ex.map(analyse, jobs)))
    # phase-randomised feature surrogates (smooth-signal control) on runs >= 8 windows
    F["_Z"] = list(sc.transform(X)); rng = np.random.default_rng(5)
    obs8 = runs_min(None, F)
    PR = []
    for v, ss in obs8.items():
        o = cond_entropy(ss, 1); sh = []; ph = []
        for _ in range(100):
            sh.append(cond_entropy(surrogate(ss, "shuffle", rng, sorted({x for q in ss for x in q})), 1))
        for _ in range(100):
            q = phase_randomized_words(F[F.video == v], sc, km, rng).get(v, [])
            ph.append((cond_entropy(q, 1), cond_entropy(surrogate(q, "shuffle", rng, sorted({x for z in q for x in z})), 1)) if q else (np.nan, np.nan))
        ph = np.array(ph, float)
        gain_obs = np.nanmean(sh) - o; gain_ph = ph[:, 1] - ph[:, 0]
        PR.append(dict(video=v, n_symbols=sum(len(q) for q in ss), H1=o, H1_shuffle=float(np.nanmean(sh)), gain_obs=gain_obs,
                       gain_phase_mean=float(np.nanmean(gain_ph)), gain_phase_p_high=float((np.sum(gain_ph >= gain_obs) + 1) / (np.isfinite(gain_ph).sum() + 1)),
                       H1_phase_mean=float(np.nanmean(ph[:, 0]))))
    PR = pd.DataFrame(PR); PR.to_csv(OUT / "phase_control.csv", index=False)
    print(PR.round(3).to_string())
    R[["set", "unit"]] = R.key.str.split("|", expand=True)
    R.to_csv(OUT / "per_duet.csv", index=False)
    HO = heldout(W_ci); HO["set"] = "words_CI"; HO2 = heldout(S_ci); HO2["set"] = "states_CI"
    HO = pd.concat([HO, HO2]); HO.to_csv(OUT / "heldout.csv", index=False)
    report(R, HO, repro, usage, sal_usage, sal_len, PR)


def report(R, HO, repro, usage, sal_usage, sal_len, PR):
    R = R.copy()
    R["gain_H1_vs_shuffle"] = R.H1_shuffle - R.H1; R["gain_H2_vs_markov1"] = R.H2_markov1 - R.H2
    R["nov3_minus_markov1"] = R.nov3 - R.nov3_markov1; R["nov2_minus_markov1"] = R.nov2 - R.nov2_markov1
    md = ["# Idea C: predictability and novelty of the improvisation\n",
          f"Vocabulary refitted exactly as describe_duets.py: max |usage difference| vs outputs/describe/vocabulary_usage.csv = {repro:.3f}.\n",
          "H0/H1/H2 = entropy of the next symbol given 0/1/2 previous symbols (bits, Miller-Madow), collapsed sequences. "
          "`_shuffle` / `_markov1` = surrogate means (same length and frequencies / same first-order transitions). "
          "`nov3` = share of 3-grams in the second half never seen before.\n"]
    cols = ["set", "unit", "n_symbols", "n_distinct", "H0", "H1", "H1_shuffle", "H1_shuffle_p_low", "H2", "H2_markov1", "H2_markov1_p_low",
            "nov2", "nov2_markov1", "nov3", "nov3_shuffle", "nov3_markov1", "nov3_markov1_p_low", "nov3_markov1_p_high"]
    for s in ("words_CI", "states_CI", "words_salsa_CIvocab", "words_salsa_ownvocab", "states_salsa"):
        md.append(f"\n## {s}\n\n" + R[R.set == s][cols].round(3).to_markdown(index=False))
    summ = R.groupby("set").agg(units=("unit", "size"), n_symbols=("n_symbols", "median"), H0=("H0", "median"), H1=("H1", "median"),
                                gain_H1_vs_shuffle=("gain_H1_vs_shuffle", "median"), H1_sig_lower_than_shuffle=("H1_shuffle_p_low", lambda p: int((p < 0.05).sum())),
                                gain_H2_vs_markov1=("gain_H2_vs_markov1", "median"), H2_sig_lower_than_markov1=("H2_markov1_p_low", lambda p: int((p < 0.05).sum())),
                                nov3=("nov3", "median"), nov3_minus_markov1=("nov3_minus_markov1", "median"),
                                nov3_sig_low=("nov3_markov1_p_low", lambda p: int((p < 0.05).sum())), nov3_sig_high=("nov3_markov1_p_high", lambda p: int((p < 0.05).sum())))
    md.append("\n\n## Summary (median over units; counts of units with surrogate p < 0.05)\n\n" + summ.round(3).to_markdown())
    a = R[R.set == "words_CI_seg"]; b = R[R.set == "words_salsa_CIvocab"]; c = R[R.set == "words_salsa_ownvocab"]
    tests = []
    for m in ("H0", "H1", "gain_H1_vs_shuffle", "gain_H2_vs_markov1", "nov3", "nov3_minus_markov1"):
        for nm, o in (("salsa CI-vocab", b), ("salsa own-vocab", c)):
            if len(o[m].dropna()) >= 3 and len(a[m].dropna()) >= 3:
                tests.append(dict(measure=m, contrast=f"CI 60-s-equivalent segments vs {nm}", ci_median=a[m].median(), salsa_median=o[m].median(),
                                  n_ci=a[m].notna().sum(), n_salsa=o[m].notna().sum(), mannwhitney_p=stats.mannwhitneyu(a[m].dropna(), o[m].dropna()).pvalue))
    md.append(f"\n\n## CI vs salsa at equal length ({sal_len} collapsed word symbols per segment; CI segments from the same duet are not independent)\n\n"
              + pd.DataFrame(tests).round(4).to_markdown(index=False))
    md.append("\n\n## Smooth-signal control (CI words, runs >= 8 windows)\n\nGain = H1(shuffle) - H1. `gain_phase_mean` = the same gain for "
              "multivariate phase-randomised features re-quantised with the same k-means (100 surrogates); `gain_phase_p_high` = share of "
              "surrogates with a gain at least as large as observed.\n\n" + PR.round(3).to_markdown(index=False))
    md.append("\n\nSalsa word usage with the CI vocabulary (alphabet collapse check):\n\n" + sal_usage.to_markdown())
    md.append("\n\n## Held-out (leave-one-duet-out) cross-entropy, bits per symbol, CI\n\n" + HO.round(3).to_markdown(index=False))
    md.append("\n\nMedian held-out gain order0 -> order1: words %.3f bits, states %.3f bits; order1 -> order2: words %.3f, states %.3f." % (
        (HO[HO.set == "words_CI"].bits_order0 - HO[HO.set == "words_CI"].bits_order1).median(),
        (HO[HO.set == "states_CI"].bits_order0 - HO[HO.set == "states_CI"].bits_order1).median(),
        (HO[HO.set == "words_CI"].bits_order1 - HO[HO.set == "words_CI"].bits_order2).median(),
        (HO[HO.set == "states_CI"].bits_order1 - HO[HO.set == "states_CI"].bits_order2).median()))
    (OUT / "report.md").write_text("\n".join(md)); print("\n".join(md[-8:]))

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    sets = ["words_CI", "words_CI_seg", "words_salsa_CIvocab", "words_salsa_ownvocab", "states_CI"]
    for i, (m, t) in enumerate((("gain_H1_vs_shuffle", "bits gained by knowing the current symbol\n(H1 shuffle - H1 observed)"),
                                ("nov3_minus_markov1", "late 3-gram novelty minus Markov-1 surrogate"))):
        ax[i].boxplot([R[R.set == s][m].dropna() for s in sets], labels=["CI\nwords", "CI words\n60-s seg", "salsa\nCI vocab", "salsa\nown vocab", "CI\nstates"])
        ax[i].axhline(0, c="k", lw=0.6); ax[i].set_title(t, fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "novelty.png", dpi=130)


if __name__ == "__main__":
    main()
