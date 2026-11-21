# Run log

Append-only record of experiment/analysis runs (no reference text).

## 2026-11-21T12:32:40Z — make_figures.py (figures for WER We Stand re-eval)

- Worktree / branch: `/home/user/wt/d` / `figures`
- Commit: `43e46dc410a9bd668cedc2a949e00081aed3a6b8` ("Add make_figures.py: rank slope chart and WER-by-length figure")
- Tree state before run: dirty only by untracked `external/` (not an input to this script); no tracked modifications.
- Command (from repo root): `python3 src/make_figures.py --results-dir results` (default `--condition as_released~`)
- Exit status: 0; wall time: 1.31 s
- Environment: Python 3.13.18, matplotlib 3.11.2 (Agg backend), numpy 2.5.3, pandas 3.0.5 (pandas/numpy not used by the script)
- Inputs (working-tree blob hash == committed `HEAD:<file>` blob hash, i.e. committed versions):
  - `results/reeval_table.csv` — `a55dcad3b2201fdc3dc338ea1a4b470b5267ccb3` (matches HEAD)
  - `results/reeval_length_buckets.csv` — `7666fecb0424dad745521076c8740d5d4f45676d` (matches HEAD)
- Upstream provenance of those tables (from `results/reeval_meta.json`): WER-We-Stand commit `9dd7f4d0580a608e53942916a37d4d417328b1b6`; HF dataset `urdu-asr/csalt-voice` revision `6f0c4fdeea94c77b4b64c4b88d5887e087566a5f`; 471 utterances, 17 models. No randomness in this script (no seed needed).
- Outputs:
  - `results/figures/rank_slope_utt_vs_corpus.png` — 1440x1280 px, 314406 bytes, sha256 `c02ee29c67e8a1e87ab9e17719f3bf4a7ae3622fc9add48dec646c7017423e94`
  - `results/figures/wer_by_length_top5.png` — 1920x840 px, 185946 bytes, sha256 `bde00030725d81f8705bfac2820a5f32eec7b9a75c96696eba5792573bf6c496`
- Sanity checks: both PNGs present and non-trivial; visually inspected. Slope chart: 17 models each side with WER labels, title shows Kendall's τ = 0.897 (matches table). Spot-checked vs `reeval_table.csv` (overall, as_released~): whisper-large-v3-ur utt 17.68 / corpus 16.25; whisper-medium-ur 28.79 / 27.18; whisper-base 163.35 / 132.22 — all match. Length chart: 5 models in both panels, buckets ≤5/6-15/>15 with n = 12/103/356 and finer ≤15/16-30/31-50/>50 with n = 115/149/115/92; legend present; no overlapping text. No NaN in plotted inputs.
- Warnings / notes: in the length chart some markers are occluded where series converge (e.g. whisper-large-v3-ur's blue circle at >15 and >50 is hidden under whisper-large-v3's orange square); cosmetic only.

## 2026-11-21T12:33:51Z — make_figures.py re-run after layout fixes

- Worktree / branch: `/home/user/wt/d` / `figures`
- Commit: `ceabdadfa83f99f6ad761a82c930f98fbdefbb76` ("make_figures: dodge overlapping markers, solid legend lines, footnote padding"); diff vs previous run touches only `length_chart()` in `src/make_figures.py`.
- Tree state before run: untracked `external/` (not an input), plus untracked outputs of the previous run (`results/RUNS.md`, `results/figures/`), which this run overwrote/appended. No tracked modifications.
- Command (from repo root): `python3 src/make_figures.py --results-dir results` (default `--condition as_released~`)
- Exit status: 0; wall time: 0.92 s
- Environment: unchanged (Python 3.13.18, matplotlib 3.11.2, Agg backend)
- Inputs (working-tree blob == `HEAD:<file>` blob): `results/reeval_table.csv` `a55dcad3b2201fdc3dc338ea1a4b470b5267ccb3`; `results/reeval_length_buckets.csv` `7666fecb0424dad745521076c8740d5d4f45676d` (both unchanged from previous run).
- Outputs:
  - `results/figures/rank_slope_utt_vs_corpus.png` — 1440x1280 px, 314406 bytes, sha256 `c02ee29c67e8a1e87ab9e17719f3bf4a7ae3622fc9add48dec646c7017423e94` (byte-identical to previous run; code path unchanged)
  - `results/figures/wer_by_length_top5.png` — 1920x840 px, 198717 bytes, sha256 `0b3582adc013486035959ffd3ca37d3f225db6b9a70b06c20db4ac428bac424d`
- Sanity checks: legend lines now solid; footnote clear of the bottom edge (~24 px margin); no text overlaps; 5 models, bucket labels/n unchanged. Hidden markers mostly fixed by the x-dodge.
- Warning: one marker is still hidden. In the finer split at 31-50 words, the whisper-large-v3-ur circle (16.60) sits under the hf-seamless-m4t-medium line (16.49 at both 16-30 and 31-50, drawn at a higher zorder), so it can't be seen even at zoom. Cause: each series' markers share its line's zorder, so lines drawn later cover earlier series' markers. The orange squares at 16-30 and 31-50 are also partly crossed by later lines. Possible fix (not applied; src/ is out of scope for this role): draw all markers in a second pass above all lines.

## 2026-11-21T12:34:54Z — make_figures.py re-run after marker-layer fix

- Worktree / branch: `/home/user/wt/d` / `figures`
- Commit: `46af62dbff5ca79f046b7836715a6ed06870c6dd` ("make_figures: draw markers above all lines so none are hidden"); diff vs previous run touches only `length_chart()` (lines at zorder 3, markers in a separate pass at zorder 10+i).
- Tree state before run: untracked `external/` (not an input) and the untracked outputs of earlier runs; no tracked modifications.
- Command (from repo root): `python3 src/make_figures.py --results-dir results` (default `--condition as_released~`)
- Exit status: 0; wall time: 1.00 s
- Environment: unchanged (Python 3.13.18, matplotlib 3.11.2, Agg backend)
- Inputs (working-tree blob == `HEAD:<file>` blob): `results/reeval_table.csv` `a55dcad3b2201fdc3dc338ea1a4b470b5267ccb3`; `results/reeval_length_buckets.csv` `7666fecb0424dad745521076c8740d5d4f45676d` (both unchanged).
- Outputs:
  - `results/figures/rank_slope_utt_vs_corpus.png` — 314406 bytes, sha256 `c02ee29c67e8a1e87ab9e17719f3bf4a7ae3622fc9add48dec646c7017423e94` (byte-identical to runs 1 and 2)
  - `results/figures/wer_by_length_top5.png` — 1920x840 px, 199139 bytes, sha256 `6b82039a337c0a1be8fcd3c56ed2f4a75716a4989e090392ad2946577e66766e`
- Sanity checks (zoomed crop of the finer-split panel): the whisper-large-v3-ur circle at 31-50 is visible; the whisper-large-v3 orange squares at 16-30 and 31-50 are fully visible, with no line crossing them. All markers are visible in both panels. Legend lines are solid, the footnote is clear of the edge, and no text overlaps.
- Warnings: none.
