# Run log

Append-only record of experiment/analysis runs (no reference text).

## 2026-11-20 (retrospective) — reeval_wws.py (produced reeval_table.*)

Logged after the fact: this run predates `RUNS.md`. Details reconstructed from
`results/reeval_meta.json` and the commit that added the tables.

- Command: `python src/reeval_wws.py --wws-dir external/WER-We-Stand --out-dir results`
- Code: `src/reeval_wws.py` as of commit f1c91c8 (tables committed in 0bd9e36)
- WER-We-Stand commit: `9dd7f4d0580a608e53942916a37d4d417328b1b6`
- References: HF `urdu-asr/csalt-voice` revision `6f0c4fdeea94c77b4b64c4b88d5887e087566a5f`
  (datasets fingerprint `83e8388afd07c2f4`), 471 utterances, split `validation`
- Models: 17; chars.json: not available (stand-in label `as_released~`)
- Bootstrap: 1000 resamples, seed 42, paired
- Wall time: about 25 s (CPU)
- Outputs: reeval_table.csv/.md (committed); reeval_per_utt.csv, reeval_codeswitch_flags.csv,
  csalt_voice_refs.json, reeval_meta.json (local only; contain reference text or provenance)

## 2026-11-21T12:32:39Z — reeval_analysis (Holm–Bonferroni columns)

- Worktree / branch: `/home/user/wt/c` / `holm-correction`
- Git commit: `aa240ca2ad98aa9fd249b4703393592eb11f6756`
- Tree status before run: dirty only by untracked `external/` (WER-We-Stand clone); no tracked changes.
- Command (from worktree root): `python3 src/reeval_analysis.py --results-dir results`
- Exit status: 0; wall time 4.5 s
- Environment: Python 3.13.18, numpy 2.5.3, pandas 3.0.5
- Provenance (from `results/reeval_meta.json`):
  - WER-We-Stand commit `9dd7f4d0580a608e53942916a37d4d417328b1b6` (matches `external/WER-We-Stand` HEAD)
  - HF dataset `urdu-asr/csalt-voice`, revision `6f0c4fdeea94c77b4b64c4b88d5887e087566a5f`, fingerprint `83e8388afd07c2f4`
  - 471 utterances, 17 models
  - Paired bootstrap: B = 1000, seed 42
- Outputs written: `results/reeval_pairwise.{csv,md}`, `results/reeval_length_buckets.{csv,md}`,
  `results/reeval_cs_by_length.{csv,md}`. New columns: `p_boot`, `family_size`, `p_holm`, `reject_holm_05`
  in pairwise and cs_by_length (standardised rows only). `reeval_length_buckets` is unchanged (byte-identical; no new columns).
- Sanity checks: 17 models in every table; pairwise 18 families x 16 adjacent pairs, `family_size` = 16;
  cs standardised 8 families (scheme x condition x metric) x 17 models, `family_size` = 17; no NaN in value/delta/CI/p
  columns (pairwise; cs standardised rows); `p_holm >= p_boot` everywhere; no Urdu-script characters in the
  regenerated tables. All pre-existing columns are identical to HEAD (same rows, same order, same values).
- Warnings: with B = 1000 the smallest attainable two-sided `p_boot` is 2/1001 ~ 0.002, so Holm rejections are
  resolution-limited (e.g. several `p_holm` = 0.052 sit just above 0.05). Pre-existing committed files
  `results/reeval_table.{csv,md}` and `results/README.md` contain isolated Arabic-script letters in normalization-rule
  descriptions (e.g. hamza merge rule); these are not reference text and were not touched by this run.

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

## 2026-11-21T12:39:19Z — reeval_analysis re-run after review fixes

- Worktree / branch: `/home/user/wt/c` / `holm-correction`
- Git commit: `0b5a19929cae382def9d909950f164760984a314` ("Holm on unrounded p, exclude untestable rows, restore p_boot_delta_le_0")
- Tree status before run: dirty only by untracked `external/`; no tracked changes.
- Command (from worktree root): `python3 src/reeval_analysis.py --results-dir results`
- Exit status: 0; wall time 4.0 s
- Environment: Python 3.13.18, numpy 2.5.3, pandas 3.0.5
- Provenance (from `results/reeval_meta.json`): WER-We-Stand commit `9dd7f4d0580a608e53942916a37d4d417328b1b6`;
  HF dataset `urdu-asr/csalt-voice` revision `6f0c4fdeea94c77b4b64c4b88d5887e087566a5f`; 471 utterances, 17 models;
  paired bootstrap B = 1000, seed 42.
- Outputs written: `results/reeval_pairwise.{csv,md}`, `results/reeval_length_buckets.{csv,md}` (unchanged),
  `results/reeval_cs_by_length.{csv,md}`.
- Changes vs HEAD tables: only `p_holm` differs (pairwise 54 rows, cs standardised 40 rows), by at most 0.0007,
  because Holm now runs on unrounded p-values (e.g. 0.052 -> 0.0519, 0.068 -> 0.0679). No change in
  `reject_holm_05` or any other column; no `p_holm` crossed 0.05. `reeval_pairwise.md` again shows `p_boot_delta_le_0`;
  legend text in both .md files updated.
- Sanity checks: same as previous run, all pass (17 models; pairwise 18 x 16, `family_size` 16; cs standardised
  8 x 17, `family_size` 17; no NaN in value/delta/CI/p columns; `p_holm >= p_boot`; no Urdu-script characters in the
  regenerated tables).

## 2026-11-21T12:39:55Z — make_figures.py re-run after label/tau fixes (DPI 150)

- Worktree / branch: `/home/user/wt/d` / `figures`
- Commit: `5fe873cdd6d59cfd5df0b994d75336ec6bfc35b5` ("make_figures: condition-aware labels and tau, honest as_released~ label"). Changes: titles use `condition_label()`; tau is computed with `scipy.stats.kendalltau` from the two plotted rankings; left axis reads "(the paper's metric)"; the footnote is derived from the smallest spec bucket; DPI 200 -> 150; `--condition` restricted to `as_released~`/`N7_numwords`.
- Tree state before run: only untracked `external/` (not an input). The previous figures and RUNS.md are committed in `81f3e6e`.
- Command (from repo root): `python3 src/make_figures.py --results-dir results` (default `--condition as_released~`)
- Exit status: 0; wall time: 1.58 s
- Environment: Python 3.13.18, matplotlib 3.11.2 (Agg), scipy 1.18.1 (newly imported; `scipy>=1.10` in requirements.txt)
- Inputs (working-tree blob == `HEAD:<file>` blob): `results/reeval_table.csv` `a55dcad3b2201fdc3dc338ea1a4b470b5267ccb3`; `results/reeval_length_buckets.csv` `7666fecb0424dad745521076c8740d5d4f45676d` (unchanged).
- Outputs:
  - `results/figures/rank_slope_utt_vs_corpus.png` — 1080x960 px, 222999 bytes, sha256 `d2fd12422bb69fb26c827c761bd55462c76bb6a69dd3428c2a75b669264c9081`
  - `results/figures/wer_by_length_top5.png` — 1440x630 px, 151286 bytes, sha256 `a2b0b526bd685ca9e04bec65db87bbe9da3efc815a078eb647669db812a7a283`
- Sanity checks:
  - Slope chart: title reads "(Kendall's τ = 0.897)" over "as released~ (reproduction of the published scoring)", and the computed τ matches the table's `kendall_tau_vs_as_released` for corpus_wer (0.897). Left header reads "(the paper's metric)". 17 models appear on each side. Spot-checked against `reeval_table.csv` (overall, as_released~): seamless-m4t-v2-large utt 29.85 (rank 7) / corpus 32.99 (rank 8); mms-1b-ur utt 42.45 (rank 10) / corpus 42.09 (rank 9). Both match.
  - Length chart: suptitle ends with "— as released~ (reproduction of the published scoring)"; the footnote reads "The ≤5 bucket has only 12 utterances (0.3% of words)"; 5 models in both panels; n = 12/103/356 and 115/149/115/92. All markers are visible (zoomed crop of the finer split), legend lines are solid, and no text overlaps.
- Warnings: none.
