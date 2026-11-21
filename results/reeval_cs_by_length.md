# Code-switch flag vs length

Flagged = extended detector (Latin letters or Urdu-script loanword) on the raw reference. Per-bucket rows compare flagged vs unflagged utterances of the same length bucket. `standardised` rows weight each group's per-bucket corpus metric by the pooled word share of the bucket, using only buckets where both groups have >= 5 utterances (`buckets_used`), with a 1000-resample bootstrap CI (seed 42) of the difference; resamples that leave a cell empty are dropped (`n_valid_resamples`). For the standardised rows, `p_boot` is the two-sided bootstrap p-value and `p_holm` the Holm–Bonferroni adjustment over all models (one family per scheme × condition × metric, size in `family_size`); `reject_holm_05` = p_holm < 0.05.

## as_released~ — corpus_wer — buckets: spec

| model | bucket | n_flagged | n_unflagged | flagged | unflagged | delta | ci_low | ci_high | ci_includes_0 | p_boot | p_holm | reject_holm_05 | n_valid_resamples | buckets_used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hf-seamless-m4t-medium | <=5 | 0 | 12 |  | 60.98 |  |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 6-15 | 3 | 100 | 20.0 | 34.03 | -14.03 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | >15 | 61 | 295 | 15.06 | 17.66 | -2.59 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | standardised | 61 | 295 | 15.06 | 17.66 | -2.59 | -6.07 | 1.4 | True | 0.1858 | 1.0 | False | 1000 | >15 |
| mms-1b-all | <=5 | 0 | 12 |  | 70.73 |  |  |  |  |  |  |  |  |  |
| mms-1b-all | 6-15 | 3 | 100 | 63.33 | 52.36 | 10.97 |  |  |  |  |  |  |  |  |
| mms-1b-all | >15 | 61 | 295 | 40.51 | 43.78 | -3.27 |  |  |  |  |  |  |  |  |
| mms-1b-all | standardised | 61 | 295 | 40.51 | 43.78 | -3.27 | -6.52 | -0.16 | False | 0.042 | 0.6294 | False | 1000 | >15 |
| mms-1b-ur | <=5 | 0 | 12 |  | 58.54 |  |  |  |  |  |  |  |  |  |
| mms-1b-ur | 6-15 | 3 | 100 | 56.67 | 43.38 | 13.28 |  |  |  |  |  |  |  |  |
| mms-1b-ur | >15 | 61 | 295 | 38.62 | 42.8 | -4.18 |  |  |  |  |  |  |  |  |
| mms-1b-ur | standardised | 61 | 295 | 38.62 | 42.8 | -4.18 | -8.02 | 0.31 | True | 0.0639 | 0.8392 | False | 1000 | >15 |
| mms-300m-ur | <=5 | 0 | 12 |  | 73.17 |  |  |  |  |  |  |  |  |  |
| mms-300m-ur | 6-15 | 3 | 100 | 80.0 | 67.39 | 12.61 |  |  |  |  |  |  |  |  |
| mms-300m-ur | >15 | 61 | 295 | 70.97 | 67.43 | 3.54 |  |  |  |  |  |  |  |  |
| mms-300m-ur | standardised | 61 | 295 | 70.97 | 67.43 | 3.54 | -1.43 | 7.9 | True | 0.1199 | 1.0 | False | 1000 | >15 |
| seamless-m4t-medium-ur | <=5 | 0 | 12 |  | 48.78 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 6-15 | 3 | 100 | 23.33 | 24.57 | -1.24 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | >15 | 61 | 295 | 15.2 | 18.13 | -2.94 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | standardised | 61 | 295 | 15.2 | 18.13 | -2.94 | -6.26 | 0.64 | True | 0.1119 | 1.0 | False | 1000 | >15 |
| seamless-m4t-v2-large | <=5 | 0 | 12 |  | 43.9 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 6-15 | 3 | 100 | 23.33 | 24.1 | -0.77 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | >15 | 61 | 295 | 32.08 | 34.05 | -1.97 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | standardised | 61 | 295 | 32.08 | 34.05 | -1.97 | -8.62 | 3.74 | True | 0.5514 | 1.0 | False | 1000 | >15 |
| seamless-m4t-v2-large-ur | <=5 | 0 | 12 |  | 39.02 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 6-15 | 3 | 100 | 23.33 | 20.32 | 3.01 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | >15 | 61 | 295 | 14.7 | 19.25 | -4.55 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | standardised | 61 | 295 | 14.7 | 19.25 | -4.55 | -7.48 | -1.59 | False | 0.006 | 0.1019 | False | 1000 | >15 |
| whisper-base | <=5 | 0 | 12 |  | 85.37 |  |  |  |  |  |  |  |  |  |
| whisper-base | 6-15 | 3 | 100 | 773.33 | 241.21 | 532.12 |  |  |  |  |  |  |  |  |
| whisper-base | >15 | 61 | 295 | 107.9 | 126.97 | -19.07 |  |  |  |  |  |  |  |  |
| whisper-base | standardised | 61 | 295 | 107.9 | 126.97 | -19.07 | -53.54 | 18.9 | True | 0.2717 | 1.0 | False | 1000 | >15 |
| whisper-base-ur | <=5 | 0 | 12 |  | 51.22 |  |  |  |  |  |  |  |  |  |
| whisper-base-ur | 6-15 | 3 | 100 | 63.33 | 49.34 | 13.99 |  |  |  |  |  |  |  |  |
| whisper-base-ur | >15 | 61 | 295 | 43.56 | 51.52 | -7.96 |  |  |  |  |  |  |  |  |
| whisper-base-ur | standardised | 61 | 295 | 43.56 | 51.52 | -7.96 | -15.06 | -0.96 | False | 0.034 | 0.5435 | False | 1000 | >15 |
| whisper-large-v3 | <=5 | 0 | 12 |  | 29.27 |  |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 6-15 | 3 | 100 | 23.33 | 24.39 | -1.05 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | >15 | 61 | 295 | 13.5 | 16.1 | -2.6 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | standardised | 61 | 295 | 13.5 | 16.1 | -2.6 | -5.04 | 0.09 | True | 0.0599 | 0.8392 | False | 1000 | >15 |
| whisper-large-v3-ur | <=5 | 0 | 12 |  | 17.07 |  |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 6-15 | 3 | 100 | 23.33 | 20.79 | 2.54 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | >15 | 61 | 295 | 13.9 | 16.43 | -2.53 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | standardised | 61 | 295 | 13.9 | 16.43 | -2.53 | -5.29 | 0.38 | True | 0.0899 | 1.0 | False | 1000 | >15 |
| whisper-medium | <=5 | 0 | 12 |  | 31.71 |  |  |  |  |  |  |  |  |  |
| whisper-medium | 6-15 | 3 | 100 | 40.0 | 38.75 | 1.25 |  |  |  |  |  |  |  |  |
| whisper-medium | >15 | 61 | 295 | 34.01 | 45.34 | -11.33 |  |  |  |  |  |  |  |  |
| whisper-medium | standardised | 61 | 295 | 34.01 | 45.34 | -11.33 | -26.24 | 6.22 | True | 0.1978 | 1.0 | False | 1000 | >15 |
| whisper-medium-ur | <=5 | 0 | 12 |  | 39.02 |  |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 6-15 | 3 | 100 | 40.0 | 32.33 | 7.67 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | >15 | 61 | 295 | 24.35 | 27.37 | -3.02 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | standardised | 61 | 295 | 24.35 | 27.37 | -3.02 | -6.54 | 0.76 | True | 0.1199 | 1.0 | False | 1000 | >15 |
| whisper-small | <=5 | 0 | 12 |  | 51.22 |  |  |  |  |  |  |  |  |  |
| whisper-small | 6-15 | 3 | 100 | 50.0 | 75.52 | -25.52 |  |  |  |  |  |  |  |  |
| whisper-small | >15 | 61 | 295 | 46.35 | 44.24 | 2.11 |  |  |  |  |  |  |  |  |
| whisper-small | standardised | 61 | 295 | 46.35 | 44.24 | 2.11 | -11.27 | 21.66 | True | 0.8631 | 1.0 | False | 1000 | >15 |
| whisper-small-ur | <=5 | 0 | 12 |  | 46.34 |  |  |  |  |  |  |  |  |  |
| whisper-small-ur | 6-15 | 3 | 100 | 36.67 | 37.05 | -0.38 |  |  |  |  |  |  |  |  |
| whisper-small-ur | >15 | 61 | 295 | 28.8 | 31.34 | -2.54 |  |  |  |  |  |  |  |  |
| whisper-small-ur | standardised | 61 | 295 | 28.8 | 31.34 | -2.54 | -6.28 | 1.58 | True | 0.2278 | 1.0 | False | 1000 | >15 |
| whisper-tiny | <=5 | 0 | 12 |  | 90.24 |  |  |  |  |  |  |  |  |  |
| whisper-tiny | 6-15 | 3 | 100 | 83.33 | 208.88 | -125.55 |  |  |  |  |  |  |  |  |
| whisper-tiny | >15 | 61 | 295 | 130.06 | 153.45 | -23.39 |  |  |  |  |  |  |  |  |
| whisper-tiny | standardised | 61 | 295 | 130.06 | 153.45 | -23.39 | -58.72 | 13.27 | True | 0.1978 | 1.0 | False | 1000 | >15 |
| whisper-tiny-ur | <=5 | 0 | 12 |  | 75.61 |  |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 6-15 | 3 | 100 | 63.33 | 62.29 | 1.05 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | >15 | 61 | 295 | 65.43 | 58.96 | 6.47 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | standardised | 61 | 295 | 65.43 | 58.96 | 6.47 | -8.92 | 30.81 | True | 0.6753 | 1.0 | False | 1000 | >15 |

## as_released~ — corpus_cer — buckets: spec

| model | bucket | n_flagged | n_unflagged | flagged | unflagged | delta | ci_low | ci_high | ci_includes_0 | p_boot | p_holm | reject_holm_05 | n_valid_resamples | buckets_used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hf-seamless-m4t-medium | <=5 | 0 | 12 |  | 41.18 |  |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 6-15 | 3 | 100 | 15.71 | 20.16 | -4.44 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | >15 | 61 | 295 | 8.95 | 10.56 | -1.61 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | standardised | 61 | 295 | 8.95 | 10.56 | -1.61 | -4.85 | 2.24 | True | 0.3536 | 1.0 | False | 1000 | >15 |
| mms-1b-all | <=5 | 0 | 12 |  | 38.24 |  |  |  |  |  |  |  |  |  |
| mms-1b-all | 6-15 | 3 | 100 | 30.71 | 24.89 | 5.82 |  |  |  |  |  |  |  |  |
| mms-1b-all | >15 | 61 | 295 | 17.17 | 19.49 | -2.32 |  |  |  |  |  |  |  |  |
| mms-1b-all | standardised | 61 | 295 | 17.17 | 19.49 | -2.32 | -4.24 | -0.21 | False | 0.036 | 0.5035 | False | 1000 | >15 |
| mms-1b-ur | <=5 | 0 | 12 |  | 34.71 |  |  |  |  |  |  |  |  |  |
| mms-1b-ur | 6-15 | 3 | 100 | 22.86 | 22.18 | 0.68 |  |  |  |  |  |  |  |  |
| mms-1b-ur | >15 | 61 | 295 | 17.06 | 21.93 | -4.87 |  |  |  |  |  |  |  |  |
| mms-1b-ur | standardised | 61 | 295 | 17.06 | 21.93 | -4.87 | -7.52 | -1.93 | False | 0.004 | 0.0679 | False | 1000 | >15 |
| mms-300m-ur | <=5 | 0 | 12 |  | 38.82 |  |  |  |  |  |  |  |  |  |
| mms-300m-ur | 6-15 | 3 | 100 | 37.14 | 29.34 | 7.81 |  |  |  |  |  |  |  |  |
| mms-300m-ur | >15 | 61 | 295 | 29.1 | 28.06 | 1.04 |  |  |  |  |  |  |  |  |
| mms-300m-ur | standardised | 61 | 295 | 29.1 | 28.06 | 1.04 | -1.49 | 3.3 | True | 0.4056 | 1.0 | False | 1000 | >15 |
| seamless-m4t-medium-ur | <=5 | 0 | 12 |  | 31.76 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 6-15 | 3 | 100 | 15.71 | 13.38 | 2.34 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | >15 | 61 | 295 | 8.88 | 10.73 | -1.85 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | standardised | 61 | 295 | 8.88 | 10.73 | -1.85 | -4.91 | 1.82 | True | 0.2557 | 1.0 | False | 1000 | >15 |
| seamless-m4t-v2-large | <=5 | 0 | 12 |  | 28.82 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 6-15 | 3 | 100 | 10.71 | 14.41 | -3.7 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | >15 | 61 | 295 | 22.67 | 23.7 | -1.03 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | standardised | 61 | 295 | 22.67 | 23.7 | -1.03 | -5.91 | 3.26 | True | 0.7073 | 1.0 | False | 1000 | >15 |
| seamless-m4t-v2-large-ur | <=5 | 0 | 12 |  | 23.53 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 6-15 | 3 | 100 | 16.43 | 10.77 | 5.65 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | >15 | 61 | 295 | 8.63 | 12.13 | -3.51 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | standardised | 61 | 295 | 8.63 | 12.13 | -3.51 | -5.89 | -0.96 | False | 0.004 | 0.0679 | False | 1000 | >15 |
| whisper-base | <=5 | 0 | 12 |  | 48.82 |  |  |  |  |  |  |  |  |  |
| whisper-base | 6-15 | 3 | 100 | 479.29 | 169.94 | 309.34 |  |  |  |  |  |  |  |  |
| whisper-base | >15 | 61 | 295 | 81.16 | 93.15 | -11.99 |  |  |  |  |  |  |  |  |
| whisper-base | standardised | 61 | 295 | 81.16 | 93.15 | -11.99 | -44.17 | 22.67 | True | 0.4535 | 1.0 | False | 1000 | >15 |
| whisper-base-ur | <=5 | 0 | 12 |  | 28.82 |  |  |  |  |  |  |  |  |  |
| whisper-base-ur | 6-15 | 3 | 100 | 30.0 | 26.06 | 3.94 |  |  |  |  |  |  |  |  |
| whisper-base-ur | >15 | 61 | 295 | 28.31 | 33.2 | -4.89 |  |  |  |  |  |  |  |  |
| whisper-base-ur | standardised | 61 | 295 | 28.31 | 33.2 | -4.89 | -16.01 | 10.64 | True | 0.4655 | 1.0 | False | 1000 | >15 |
| whisper-large-v3 | <=5 | 0 | 12 |  | 18.82 |  |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 6-15 | 3 | 100 | 16.43 | 13.4 | 3.03 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | >15 | 61 | 295 | 7.06 | 9.39 | -2.33 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | standardised | 61 | 295 | 7.06 | 9.39 | -2.33 | -4.39 | -0.19 | False | 0.038 | 0.5035 | False | 1000 | >15 |
| whisper-large-v3-ur | <=5 | 0 | 12 |  | 11.76 |  |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 6-15 | 3 | 100 | 10.71 | 11.0 | -0.28 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | >15 | 61 | 295 | 6.52 | 9.4 | -2.88 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | standardised | 61 | 295 | 6.52 | 9.4 | -2.88 | -4.98 | -0.79 | False | 0.006 | 0.0899 | False | 1000 | >15 |
| whisper-medium | <=5 | 0 | 12 |  | 21.76 |  |  |  |  |  |  |  |  |  |
| whisper-medium | 6-15 | 3 | 100 | 29.29 | 23.88 | 5.4 |  |  |  |  |  |  |  |  |
| whisper-medium | >15 | 61 | 295 | 21.46 | 33.33 | -11.87 |  |  |  |  |  |  |  |  |
| whisper-medium | standardised | 61 | 295 | 21.46 | 33.33 | -11.87 | -24.2 | 1.35 | True | 0.0779 | 0.8571 | False | 1000 | >15 |
| whisper-medium-ur | <=5 | 0 | 12 |  | 20.59 |  |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 6-15 | 3 | 100 | 12.14 | 17.53 | -5.39 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | >15 | 61 | 295 | 11.96 | 15.26 | -3.3 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | standardised | 61 | 295 | 11.96 | 15.26 | -3.3 | -6.1 | -0.24 | False | 0.04 | 0.5035 | False | 1000 | >15 |
| whisper-small | <=5 | 0 | 12 |  | 30.0 |  |  |  |  |  |  |  |  |  |
| whisper-small | 6-15 | 3 | 100 | 20.71 | 61.44 | -40.72 |  |  |  |  |  |  |  |  |
| whisper-small | >15 | 61 | 295 | 28.25 | 28.24 | 0.01 |  |  |  |  |  |  |  |  |
| whisper-small | standardised | 61 | 295 | 28.25 | 28.24 | 0.01 | -12.81 | 17.55 | True | 0.9211 | 1.0 | False | 1000 | >15 |
| whisper-small-ur | <=5 | 0 | 12 |  | 23.53 |  |  |  |  |  |  |  |  |  |
| whisper-small-ur | 6-15 | 3 | 100 | 20.0 | 18.99 | 1.01 |  |  |  |  |  |  |  |  |
| whisper-small-ur | >15 | 61 | 295 | 14.82 | 17.18 | -2.36 |  |  |  |  |  |  |  |  |
| whisper-small-ur | standardised | 61 | 295 | 14.82 | 17.18 | -2.36 | -5.6 | 1.53 | True | 0.1618 | 1.0 | False | 1000 | >15 |
| whisper-tiny | <=5 | 0 | 12 |  | 317.65 |  |  |  |  |  |  |  |  |  |
| whisper-tiny | 6-15 | 3 | 100 | 45.0 | 157.85 | -112.85 |  |  |  |  |  |  |  |  |
| whisper-tiny | >15 | 61 | 295 | 94.38 | 116.49 | -22.11 |  |  |  |  |  |  |  |  |
| whisper-tiny | standardised | 61 | 295 | 94.38 | 116.49 | -22.11 | -52.93 | 10.45 | True | 0.1778 | 1.0 | False | 1000 | >15 |
| whisper-tiny-ur | <=5 | 0 | 12 |  | 43.53 |  |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 6-15 | 3 | 100 | 35.0 | 59.51 | -24.51 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | >15 | 61 | 295 | 34.69 | 34.24 | 0.45 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | standardised | 61 | 295 | 34.69 | 34.24 | 0.45 | -9.45 | 13.55 | True | 0.969 | 1.0 | False | 1000 | >15 |

## N7_numwords — corpus_wer — buckets: spec

| model | bucket | n_flagged | n_unflagged | flagged | unflagged | delta | ci_low | ci_high | ci_includes_0 | p_boot | p_holm | reject_holm_05 | n_valid_resamples | buckets_used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hf-seamless-m4t-medium | <=5 | 0 | 12 |  | 60.98 |  |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 6-15 | 3 | 100 | 20.0 | 33.84 | -13.84 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | >15 | 61 | 295 | 15.1 | 17.69 | -2.59 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | standardised | 61 | 295 | 15.1 | 17.69 | -2.59 | -6.12 | 1.46 | True | 0.1858 | 1.0 | False | 1000 | >15 |
| mms-1b-all | <=5 | 0 | 12 |  | 70.73 |  |  |  |  |  |  |  |  |  |
| mms-1b-all | 6-15 | 3 | 100 | 63.33 | 52.36 | 10.97 |  |  |  |  |  |  |  |  |
| mms-1b-all | >15 | 61 | 295 | 40.51 | 43.76 | -3.25 |  |  |  |  |  |  |  |  |
| mms-1b-all | standardised | 61 | 295 | 40.51 | 43.76 | -3.25 | -6.48 | -0.07 | False | 0.044 | 0.6593 | False | 1000 | >15 |
| mms-1b-ur | <=5 | 0 | 12 |  | 58.54 |  |  |  |  |  |  |  |  |  |
| mms-1b-ur | 6-15 | 3 | 100 | 56.67 | 43.48 | 13.19 |  |  |  |  |  |  |  |  |
| mms-1b-ur | >15 | 61 | 295 | 38.55 | 42.8 | -4.24 |  |  |  |  |  |  |  |  |
| mms-1b-ur | standardised | 61 | 295 | 38.55 | 42.8 | -4.24 | -8.06 | 0.2 | True | 0.0639 | 0.8951 | False | 1000 | >15 |
| mms-300m-ur | <=5 | 0 | 12 |  | 73.17 |  |  |  |  |  |  |  |  |  |
| mms-300m-ur | 6-15 | 3 | 100 | 80.0 | 67.39 | 12.61 |  |  |  |  |  |  |  |  |
| mms-300m-ur | >15 | 61 | 295 | 70.97 | 67.43 | 3.54 |  |  |  |  |  |  |  |  |
| mms-300m-ur | standardised | 61 | 295 | 70.97 | 67.43 | 3.54 | -1.43 | 7.9 | True | 0.1199 | 1.0 | False | 1000 | >15 |
| seamless-m4t-medium-ur | <=5 | 0 | 12 |  | 48.78 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 6-15 | 3 | 100 | 26.67 | 24.57 | 2.09 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | >15 | 61 | 295 | 15.03 | 18.13 | -3.1 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | standardised | 61 | 295 | 15.03 | 18.13 | -3.1 | -6.48 | 0.5 | True | 0.0859 | 1.0 | False | 1000 | >15 |
| seamless-m4t-v2-large | <=5 | 0 | 12 |  | 43.9 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 6-15 | 3 | 100 | 23.33 | 24.01 | -0.67 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | >15 | 61 | 295 | 32.12 | 34.07 | -1.95 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | standardised | 61 | 295 | 32.12 | 34.07 | -1.95 | -8.66 | 3.76 | True | 0.5534 | 1.0 | False | 1000 | >15 |
| seamless-m4t-v2-large-ur | <=5 | 0 | 12 |  | 39.02 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 6-15 | 3 | 100 | 23.33 | 20.23 | 3.11 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | >15 | 61 | 295 | 14.43 | 19.22 | -4.79 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | standardised | 61 | 295 | 14.43 | 19.22 | -4.79 | -7.67 | -1.8 | False | 0.002 | 0.034 | True | 1000 | >15 |
| whisper-base | <=5 | 0 | 12 |  | 85.37 |  |  |  |  |  |  |  |  |  |
| whisper-base | 6-15 | 3 | 100 | 773.33 | 241.21 | 532.12 |  |  |  |  |  |  |  |  |
| whisper-base | >15 | 61 | 295 | 107.93 | 126.9 | -18.97 |  |  |  |  |  |  |  |  |
| whisper-base | standardised | 61 | 295 | 107.93 | 126.9 | -18.97 | -53.4 | 19.03 | True | 0.2737 | 1.0 | False | 1000 | >15 |
| whisper-base-ur | <=5 | 0 | 12 |  | 51.22 |  |  |  |  |  |  |  |  |  |
| whisper-base-ur | 6-15 | 3 | 100 | 63.33 | 49.34 | 13.99 |  |  |  |  |  |  |  |  |
| whisper-base-ur | >15 | 61 | 295 | 43.5 | 51.41 | -7.92 |  |  |  |  |  |  |  |  |
| whisper-base-ur | standardised | 61 | 295 | 43.5 | 51.41 | -7.92 | -15.09 | -0.87 | False | 0.036 | 0.5754 | False | 1000 | >15 |
| whisper-large-v3 | <=5 | 0 | 12 |  | 29.27 |  |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 6-15 | 3 | 100 | 26.67 | 24.48 | 2.19 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | >15 | 61 | 295 | 13.6 | 16.17 | -2.57 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | standardised | 61 | 295 | 13.6 | 16.17 | -2.57 | -5.04 | 0.11 | True | 0.0659 | 0.8951 | False | 1000 | >15 |
| whisper-large-v3-ur | <=5 | 0 | 12 |  | 17.07 |  |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 6-15 | 3 | 100 | 30.0 | 20.51 | 9.49 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | >15 | 61 | 295 | 13.8 | 16.47 | -2.66 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | standardised | 61 | 295 | 13.8 | 16.47 | -2.66 | -5.46 | 0.27 | True | 0.0859 | 1.0 | False | 1000 | >15 |
| whisper-medium | <=5 | 0 | 12 |  | 31.71 |  |  |  |  |  |  |  |  |  |
| whisper-medium | 6-15 | 3 | 100 | 40.0 | 38.75 | 1.25 |  |  |  |  |  |  |  |  |
| whisper-medium | >15 | 61 | 295 | 34.11 | 45.27 | -11.16 |  |  |  |  |  |  |  |  |
| whisper-medium | standardised | 61 | 295 | 34.11 | 45.27 | -11.16 | -26.2 | 6.48 | True | 0.2058 | 1.0 | False | 1000 | >15 |
| whisper-medium-ur | <=5 | 0 | 12 |  | 39.02 |  |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 6-15 | 3 | 100 | 40.0 | 32.42 | 7.58 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | >15 | 61 | 295 | 24.42 | 27.33 | -2.91 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | standardised | 61 | 295 | 24.42 | 27.33 | -2.91 | -6.43 | 0.88 | True | 0.1339 | 1.0 | False | 1000 | >15 |
| whisper-small | <=5 | 0 | 12 |  | 51.22 |  |  |  |  |  |  |  |  |  |
| whisper-small | 6-15 | 3 | 100 | 50.0 | 75.52 | -25.52 |  |  |  |  |  |  |  |  |
| whisper-small | >15 | 61 | 295 | 46.12 | 44.19 | 1.93 |  |  |  |  |  |  |  |  |
| whisper-small | standardised | 61 | 295 | 46.12 | 44.19 | 1.93 | -11.51 | 21.64 | True | 0.8851 | 1.0 | False | 1000 | >15 |
| whisper-small-ur | <=5 | 0 | 12 |  | 46.34 |  |  |  |  |  |  |  |  |  |
| whisper-small-ur | 6-15 | 3 | 100 | 40.0 | 36.86 | 3.14 |  |  |  |  |  |  |  |  |
| whisper-small-ur | >15 | 61 | 295 | 28.8 | 31.34 | -2.54 |  |  |  |  |  |  |  |  |
| whisper-small-ur | standardised | 61 | 295 | 28.8 | 31.34 | -2.54 | -6.29 | 1.57 | True | 0.2298 | 1.0 | False | 1000 | >15 |
| whisper-tiny | <=5 | 0 | 12 |  | 87.8 |  |  |  |  |  |  |  |  |  |
| whisper-tiny | 6-15 | 3 | 100 | 83.33 | 208.79 | -125.46 |  |  |  |  |  |  |  |  |
| whisper-tiny | >15 | 61 | 295 | 130.06 | 153.45 | -23.39 |  |  |  |  |  |  |  |  |
| whisper-tiny | standardised | 61 | 295 | 130.06 | 153.45 | -23.39 | -58.72 | 13.27 | True | 0.1978 | 1.0 | False | 1000 | >15 |
| whisper-tiny-ur | <=5 | 0 | 12 |  | 75.61 |  |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 6-15 | 3 | 100 | 63.33 | 62.29 | 1.05 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | >15 | 61 | 295 | 65.43 | 58.93 | 6.49 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | standardised | 61 | 295 | 65.43 | 58.93 | 6.49 | -8.89 | 30.86 | True | 0.6753 | 1.0 | False | 1000 | >15 |

## N7_numwords — corpus_cer — buckets: spec

| model | bucket | n_flagged | n_unflagged | flagged | unflagged | delta | ci_low | ci_high | ci_includes_0 | p_boot | p_holm | reject_holm_05 | n_valid_resamples | buckets_used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hf-seamless-m4t-medium | <=5 | 0 | 12 |  | 44.71 |  |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 6-15 | 3 | 100 | 15.71 | 20.13 | -4.42 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | >15 | 61 | 295 | 8.95 | 10.55 | -1.61 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | standardised | 61 | 295 | 8.95 | 10.55 | -1.61 | -4.86 | 2.27 | True | 0.3556 | 1.0 | False | 1000 | >15 |
| mms-1b-all | <=5 | 0 | 12 |  | 38.24 |  |  |  |  |  |  |  |  |  |
| mms-1b-all | 6-15 | 3 | 100 | 30.71 | 24.89 | 5.82 |  |  |  |  |  |  |  |  |
| mms-1b-all | >15 | 61 | 295 | 17.06 | 19.42 | -2.35 |  |  |  |  |  |  |  |  |
| mms-1b-all | standardised | 61 | 295 | 17.06 | 19.42 | -2.35 | -4.28 | -0.27 | False | 0.03 | 0.4196 | False | 1000 | >15 |
| mms-1b-ur | <=5 | 0 | 12 |  | 34.71 |  |  |  |  |  |  |  |  |  |
| mms-1b-ur | 6-15 | 3 | 100 | 22.86 | 22.27 | 0.59 |  |  |  |  |  |  |  |  |
| mms-1b-ur | >15 | 61 | 295 | 16.95 | 21.9 | -4.95 |  |  |  |  |  |  |  |  |
| mms-1b-ur | standardised | 61 | 295 | 16.95 | 21.9 | -4.95 | -7.59 | -1.97 | False | 0.004 | 0.0679 | False | 1000 | >15 |
| mms-300m-ur | <=5 | 0 | 12 |  | 38.82 |  |  |  |  |  |  |  |  |  |
| mms-300m-ur | 6-15 | 3 | 100 | 37.14 | 29.34 | 7.81 |  |  |  |  |  |  |  |  |
| mms-300m-ur | >15 | 61 | 295 | 29.08 | 28.05 | 1.03 |  |  |  |  |  |  |  |  |
| mms-300m-ur | standardised | 61 | 295 | 29.08 | 28.05 | 1.03 | -1.49 | 3.29 | True | 0.4076 | 1.0 | False | 1000 | >15 |
| seamless-m4t-medium-ur | <=5 | 0 | 12 |  | 31.76 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 6-15 | 3 | 100 | 16.43 | 13.38 | 3.05 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | >15 | 61 | 295 | 8.67 | 10.67 | -1.99 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | standardised | 61 | 295 | 8.67 | 10.67 | -1.99 | -5.11 | 1.59 | True | 0.2378 | 1.0 | False | 1000 | >15 |
| seamless-m4t-v2-large | <=5 | 0 | 12 |  | 28.82 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 6-15 | 3 | 100 | 12.14 | 14.46 | -2.31 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | >15 | 61 | 295 | 22.66 | 23.7 | -1.04 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | standardised | 61 | 295 | 22.66 | 23.7 | -1.04 | -5.93 | 3.28 | True | 0.7033 | 1.0 | False | 1000 | >15 |
| seamless-m4t-v2-large-ur | <=5 | 0 | 12 |  | 23.53 |  |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 6-15 | 3 | 100 | 16.43 | 10.68 | 5.74 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | >15 | 61 | 295 | 8.42 | 12.07 | -3.66 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | standardised | 61 | 295 | 8.42 | 12.07 | -3.66 | -6.01 | -1.14 | False | 0.004 | 0.0679 | False | 1000 | >15 |
| whisper-base | <=5 | 0 | 12 |  | 48.82 |  |  |  |  |  |  |  |  |  |
| whisper-base | 6-15 | 3 | 100 | 479.29 | 169.9 | 309.39 |  |  |  |  |  |  |  |  |
| whisper-base | >15 | 61 | 295 | 81.15 | 93.09 | -11.93 |  |  |  |  |  |  |  |  |
| whisper-base | standardised | 61 | 295 | 81.15 | 93.09 | -11.93 | -44.12 | 22.74 | True | 0.4575 | 1.0 | False | 1000 | >15 |
| whisper-base-ur | <=5 | 0 | 12 |  | 28.82 |  |  |  |  |  |  |  |  |  |
| whisper-base-ur | 6-15 | 3 | 100 | 30.0 | 26.11 | 3.89 |  |  |  |  |  |  |  |  |
| whisper-base-ur | >15 | 61 | 295 | 28.28 | 33.17 | -4.89 |  |  |  |  |  |  |  |  |
| whisper-base-ur | standardised | 61 | 295 | 28.28 | 33.17 | -4.89 | -16.06 | 10.65 | True | 0.4675 | 1.0 | False | 1000 | >15 |
| whisper-large-v3 | <=5 | 0 | 12 |  | 18.82 |  |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 6-15 | 3 | 100 | 16.43 | 13.49 | 2.94 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | >15 | 61 | 295 | 7.06 | 9.38 | -2.32 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | standardised | 61 | 295 | 7.06 | 9.38 | -2.32 | -4.34 | -0.17 | False | 0.04 | 0.5195 | False | 1000 | >15 |
| whisper-large-v3-ur | <=5 | 0 | 12 |  | 11.76 |  |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 6-15 | 3 | 100 | 12.14 | 10.95 | 1.19 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | >15 | 61 | 295 | 6.35 | 9.38 | -3.03 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | standardised | 61 | 295 | 6.35 | 9.38 | -3.03 | -5.04 | -1.01 | False | 0.004 | 0.0679 | False | 1000 | >15 |
| whisper-medium | <=5 | 0 | 12 |  | 21.76 |  |  |  |  |  |  |  |  |  |
| whisper-medium | 6-15 | 3 | 100 | 29.29 | 23.88 | 5.4 |  |  |  |  |  |  |  |  |
| whisper-medium | >15 | 61 | 295 | 21.48 | 33.24 | -11.76 |  |  |  |  |  |  |  |  |
| whisper-medium | standardised | 61 | 295 | 21.48 | 33.24 | -11.76 | -24.09 | 1.54 | True | 0.0839 | 0.9231 | False | 1000 | >15 |
| whisper-medium-ur | <=5 | 0 | 12 |  | 20.59 |  |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 6-15 | 3 | 100 | 13.57 | 17.53 | -3.96 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | >15 | 61 | 295 | 11.97 | 15.25 | -3.28 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | standardised | 61 | 295 | 11.97 | 15.25 | -3.28 | -6.07 | -0.21 | False | 0.04 | 0.5195 | False | 1000 | >15 |
| whisper-small | <=5 | 0 | 12 |  | 30.0 |  |  |  |  |  |  |  |  |  |
| whisper-small | 6-15 | 3 | 100 | 20.71 | 61.41 | -40.7 |  |  |  |  |  |  |  |  |
| whisper-small | >15 | 61 | 295 | 28.03 | 28.18 | -0.15 |  |  |  |  |  |  |  |  |
| whisper-small | standardised | 61 | 295 | 28.03 | 28.18 | -0.15 | -13.06 | 17.61 | True | 0.9071 | 1.0 | False | 1000 | >15 |
| whisper-small-ur | <=5 | 0 | 12 |  | 23.53 |  |  |  |  |  |  |  |  |  |
| whisper-small-ur | 6-15 | 3 | 100 | 20.71 | 18.97 | 1.75 |  |  |  |  |  |  |  |  |
| whisper-small-ur | >15 | 61 | 295 | 14.75 | 17.14 | -2.38 |  |  |  |  |  |  |  |  |
| whisper-small-ur | standardised | 61 | 295 | 14.75 | 17.14 | -2.38 | -5.61 | 1.46 | True | 0.1538 | 1.0 | False | 1000 | >15 |
| whisper-tiny | <=5 | 0 | 12 |  | 316.47 |  |  |  |  |  |  |  |  |  |
| whisper-tiny | 6-15 | 3 | 100 | 45.0 | 157.8 | -112.8 |  |  |  |  |  |  |  |  |
| whisper-tiny | >15 | 61 | 295 | 94.38 | 116.49 | -22.11 |  |  |  |  |  |  |  |  |
| whisper-tiny | standardised | 61 | 295 | 94.38 | 116.49 | -22.11 | -52.92 | 10.47 | True | 0.1778 | 1.0 | False | 1000 | >15 |
| whisper-tiny-ur | <=5 | 0 | 12 |  | 43.53 |  |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 6-15 | 3 | 100 | 35.0 | 59.46 | -24.46 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | >15 | 61 | 295 | 34.68 | 34.2 | 0.47 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | standardised | 61 | 295 | 34.68 | 34.2 | 0.47 | -9.45 | 13.61 | True | 0.971 | 1.0 | False | 1000 | >15 |

## as_released~ — corpus_wer — buckets: fine

| model | bucket | n_flagged | n_unflagged | flagged | unflagged | delta | ci_low | ci_high | ci_includes_0 | p_boot | p_holm | reject_holm_05 | n_valid_resamples | buckets_used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hf-seamless-m4t-medium | <=15 | 3 | 112 | 20.0 | 35.03 | -15.03 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 16-30 | 17 | 132 | 13.82 | 16.84 | -3.02 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 31-50 | 18 | 97 | 14.01 | 16.97 | -2.96 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | >50 | 26 | 66 | 15.74 | 18.79 | -3.05 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | standardised | 61 | 295 | 14.73 | 17.75 | -3.01 | -6.6 | 0.83 | True | 0.1319 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-1b-all | <=15 | 3 | 112 | 63.33 | 53.05 | 10.29 |  |  |  |  |  |  |  |  |
| mms-1b-all | 16-30 | 17 | 132 | 41.96 | 43.7 | -1.74 |  |  |  |  |  |  |  |  |
| mms-1b-all | 31-50 | 18 | 97 | 41.9 | 43.11 | -1.2 |  |  |  |  |  |  |  |  |
| mms-1b-all | >50 | 26 | 66 | 39.66 | 44.4 | -4.74 |  |  |  |  |  |  |  |  |
| mms-1b-all | standardised | 61 | 295 | 40.92 | 43.82 | -2.9 | -6.77 | 0.89 | True | 0.1578 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-1b-ur | <=15 | 3 | 112 | 56.67 | 43.95 | 12.72 |  |  |  |  |  |  |  |  |
| mms-1b-ur | 16-30 | 17 | 132 | 37.94 | 40.94 | -3.0 |  |  |  |  |  |  |  |  |
| mms-1b-ur | 31-50 | 18 | 97 | 39.05 | 40.66 | -1.62 |  |  |  |  |  |  |  |  |
| mms-1b-ur | >50 | 26 | 66 | 38.6 | 45.86 | -7.26 |  |  |  |  |  |  |  |  |
| mms-1b-ur | standardised | 61 | 295 | 38.58 | 43.04 | -4.46 | -8.92 | 0.76 | True | 0.0979 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-300m-ur | <=15 | 3 | 112 | 80.0 | 67.61 | 12.39 |  |  |  |  |  |  |  |  |
| mms-300m-ur | 16-30 | 17 | 132 | 58.04 | 61.39 | -3.35 |  |  |  |  |  |  |  |  |
| mms-300m-ur | 31-50 | 18 | 97 | 66.39 | 64.7 | 1.69 |  |  |  |  |  |  |  |  |
| mms-300m-ur | >50 | 26 | 66 | 75.49 | 73.85 | 1.64 |  |  |  |  |  |  |  |  |
| mms-300m-ur | standardised | 61 | 295 | 68.42 | 67.97 | 0.46 | -4.1 | 4.66 | True | 0.8551 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-medium-ur | <=15 | 3 | 112 | 23.33 | 25.48 | -2.14 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 16-30 | 17 | 132 | 14.07 | 15.69 | -1.62 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 31-50 | 18 | 97 | 13.2 | 18.27 | -5.08 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | >50 | 26 | 66 | 16.21 | 19.68 | -3.47 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | standardised | 61 | 295 | 14.75 | 18.28 | -3.53 | -7.09 | 0.19 | True | 0.0699 | 0.979 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-v2-large | <=15 | 3 | 112 | 23.33 | 24.84 | -1.51 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 16-30 | 17 | 132 | 20.6 | 29.12 | -8.52 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 31-50 | 18 | 97 | 23.4 | 28.07 | -4.67 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | >50 | 26 | 66 | 37.91 | 42.45 | -4.55 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | standardised | 61 | 295 | 29.17 | 34.71 | -5.54 | -11.38 | -0.43 | False | 0.042 | 0.6294 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-v2-large-ur | <=15 | 3 | 112 | 23.33 | 21.02 | 2.31 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 16-30 | 17 | 132 | 13.82 | 14.18 | -0.36 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 31-50 | 18 | 97 | 15.51 | 18.22 | -2.71 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | >50 | 26 | 66 | 14.57 | 23.58 | -9.01 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | standardised | 61 | 295 | 14.68 | 19.63 | -4.94 | -8.02 | -1.7 | False | 0.006 | 0.1019 | False | 1000 | 16-30+31-50+>50 |
| whisper-base | <=15 | 3 | 112 | 773.33 | 235.4 | 537.94 |  |  |  |  |  |  |  |  |
| whisper-base | 16-30 | 17 | 132 | 143.72 | 152.76 | -9.04 |  |  |  |  |  |  |  |  |
| whisper-base | 31-50 | 18 | 97 | 130.88 | 129.91 | 0.98 |  |  |  |  |  |  |  |  |
| whisper-base | >50 | 26 | 66 | 91.33 | 106.9 | -15.56 |  |  |  |  |  |  |  |  |
| whisper-base | standardised | 61 | 295 | 116.41 | 125.19 | -8.78 | -48.64 | 32.12 | True | 0.6394 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-base-ur | <=15 | 3 | 112 | 63.33 | 49.41 | 13.92 |  |  |  |  |  |  |  |  |
| whisper-base-ur | 16-30 | 17 | 132 | 42.96 | 41.2 | 1.76 |  |  |  |  |  |  |  |  |
| whisper-base-ur | 31-50 | 18 | 97 | 41.5 | 54.61 | -13.11 |  |  |  |  |  |  |  |  |
| whisper-base-ur | >50 | 26 | 66 | 44.5 | 55.96 | -11.46 |  |  |  |  |  |  |  |  |
| whisper-base-ur | standardised | 61 | 295 | 43.18 | 51.98 | -8.79 | -16.23 | -1.76 | False | 0.02 | 0.3197 | False | 1000 | 16-30+31-50+>50 |
| whisper-large-v3 | <=15 | 3 | 112 | 23.33 | 24.57 | -1.23 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 16-30 | 17 | 132 | 14.32 | 14.87 | -0.55 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 31-50 | 18 | 97 | 14.01 | 16.44 | -2.43 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | >50 | 26 | 66 | 13.13 | 16.66 | -3.53 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | standardised | 61 | 295 | 13.7 | 16.16 | -2.46 | -5.45 | 0.78 | True | 0.1399 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-large-v3-ur | <=15 | 3 | 112 | 23.33 | 20.66 | 2.68 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 16-30 | 17 | 132 | 16.58 | 16.71 | -0.13 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 31-50 | 18 | 97 | 15.92 | 16.73 | -0.81 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | >50 | 26 | 66 | 12.55 | 15.99 | -3.44 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | standardised | 61 | 295 | 14.58 | 16.4 | -1.82 | -4.82 | 1.58 | True | 0.2717 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-medium | <=15 | 3 | 112 | 40.0 | 38.49 | 1.51 |  |  |  |  |  |  |  |  |
| whisper-medium | 16-30 | 17 | 132 | 32.91 | 33.32 | -0.41 |  |  |  |  |  |  |  |  |
| whisper-medium | 31-50 | 18 | 97 | 49.66 | 42.1 | 7.56 |  |  |  |  |  |  |  |  |
| whisper-medium | >50 | 26 | 66 | 28.12 | 56.27 | -28.15 |  |  |  |  |  |  |  |  |
| whisper-medium | standardised | 61 | 295 | 36.06 | 46.28 | -10.22 | -27.04 | 11.26 | True | 0.3057 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-medium-ur | <=15 | 3 | 112 | 40.0 | 32.58 | 7.42 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 16-30 | 17 | 132 | 25.63 | 27.18 | -1.56 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 31-50 | 18 | 97 | 24.35 | 26.83 | -2.47 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | >50 | 26 | 66 | 24.08 | 27.97 | -3.88 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | standardised | 61 | 295 | 24.54 | 27.42 | -2.88 | -6.89 | 1.43 | True | 0.1858 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-small | <=15 | 3 | 112 | 50.0 | 74.61 | -24.61 |  |  |  |  |  |  |  |  |
| whisper-small | 16-30 | 17 | 132 | 85.68 | 40.02 | 45.66 |  |  |  |  |  |  |  |  |
| whisper-small | 31-50 | 18 | 97 | 38.37 | 43.21 | -4.85 |  |  |  |  |  |  |  |  |
| whisper-small | >50 | 26 | 66 | 41.15 | 47.98 | -6.84 |  |  |  |  |  |  |  |  |
| whisper-small | standardised | 61 | 295 | 51.0 | 44.56 | 6.44 | -11.92 | 33.83 | True | 0.7273 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-small-ur | <=15 | 3 | 112 | 36.67 | 37.4 | -0.73 |  |  |  |  |  |  |  |  |
| whisper-small-ur | 16-30 | 17 | 132 | 29.4 | 30.2 | -0.81 |  |  |  |  |  |  |  |  |
| whisper-small-ur | 31-50 | 18 | 97 | 29.25 | 30.92 | -1.66 |  |  |  |  |  |  |  |  |
| whisper-small-ur | >50 | 26 | 66 | 28.5 | 32.47 | -3.97 |  |  |  |  |  |  |  |  |
| whisper-small-ur | standardised | 61 | 295 | 28.95 | 31.43 | -2.48 | -6.84 | 2.43 | True | 0.2737 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-tiny | <=15 | 3 | 112 | 83.33 | 204.46 | -121.13 |  |  |  |  |  |  |  |  |
| whisper-tiny | 16-30 | 17 | 132 | 121.36 | 156.17 | -34.82 |  |  |  |  |  |  |  |  |
| whisper-tiny | 31-50 | 18 | 97 | 188.03 | 153.6 | 34.43 |  |  |  |  |  |  |  |  |
| whisper-tiny | >50 | 26 | 66 | 109.25 | 151.48 | -42.23 |  |  |  |  |  |  |  |  |
| whisper-tiny | standardised | 61 | 295 | 136.97 | 153.28 | -16.3 | -55.2 | 26.63 | True | 0.4196 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-tiny-ur | <=15 | 3 | 112 | 63.33 | 62.78 | 0.55 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 16-30 | 17 | 132 | 56.28 | 51.18 | 5.1 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 31-50 | 18 | 97 | 98.1 | 58.09 | 40.01 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | >50 | 26 | 66 | 54.6 | 65.0 | -10.4 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | standardised | 61 | 295 | 68.7 | 59.49 | 9.21 | -9.48 | 38.61 | True | 0.6653 | 1.0 | False | 1000 | 16-30+31-50+>50 |

## as_released~ — corpus_cer — buckets: fine

| model | bucket | n_flagged | n_unflagged | flagged | unflagged | delta | ci_low | ci_high | ci_includes_0 | p_boot | p_holm | reject_holm_05 | n_valid_resamples | buckets_used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hf-seamless-m4t-medium | <=15 | 3 | 112 | 15.71 | 20.93 | -5.22 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 16-30 | 17 | 132 | 7.39 | 9.08 | -1.69 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 31-50 | 18 | 97 | 6.72 | 9.13 | -2.41 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | >50 | 26 | 66 | 10.15 | 12.78 | -2.63 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | standardised | 61 | 295 | 8.41 | 10.74 | -2.33 | -5.34 | 1.07 | True | 0.1538 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-1b-all | <=15 | 3 | 112 | 30.71 | 25.38 | 5.33 |  |  |  |  |  |  |  |  |
| mms-1b-all | 16-30 | 17 | 132 | 19.93 | 19.87 | 0.06 |  |  |  |  |  |  |  |  |
| mms-1b-all | 31-50 | 18 | 97 | 17.1 | 19.08 | -1.98 |  |  |  |  |  |  |  |  |
| mms-1b-all | >50 | 26 | 66 | 16.61 | 19.57 | -2.96 |  |  |  |  |  |  |  |  |
| mms-1b-all | standardised | 61 | 295 | 17.56 | 19.49 | -1.92 | -4.28 | 0.61 | True | 0.1239 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-1b-ur | <=15 | 3 | 112 | 22.86 | 22.64 | 0.22 |  |  |  |  |  |  |  |  |
| mms-1b-ur | 16-30 | 17 | 132 | 19.16 | 20.44 | -1.28 |  |  |  |  |  |  |  |  |
| mms-1b-ur | 31-50 | 18 | 97 | 17.55 | 20.93 | -3.38 |  |  |  |  |  |  |  |  |
| mms-1b-ur | >50 | 26 | 66 | 16.42 | 23.79 | -7.36 |  |  |  |  |  |  |  |  |
| mms-1b-ur | standardised | 61 | 295 | 17.44 | 22.08 | -4.64 | -7.68 | -1.05 | False | 0.022 | 0.3516 | False | 1000 | 16-30+31-50+>50 |
| mms-300m-ur | <=15 | 3 | 112 | 37.14 | 29.69 | 7.46 |  |  |  |  |  |  |  |  |
| mms-300m-ur | 16-30 | 17 | 132 | 25.49 | 25.49 | -0.0 |  |  |  |  |  |  |  |  |
| mms-300m-ur | 31-50 | 18 | 97 | 27.39 | 26.38 | 1.01 |  |  |  |  |  |  |  |  |
| mms-300m-ur | >50 | 26 | 66 | 30.53 | 31.22 | -0.7 |  |  |  |  |  |  |  |  |
| mms-300m-ur | standardised | 61 | 295 | 28.32 | 28.32 | 0.01 | -2.62 | 2.55 | True | 0.997 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-medium-ur | <=15 | 3 | 112 | 15.71 | 14.05 | 1.66 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 16-30 | 17 | 132 | 8.22 | 8.55 | -0.33 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 31-50 | 18 | 97 | 5.88 | 10.22 | -4.34 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | >50 | 26 | 66 | 10.19 | 12.64 | -2.45 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | standardised | 61 | 295 | 8.36 | 10.89 | -2.54 | -5.46 | 0.69 | True | 0.1299 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-v2-large | <=15 | 3 | 112 | 10.71 | 14.94 | -4.23 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 16-30 | 17 | 132 | 13.31 | 19.42 | -6.12 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 31-50 | 18 | 97 | 14.82 | 18.52 | -3.7 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | >50 | 26 | 66 | 27.68 | 30.97 | -3.28 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | standardised | 61 | 295 | 20.17 | 24.26 | -4.1 | -8.37 | -0.27 | False | 0.042 | 0.6294 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-v2-large-ur | <=15 | 3 | 112 | 16.43 | 11.24 | 5.19 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 16-30 | 17 | 132 | 7.1 | 8.61 | -1.51 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 31-50 | 18 | 97 | 7.78 | 10.67 | -2.89 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | >50 | 26 | 66 | 9.28 | 15.76 | -6.48 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | standardised | 61 | 295 | 8.28 | 12.43 | -4.15 | -6.55 | -1.63 | False | 0.002 | 0.034 | True | 1000 | 16-30+31-50+>50 |
| whisper-base | <=15 | 3 | 112 | 479.29 | 165.49 | 313.79 |  |  |  |  |  |  |  |  |
| whisper-base | 16-30 | 17 | 132 | 136.07 | 117.52 | 18.56 |  |  |  |  |  |  |  |  |
| whisper-base | 31-50 | 18 | 97 | 99.9 | 92.59 | 7.31 |  |  |  |  |  |  |  |  |
| whisper-base | >50 | 26 | 66 | 62.31 | 77.15 | -14.84 |  |  |  |  |  |  |  |  |
| whisper-base | standardised | 61 | 295 | 91.93 | 91.74 | 0.18 | -39.01 | 41.92 | True | 0.9451 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-base-ur | <=15 | 3 | 112 | 30.0 | 26.16 | 3.84 |  |  |  |  |  |  |  |  |
| whisper-base-ur | 16-30 | 17 | 132 | 57.48 | 21.72 | 35.76 |  |  |  |  |  |  |  |  |
| whisper-base-ur | 31-50 | 18 | 97 | 21.76 | 37.95 | -16.19 |  |  |  |  |  |  |  |  |
| whisper-base-ur | >50 | 26 | 66 | 24.69 | 36.93 | -12.24 |  |  |  |  |  |  |  |  |
| whisper-base-ur | standardised | 61 | 295 | 31.67 | 33.59 | -1.92 | -16.99 | 21.47 | True | 0.7812 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-large-v3 | <=15 | 3 | 112 | 16.43 | 13.6 | 2.83 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 16-30 | 17 | 132 | 8.93 | 8.5 | 0.43 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 31-50 | 18 | 97 | 7.55 | 9.37 | -1.82 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | >50 | 26 | 66 | 6.47 | 10.0 | -3.53 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | standardised | 61 | 295 | 7.4 | 9.44 | -2.03 | -4.53 | 0.59 | True | 0.1359 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-large-v3-ur | <=15 | 3 | 112 | 10.71 | 11.03 | -0.31 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 16-30 | 17 | 132 | 8.28 | 9.8 | -1.52 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 31-50 | 18 | 97 | 7.2 | 9.66 | -2.46 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | >50 | 26 | 66 | 5.89 | 8.91 | -3.02 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | standardised | 61 | 295 | 6.88 | 9.36 | -2.48 | -4.68 | -0.06 | False | 0.046 | 0.6434 | False | 1000 | 16-30+31-50+>50 |
| whisper-medium | <=15 | 3 | 112 | 29.29 | 23.81 | 5.48 |  |  |  |  |  |  |  |  |
| whisper-medium | 16-30 | 17 | 132 | 23.42 | 23.67 | -0.25 |  |  |  |  |  |  |  |  |
| whisper-medium | 31-50 | 18 | 97 | 31.73 | 32.01 | -0.28 |  |  |  |  |  |  |  |  |
| whisper-medium | >50 | 26 | 66 | 17.07 | 40.99 | -23.91 |  |  |  |  |  |  |  |  |
| whisper-medium | standardised | 61 | 295 | 23.22 | 33.99 | -10.77 | -23.91 | 5.11 | True | 0.1738 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-medium-ur | <=15 | 3 | 112 | 12.14 | 17.64 | -5.5 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 16-30 | 17 | 132 | 13.31 | 15.0 | -1.69 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 31-50 | 18 | 97 | 11.25 | 14.95 | -3.7 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | >50 | 26 | 66 | 11.95 | 15.7 | -3.75 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | standardised | 61 | 295 | 12.05 | 15.29 | -3.24 | -6.22 | 0.06 | True | 0.0579 | 0.7532 | False | 1000 | 16-30+31-50+>50 |
| whisper-small | <=15 | 3 | 112 | 20.71 | 60.28 | -39.57 |  |  |  |  |  |  |  |  |
| whisper-small | 16-30 | 17 | 132 | 65.05 | 24.01 | 41.04 |  |  |  |  |  |  |  |  |
| whisper-small | 31-50 | 18 | 97 | 21.67 | 27.21 | -5.55 |  |  |  |  |  |  |  |  |
| whisper-small | >50 | 26 | 66 | 23.05 | 31.97 | -8.92 |  |  |  |  |  |  |  |  |
| whisper-small | standardised | 61 | 295 | 32.73 | 28.55 | 4.18 | -13.1 | 29.68 | True | 0.8611 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-small-ur | <=15 | 3 | 112 | 20.0 | 19.16 | 0.84 |  |  |  |  |  |  |  |  |
| whisper-small-ur | 16-30 | 17 | 132 | 13.42 | 16.7 | -3.27 |  |  |  |  |  |  |  |  |
| whisper-small-ur | 31-50 | 18 | 97 | 14.95 | 17.07 | -2.13 |  |  |  |  |  |  |  |  |
| whisper-small-ur | >50 | 26 | 66 | 15.06 | 17.59 | -2.52 |  |  |  |  |  |  |  |  |
| whisper-small-ur | standardised | 61 | 295 | 14.63 | 17.21 | -2.58 | -6.01 | 1.11 | True | 0.1479 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-tiny | <=15 | 3 | 112 | 45.0 | 163.72 | -118.72 |  |  |  |  |  |  |  |  |
| whisper-tiny | 16-30 | 17 | 132 | 87.23 | 116.01 | -28.78 |  |  |  |  |  |  |  |  |
| whisper-tiny | 31-50 | 18 | 97 | 150.95 | 118.51 | 32.44 |  |  |  |  |  |  |  |  |
| whisper-tiny | >50 | 26 | 66 | 73.95 | 115.12 | -41.17 |  |  |  |  |  |  |  |  |
| whisper-tiny | standardised | 61 | 295 | 101.39 | 116.4 | -15.0 | -49.57 | 23.96 | True | 0.4276 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-tiny-ur | <=15 | 3 | 112 | 35.0 | 58.92 | -23.92 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 16-30 | 17 | 132 | 32.94 | 27.12 | 5.82 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 31-50 | 18 | 97 | 48.83 | 32.58 | 16.25 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | >50 | 26 | 66 | 29.58 | 40.46 | -10.88 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | standardised | 61 | 295 | 36.45 | 34.76 | 1.69 | -9.78 | 17.06 | True | 0.9271 | 1.0 | False | 1000 | 16-30+31-50+>50 |

## N7_numwords — corpus_wer — buckets: fine

| model | bucket | n_flagged | n_unflagged | flagged | unflagged | delta | ci_low | ci_high | ci_includes_0 | p_boot | p_holm | reject_holm_05 | n_valid_resamples | buckets_used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hf-seamless-m4t-medium | <=15 | 3 | 112 | 20.0 | 34.85 | -14.85 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 16-30 | 17 | 132 | 14.07 | 16.91 | -2.84 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 31-50 | 18 | 97 | 13.74 | 17.03 | -3.28 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | >50 | 26 | 66 | 15.84 | 18.79 | -2.94 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | standardised | 61 | 295 | 14.75 | 17.78 | -3.03 | -6.61 | 0.76 | True | 0.1319 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-1b-all | <=15 | 3 | 112 | 63.33 | 53.05 | 10.29 |  |  |  |  |  |  |  |  |
| mms-1b-all | 16-30 | 17 | 132 | 41.96 | 43.7 | -1.74 |  |  |  |  |  |  |  |  |
| mms-1b-all | 31-50 | 18 | 97 | 41.9 | 43.03 | -1.12 |  |  |  |  |  |  |  |  |
| mms-1b-all | >50 | 26 | 66 | 39.66 | 44.42 | -4.76 |  |  |  |  |  |  |  |  |
| mms-1b-all | standardised | 61 | 295 | 40.92 | 43.81 | -2.89 | -6.72 | 0.88 | True | 0.1538 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-1b-ur | <=15 | 3 | 112 | 56.67 | 44.04 | 12.63 |  |  |  |  |  |  |  |  |
| mms-1b-ur | 16-30 | 17 | 132 | 37.94 | 40.97 | -3.03 |  |  |  |  |  |  |  |  |
| mms-1b-ur | 31-50 | 18 | 97 | 39.05 | 40.64 | -1.59 |  |  |  |  |  |  |  |  |
| mms-1b-ur | >50 | 26 | 66 | 38.49 | 45.86 | -7.37 |  |  |  |  |  |  |  |  |
| mms-1b-ur | standardised | 61 | 295 | 38.53 | 43.04 | -4.5 | -8.97 | 0.75 | True | 0.0939 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-300m-ur | <=15 | 3 | 112 | 80.0 | 67.61 | 12.39 |  |  |  |  |  |  |  |  |
| mms-300m-ur | 16-30 | 17 | 132 | 58.04 | 61.39 | -3.35 |  |  |  |  |  |  |  |  |
| mms-300m-ur | 31-50 | 18 | 97 | 66.39 | 64.7 | 1.69 |  |  |  |  |  |  |  |  |
| mms-300m-ur | >50 | 26 | 66 | 75.49 | 73.85 | 1.64 |  |  |  |  |  |  |  |  |
| mms-300m-ur | standardised | 61 | 295 | 68.42 | 67.97 | 0.46 | -4.1 | 4.66 | True | 0.8551 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-medium-ur | <=15 | 3 | 112 | 26.67 | 25.48 | 1.19 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 16-30 | 17 | 132 | 14.32 | 15.76 | -1.44 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 31-50 | 18 | 97 | 12.93 | 18.14 | -5.22 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | >50 | 26 | 66 | 16.0 | 19.73 | -3.72 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | standardised | 61 | 295 | 14.63 | 18.27 | -3.64 | -7.28 | 0.13 | True | 0.0679 | 0.951 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-v2-large | <=15 | 3 | 112 | 23.33 | 24.75 | -1.42 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 16-30 | 17 | 132 | 21.11 | 29.22 | -8.11 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 31-50 | 18 | 97 | 23.13 | 28.05 | -4.92 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | >50 | 26 | 66 | 37.96 | 42.45 | -4.5 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | standardised | 61 | 295 | 29.23 | 34.73 | -5.5 | -11.33 | -0.28 | False | 0.044 | 0.6593 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-v2-large-ur | <=15 | 3 | 112 | 23.33 | 20.93 | 2.41 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 16-30 | 17 | 132 | 14.07 | 14.08 | -0.01 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 31-50 | 18 | 97 | 15.24 | 18.19 | -2.96 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | >50 | 26 | 66 | 14.19 | 23.6 | -9.41 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | standardised | 61 | 295 | 14.49 | 19.6 | -5.11 | -8.16 | -1.91 | False | 0.006 | 0.1019 | False | 1000 | 16-30+31-50+>50 |
| whisper-base | <=15 | 3 | 112 | 773.33 | 235.4 | 537.94 |  |  |  |  |  |  |  |  |
| whisper-base | 16-30 | 17 | 132 | 143.97 | 152.63 | -8.66 |  |  |  |  |  |  |  |  |
| whisper-base | 31-50 | 18 | 97 | 130.88 | 129.8 | 1.08 |  |  |  |  |  |  |  |  |
| whisper-base | >50 | 26 | 66 | 91.33 | 106.92 | -15.58 |  |  |  |  |  |  |  |  |
| whisper-base | standardised | 61 | 295 | 116.47 | 125.14 | -8.67 | -48.52 | 32.32 | True | 0.6414 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-base-ur | <=15 | 3 | 112 | 63.33 | 49.41 | 13.92 |  |  |  |  |  |  |  |  |
| whisper-base-ur | 16-30 | 17 | 132 | 42.96 | 41.14 | 1.83 |  |  |  |  |  |  |  |  |
| whisper-base-ur | 31-50 | 18 | 97 | 41.5 | 54.37 | -12.87 |  |  |  |  |  |  |  |  |
| whisper-base-ur | >50 | 26 | 66 | 44.39 | 55.93 | -11.54 |  |  |  |  |  |  |  |  |
| whisper-base-ur | standardised | 61 | 295 | 43.14 | 51.87 | -8.74 | -16.21 | -1.72 | False | 0.02 | 0.3197 | False | 1000 | 16-30+31-50+>50 |
| whisper-large-v3 | <=15 | 3 | 112 | 26.67 | 24.66 | 2.01 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 16-30 | 17 | 132 | 14.82 | 15.0 | -0.18 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 31-50 | 18 | 97 | 13.88 | 16.49 | -2.62 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | >50 | 26 | 66 | 13.24 | 16.7 | -3.47 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | standardised | 61 | 295 | 13.82 | 16.23 | -2.41 | -5.42 | 0.85 | True | 0.1479 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-large-v3-ur | <=15 | 3 | 112 | 30.0 | 20.38 | 9.62 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 16-30 | 17 | 132 | 16.83 | 16.94 | -0.11 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 31-50 | 18 | 97 | 15.78 | 16.68 | -0.9 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | >50 | 26 | 66 | 12.39 | 15.97 | -3.58 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | standardised | 61 | 295 | 14.53 | 16.43 | -1.9 | -4.97 | 1.52 | True | 0.2438 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-medium | <=15 | 3 | 112 | 40.0 | 38.49 | 1.51 |  |  |  |  |  |  |  |  |
| whisper-medium | 16-30 | 17 | 132 | 33.17 | 33.36 | -0.19 |  |  |  |  |  |  |  |  |
| whisper-medium | 31-50 | 18 | 97 | 49.66 | 41.86 | 7.8 |  |  |  |  |  |  |  |  |
| whisper-medium | >50 | 26 | 66 | 28.23 | 56.27 | -28.04 |  |  |  |  |  |  |  |  |
| whisper-medium | standardised | 61 | 295 | 36.17 | 46.21 | -10.04 | -26.93 | 11.33 | True | 0.3097 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-medium-ur | <=15 | 3 | 112 | 40.0 | 32.67 | 7.33 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 16-30 | 17 | 132 | 25.88 | 27.12 | -1.24 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 31-50 | 18 | 97 | 24.35 | 26.77 | -2.42 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | >50 | 26 | 66 | 24.14 | 27.94 | -3.81 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | standardised | 61 | 295 | 24.62 | 27.38 | -2.75 | -6.83 | 1.52 | True | 0.1978 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-small | <=15 | 3 | 112 | 50.0 | 74.61 | -24.61 |  |  |  |  |  |  |  |  |
| whisper-small | 16-30 | 17 | 132 | 85.68 | 39.99 | 45.69 |  |  |  |  |  |  |  |  |
| whisper-small | 31-50 | 18 | 97 | 38.23 | 43.11 | -4.88 |  |  |  |  |  |  |  |  |
| whisper-small | >50 | 26 | 66 | 40.83 | 47.96 | -7.13 |  |  |  |  |  |  |  |  |
| whisper-small | standardised | 61 | 295 | 50.82 | 44.51 | 6.31 | -12.17 | 33.68 | True | 0.7313 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-small-ur | <=15 | 3 | 112 | 40.0 | 37.22 | 2.78 |  |  |  |  |  |  |  |  |
| whisper-small-ur | 16-30 | 17 | 132 | 29.65 | 30.3 | -0.65 |  |  |  |  |  |  |  |  |
| whisper-small-ur | 31-50 | 18 | 97 | 29.25 | 30.81 | -1.56 |  |  |  |  |  |  |  |  |
| whisper-small-ur | >50 | 26 | 66 | 28.44 | 32.49 | -4.05 |  |  |  |  |  |  |  |  |
| whisper-small-ur | standardised | 61 | 295 | 28.99 | 31.43 | -2.45 | -6.81 | 2.46 | True | 0.2817 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-tiny | <=15 | 3 | 112 | 83.33 | 204.28 | -120.94 |  |  |  |  |  |  |  |  |
| whisper-tiny | 16-30 | 17 | 132 | 121.36 | 156.17 | -34.82 |  |  |  |  |  |  |  |  |
| whisper-tiny | 31-50 | 18 | 97 | 188.03 | 153.6 | 34.43 |  |  |  |  |  |  |  |  |
| whisper-tiny | >50 | 26 | 66 | 109.25 | 151.48 | -42.23 |  |  |  |  |  |  |  |  |
| whisper-tiny | standardised | 61 | 295 | 136.97 | 153.28 | -16.3 | -55.2 | 26.63 | True | 0.4196 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-tiny-ur | <=15 | 3 | 112 | 63.33 | 62.78 | 0.55 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 16-30 | 17 | 132 | 56.28 | 51.18 | 5.1 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 31-50 | 18 | 97 | 98.1 | 57.98 | 40.11 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | >50 | 26 | 66 | 54.6 | 65.02 | -10.43 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | standardised | 61 | 295 | 68.7 | 59.47 | 9.23 | -9.47 | 38.62 | True | 0.6653 | 1.0 | False | 1000 | 16-30+31-50+>50 |

## N7_numwords — corpus_cer — buckets: fine

| model | bucket | n_flagged | n_unflagged | flagged | unflagged | delta | ci_low | ci_high | ci_includes_0 | p_boot | p_holm | reject_holm_05 | n_valid_resamples | buckets_used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hf-seamless-m4t-medium | <=15 | 3 | 112 | 15.71 | 21.04 | -5.32 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 16-30 | 17 | 132 | 7.51 | 9.08 | -1.57 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | 31-50 | 18 | 97 | 6.62 | 9.12 | -2.5 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | >50 | 26 | 66 | 10.15 | 12.76 | -2.61 |  |  |  |  |  |  |  |  |
| hf-seamless-m4t-medium | standardised | 61 | 295 | 8.4 | 10.73 | -2.32 | -5.36 | 1.05 | True | 0.1558 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-1b-all | <=15 | 3 | 112 | 30.71 | 25.38 | 5.33 |  |  |  |  |  |  |  |  |
| mms-1b-all | 16-30 | 17 | 132 | 19.93 | 19.85 | 0.08 |  |  |  |  |  |  |  |  |
| mms-1b-all | 31-50 | 18 | 97 | 17.01 | 18.9 | -1.89 |  |  |  |  |  |  |  |  |
| mms-1b-all | >50 | 26 | 66 | 16.48 | 19.55 | -3.08 |  |  |  |  |  |  |  |  |
| mms-1b-all | standardised | 61 | 295 | 17.48 | 19.42 | -1.94 | -4.29 | 0.55 | True | 0.1179 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| mms-1b-ur | <=15 | 3 | 112 | 22.86 | 22.72 | 0.13 |  |  |  |  |  |  |  |  |
| mms-1b-ur | 16-30 | 17 | 132 | 19.16 | 20.42 | -1.26 |  |  |  |  |  |  |  |  |
| mms-1b-ur | 31-50 | 18 | 97 | 17.52 | 20.84 | -3.31 |  |  |  |  |  |  |  |  |
| mms-1b-ur | >50 | 26 | 66 | 16.26 | 23.8 | -7.54 |  |  |  |  |  |  |  |  |
| mms-1b-ur | standardised | 61 | 295 | 17.36 | 22.05 | -4.69 | -7.74 | -1.07 | False | 0.02 | 0.3197 | False | 1000 | 16-30+31-50+>50 |
| mms-300m-ur | <=15 | 3 | 112 | 37.14 | 29.69 | 7.46 |  |  |  |  |  |  |  |  |
| mms-300m-ur | 16-30 | 17 | 132 | 25.49 | 25.48 | 0.01 |  |  |  |  |  |  |  |  |
| mms-300m-ur | 31-50 | 18 | 97 | 27.33 | 26.36 | 0.97 |  |  |  |  |  |  |  |  |
| mms-300m-ur | >50 | 26 | 66 | 30.52 | 31.22 | -0.7 |  |  |  |  |  |  |  |  |
| mms-300m-ur | standardised | 61 | 295 | 28.3 | 28.31 | -0.0 | -2.63 | 2.53 | True | 0.995 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-medium-ur | <=15 | 3 | 112 | 16.43 | 14.05 | 2.37 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 16-30 | 17 | 132 | 8.34 | 8.51 | -0.17 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | 31-50 | 18 | 97 | 5.79 | 10.06 | -4.27 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | >50 | 26 | 66 | 9.87 | 12.64 | -2.78 |  |  |  |  |  |  |  |  |
| seamless-m4t-medium-ur | standardised | 61 | 295 | 8.21 | 10.83 | -2.62 | -5.6 | 0.58 | True | 0.1199 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-v2-large | <=15 | 3 | 112 | 12.14 | 14.98 | -2.84 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 16-30 | 17 | 132 | 13.48 | 19.48 | -6.0 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | 31-50 | 18 | 97 | 14.73 | 18.51 | -3.78 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | >50 | 26 | 66 | 27.68 | 30.95 | -3.27 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large | standardised | 61 | 295 | 20.18 | 24.27 | -4.09 | -8.37 | -0.27 | False | 0.042 | 0.5874 | False | 1000 | 16-30+31-50+>50 |
| seamless-m4t-v2-large-ur | <=15 | 3 | 112 | 16.43 | 11.16 | 5.27 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 16-30 | 17 | 132 | 7.21 | 8.49 | -1.27 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | 31-50 | 18 | 97 | 7.68 | 10.61 | -2.92 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | >50 | 26 | 66 | 8.95 | 15.74 | -6.78 |  |  |  |  |  |  |  |  |
| seamless-m4t-v2-large-ur | standardised | 61 | 295 | 8.14 | 12.38 | -4.24 | -6.59 | -1.72 | False | 0.002 | 0.034 | True | 1000 | 16-30+31-50+>50 |
| whisper-base | <=15 | 3 | 112 | 479.29 | 165.45 | 313.84 |  |  |  |  |  |  |  |  |
| whisper-base | 16-30 | 17 | 132 | 136.13 | 117.41 | 18.72 |  |  |  |  |  |  |  |  |
| whisper-base | 31-50 | 18 | 97 | 99.87 | 92.49 | 7.38 |  |  |  |  |  |  |  |  |
| whisper-base | >50 | 26 | 66 | 62.3 | 77.15 | -14.85 |  |  |  |  |  |  |  |  |
| whisper-base | standardised | 61 | 295 | 91.92 | 91.68 | 0.24 | -38.94 | 42.01 | True | 0.951 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-base-ur | <=15 | 3 | 112 | 30.0 | 26.21 | 3.79 |  |  |  |  |  |  |  |  |
| whisper-base-ur | 16-30 | 17 | 132 | 57.48 | 21.71 | 35.77 |  |  |  |  |  |  |  |  |
| whisper-base-ur | 31-50 | 18 | 97 | 21.74 | 37.91 | -16.17 |  |  |  |  |  |  |  |  |
| whisper-base-ur | >50 | 26 | 66 | 24.66 | 36.91 | -12.25 |  |  |  |  |  |  |  |  |
| whisper-base-ur | standardised | 61 | 295 | 31.65 | 33.56 | -1.91 | -16.9 | 21.54 | True | 0.7812 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-large-v3 | <=15 | 3 | 112 | 16.43 | 13.69 | 2.74 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 16-30 | 17 | 132 | 9.05 | 8.47 | 0.57 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | 31-50 | 18 | 97 | 7.49 | 9.37 | -1.88 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | >50 | 26 | 66 | 6.47 | 9.99 | -3.52 |  |  |  |  |  |  |  |  |
| whisper-large-v3 | standardised | 61 | 295 | 7.41 | 9.43 | -2.02 | -4.52 | 0.59 | True | 0.1379 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-large-v3-ur | <=15 | 3 | 112 | 12.14 | 10.98 | 1.16 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 16-30 | 17 | 132 | 8.4 | 9.81 | -1.42 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | 31-50 | 18 | 97 | 7.11 | 9.59 | -2.48 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | >50 | 26 | 66 | 5.62 | 8.9 | -3.28 |  |  |  |  |  |  |  |  |
| whisper-large-v3-ur | standardised | 61 | 295 | 6.76 | 9.34 | -2.58 | -4.79 | -0.16 | False | 0.036 | 0.5395 | False | 1000 | 16-30+31-50+>50 |
| whisper-medium | <=15 | 3 | 112 | 29.29 | 23.81 | 5.48 |  |  |  |  |  |  |  |  |
| whisper-medium | 16-30 | 17 | 132 | 23.42 | 23.63 | -0.21 |  |  |  |  |  |  |  |  |
| whisper-medium | 31-50 | 18 | 97 | 31.7 | 31.77 | -0.07 |  |  |  |  |  |  |  |  |
| whisper-medium | >50 | 26 | 66 | 17.1 | 40.98 | -23.88 |  |  |  |  |  |  |  |  |
| whisper-medium | standardised | 61 | 295 | 23.22 | 33.9 | -10.68 | -23.84 | 5.2 | True | 0.1758 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-medium-ur | <=15 | 3 | 112 | 13.57 | 17.64 | -4.07 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 16-30 | 17 | 132 | 13.36 | 15.03 | -1.67 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | 31-50 | 18 | 97 | 11.19 | 14.91 | -3.72 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | >50 | 26 | 66 | 11.97 | 15.69 | -3.71 |  |  |  |  |  |  |  |  |
| whisper-medium-ur | standardised | 61 | 295 | 12.06 | 15.28 | -3.22 | -6.18 | 0.09 | True | 0.0559 | 0.7273 | False | 1000 | 16-30+31-50+>50 |
| whisper-small | <=15 | 3 | 112 | 20.71 | 60.26 | -39.55 |  |  |  |  |  |  |  |  |
| whisper-small | 16-30 | 17 | 132 | 64.99 | 23.93 | 41.06 |  |  |  |  |  |  |  |  |
| whisper-small | 31-50 | 18 | 97 | 21.51 | 27.13 | -5.62 |  |  |  |  |  |  |  |  |
| whisper-small | >50 | 26 | 66 | 22.76 | 31.95 | -9.18 |  |  |  |  |  |  |  |  |
| whisper-small | standardised | 61 | 295 | 32.54 | 28.5 | 4.05 | -13.1 | 29.37 | True | 0.8671 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-small-ur | <=15 | 3 | 112 | 20.71 | 19.14 | 1.58 |  |  |  |  |  |  |  |  |
| whisper-small-ur | 16-30 | 17 | 132 | 13.54 | 16.7 | -3.16 |  |  |  |  |  |  |  |  |
| whisper-small-ur | 31-50 | 18 | 97 | 14.89 | 16.94 | -2.05 |  |  |  |  |  |  |  |  |
| whisper-small-ur | >50 | 26 | 66 | 14.95 | 17.6 | -2.65 |  |  |  |  |  |  |  |  |
| whisper-small-ur | standardised | 61 | 295 | 14.59 | 17.17 | -2.58 | -6.03 | 1.06 | True | 0.1558 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-tiny | <=15 | 3 | 112 | 45.0 | 163.63 | -118.63 |  |  |  |  |  |  |  |  |
| whisper-tiny | 16-30 | 17 | 132 | 87.23 | 116.02 | -28.79 |  |  |  |  |  |  |  |  |
| whisper-tiny | 31-50 | 18 | 97 | 150.93 | 118.51 | 32.42 |  |  |  |  |  |  |  |  |
| whisper-tiny | >50 | 26 | 66 | 73.96 | 115.11 | -41.15 |  |  |  |  |  |  |  |  |
| whisper-tiny | standardised | 61 | 295 | 101.39 | 116.4 | -15.0 | -49.54 | 23.97 | True | 0.4236 | 1.0 | False | 1000 | 16-30+31-50+>50 |
| whisper-tiny-ur | <=15 | 3 | 112 | 35.0 | 58.88 | -23.88 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 16-30 | 17 | 132 | 32.94 | 27.11 | 5.83 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | 31-50 | 18 | 97 | 48.78 | 32.47 | 16.3 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | >50 | 26 | 66 | 29.57 | 40.46 | -10.89 |  |  |  |  |  |  |  |  |
| whisper-tiny-ur | standardised | 61 | 295 | 36.43 | 34.73 | 1.7 | -9.75 | 17.07 | True | 0.9251 | 1.0 | False | 1000 | 16-30+31-50+>50 |
