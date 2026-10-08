# Videos Directory

Input clips (`.mp4` / `.mov`) are not tracked in git. Each clip is identified only by its
YouTube id or an internal stem; no performer names are stored in this repository.

| Stem | Source | Notes |
|---|---|---|
| `ci_duet_sample` | public performance recording, 30 s, 720p | benchmark clip with manual phase annotations |
| `user_ci_video` | field footage (duet in a jam, 1080x1920 vertical, 29.97 fps, 3m44s) | **handheld / panning camera** (flagged by the ego-motion screen); other dancers in the background |
| `<youtube id>` | first 60-90 s of a public YouTube video | downloaded with `scripts/acquire_videos.sh`; see `DATASET.md` for inclusion rules |

Consent and licensing: footage of identifiable people is used only for pose extraction and is
never redistributed. Field recordings made for the thesis (Phase 2) require written informed
consent and ethics-committee approval before they enter the pipeline.
