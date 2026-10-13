"""
Agreement between a human reviewer (CSV exported from outputs/review/index.html) and the assistant's by-eye
verdicts (outputs/grammar/contact_check*.csv, outputs/roles/role_check.csv): raw agreement and Cohen's kappa,
on the items both judged as decidable and on all items.

Usage (repo root):  python analyses/review/agreement.py outputs/review/answers_<name>.csv
Writes outputs/review_agreement/<name>.md (+ a merged CSV with both verdicts per item).
"""
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
from sklearn.metrics import cohen_kappa_score

OUT = Path("outputs/review_agreement"); OUT.mkdir(parents=True, exist_ok=True)


def reference() -> pd.DataFrame:
    rows = []
    for rnd, f in ((1, "outputs/grammar/contact_check.csv"), (2, "outputs/grammar/contact_check_v2.csv")):
        for r in pd.read_csv(f).itertuples():
            rows.append(dict(key=f"rel_r{rnd}_{r.id:02d}", ref=r.verdict, ref_top=""))
    rc = pd.read_csv("outputs/roles/role_check.csv")
    for r in rc.itertuples():
        top = r.tracked_top_is if isinstance(r.tracked_top_is, str) else ""
        rows.append(dict(key=f"ws_{r.id:02d}", ref=r.real, ref_top=top))
    return pd.DataFrame(rows)


def block(df, a, b, title):
    both = df[(df[a] != "") & (df[b] != "")]
    dec = both[(both[a] != "unclear") & (both[b] != "unclear")]
    out = [f"### {title}", f"items answered by both: {len(both)}; decidable for both: {len(dec)}"]
    for name, d in (("all answered", both), ("decidable", dec)):
        if len(d) > 1 and d[a].nunique() + d[b].nunique() > 2:
            out.append(f"- {name}: agreement {(d[a] == d[b]).mean():.0%}, Cohen's kappa {cohen_kappa_score(d[a], d[b]):.2f}")
        elif len(d):
            out.append(f"- {name}: agreement {(d[a] == d[b]).mean():.0%} (kappa undefined: one category)")
    out.append("\n" + pd.crosstab(both[a], both[b], rownames=["human"], colnames=["assistant"]).to_markdown())
    return "\n".join(out)


def main(path):
    h = pd.read_csv(path).fillna(""); name = Path(path).stem
    m = h.merge(reference().fillna(""), on="key", how="left").fillna("")
    m["a1n"] = m.a1.replace({"yes": "yes", "no": "no"})
    m.to_csv(OUT / f"{name}_merged.csv", index=False)
    md = [f"# Human vs assistant verdicts ({name})\n",
          block(m[m.set == "releases"], "a1", "ref", "Contact releases"),
          "\n" + block(m[m.set == "weight_share"], "a1", "ref", "Weight sharing: is it real?")]
    (OUT / f"{name}.md").write_text("\n".join(md)); print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1])
