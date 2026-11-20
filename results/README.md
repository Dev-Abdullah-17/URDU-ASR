# Re-evaluation of the WER We Stand conversational outputs

This folder holds the aggregate results of `src/reeval_wws.py`. It rescores the
released hypotheses of *WER We Stand: Benchmarking Urdu ASR Models* (Arif et al.,
COLING 2025, arXiv:2409.11252): 17 models × 471 utterances of the conversational
set `urdu-asr/csalt-voice`.

| file | committed | contents |
|---|---|---|
| `reeval_table.csv` | yes | every subset × condition × metric × model: value, 95% CI, rank, Kendall's τ, n |
| `reeval_table.md` | yes | the same, as readable tables |
| `csalt_voice_refs.json` | **no** | cached references (dataset text; not ours to redistribute) |
| `reeval_per_utt.csv` | **no** | per-utterance errors with normalized reference/hypothesis text |
| `reeval_codeswitch_flags.csv` | **no** | per-utterance detector method, with reference text |
| `reeval_meta.json` | no | provenance (also listed below) |

## Reproduce

```bash
git clone https://github.com/sameearif/WER-We-Stand external/WER-We-Stand
python src/reeval_wws.py --wws-dir external/WER-We-Stand --out-dir results
```

The run takes about 25 s on CPU. Provenance of the committed tables:

- WER-We-Stand repo commit `9dd7f4d0580a608e53942916a37d4d417328b1b6`
- `urdu-asr/csalt-voice` revision `6f0c4fdeea94c77b4b64c4b88d5887e087566a5f`.
  This is the only dataset in the `urdu-asr` org. It has a single `validation`
  split with 471 rows.
- Bootstrap: 1000 resamples of utterances, seed 42. The same resampled index sets
  are used for every model and condition (paired).

## How references were loaded

WWS `src/utils.py::prepare_dataset` concatenates `train`+`test` **only if** a
`train` split exists. Otherwise it uses `validation`, and failing that, `test`.
`csalt-voice` has only `validation`, so no concatenation applies. The script
copies this branching exactly, logs which branch it took, and asserts 471
aligned pairs for every model.

## Conditions

| name | reference | hypothesis |
|---|---|---|
| `as_released~` | raw | WWS `compute_wer_csalt` cleanup (see below) |
| `raw` | raw | raw (whitespace tokenisation only) |
| `N1_unicode` … `N8_latin_drop` | same normalizer as hypothesis | cumulative steps of `src/normalize_urdu.py` |
| `N7+hamza_merge` | same as hypothesis | N7 + legacy آ→ا, ئ→ی, ؤ→و merge (ablation) |

The cumulative steps are:

- N1: NFC + zero-width removal
- N2: punctuation removal
- N3: lowercase Latin
- N4: Arabic→Urdu confusables
- N5: strip diacritics
- N6: digits→ASCII
- N7: digits→Urdu words (Latin tokens kept)
- N8: drop Latin tokens

### `as_released~` and the missing `chars.json`

`compute_wer_csalt` keeps only the hypothesis characters listed in `src/chars.json`.
That file is not in the WER-We-Stand repository at any commit. The script accepts
it via `--chars-json`. Without it, the script uses the 44-character inventory of
the 471 references as a stand-in, and the `~` suffix marks this. With the
stand-in, all 17 utterance-averaged WERs fall between 0.20 points below and 0.00
points above the paper's Table 3 (all within 0.20). The model ranking is
identical to the paper's.

## Normalization: paper text and released code

Paper, §4 "Experimental Design", p. 4 (arXiv:2409.11252):

> "Before conducting the evaluations, we normalize both the ground truth and the
> model predictions. This involves removing punctuation and disfluencies."

Released code, `src/wer.py` at commit `9dd7f4d`, lines 37–43
(`compute_wer_csalt`):

```python
    for i, item in enumerate(transcriptions):
        new_item = ""
        for c in item:
            if c in chars:
                new_item += c
        new_item = re.sub(r'#\S+', '', new_item)
        error += wer(dataset[i]["transcription"], " ".join(new_item.split()))
```

In these lines, the character filter, `#\S+` removal and whitespace collapsing
are applied to the model output (`item`). The reference
`dataset[i]["transcription"]` is passed to `wer` without modification. The
module-level pattern `r'[،.!\'"]'` (line 14) is applied to references only in
`compute_wer_arl`, not in `compute_wer_csalt`. The paper (§3.2.2) says
transcription was carried out in three passes. In the current dataset revision,
the `transcription` column contains no punctuation characters (see the inventory
below).

## Results summary

All numbers are % over all 471 utterances. Full tables with CIs are in
`reeval_table.md`.

### Effect of normalization

**Utterance-averaged WER (the paper's metric):**

- `raw` vs `as_released~`: differs by 0.00 (mms-1b-all) to +2.99 (whisper-medium) points.
- `N7_numwords` vs `as_released~`: differs by −0.11 to +0.31 points.
- Kendall's τ vs the as-released ranking is 0.971 for `raw` and 1.000 for N2–N8.

**Corpus WER:**

- `N7+hamza_merge` vs `N7_numwords`: lower by 0.07 (whisper-tiny) to 1.02 (mms-300m-ur) points.
- `N8_latin_drop` vs `N7_numwords`: differs by −0.37 to 0.00 points. The
  references contain no Latin letters, so this step removes Latin tokens from
  hypotheses only.

### Effect of aggregation (utterance-averaged vs corpus-level)

Under `as_released~`:

- Utterance-averaged minus corpus WER ranges from −3.14 (seamless-m4t-v2-large)
  to +31.13 (whisper-base) points.
- τ between the as-released ranking and the corpus-WER ranking is 0.897, and
  0.794 for corpus CER.
- Ranks 1–2 swap: whisper-large-v3 is ranked 1 by corpus WER (16.21) and
  whisper-large-v3-ur 1 by utterance-averaged WER (17.68).
- Ranks 3–5 reorder among the three Seamless models.

Under `N7_numwords`, the 95% CIs of the top two models overlap:

- whisper-large-v3: corpus WER 16.30 [15.12, 17.54]
- whisper-large-v3-ur: corpus WER 16.25 [14.92, 17.81]

### Code-switched vs monolingual

The old Latin-letter heuristic flags 0 of 471 references. The extended detector
(Urdu-script loanword list) flags 64, all by method `loanword`. Under
`N7_numwords`:

- Corpus WER on the 64 flagged utterances is lower than on the 407 others for
  15 of 17 models.
- The exceptions are mms-300m-ur (71.06 vs 67.45) and whisper-tiny-ur (65.41 vs
  59.28).

The detector has not been validated yet. `data/codeswitch_labels_template.csv`
(100 utterances, seed 42) is the sheet for measuring its precision and recall.

### Reference character inventory

44 distinct characters:

- space
- the digits `1` and `4`
- 41 Arabic-script letters, including ي U+064A (7 occurrences) and the hamza or
  madda letters آ (548), ئ (523) and ؤ (22)

The references contain no Latin letters, no punctuation and no diacritics.
