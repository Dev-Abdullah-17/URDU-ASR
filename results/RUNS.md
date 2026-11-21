# Run log

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
