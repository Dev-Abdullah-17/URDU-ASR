# CLAUDE.md — operating context for Claude Code

## What this project is
Low-resource **conversational, code-switched Urdu ASR**. We extend Arif et al.
("WER We Stand", COLING 2025, arXiv:2409.11252), whose conversational Urdu set is
only ~1.3 hours and who explicitly flagged **code-switching, disfluencies, and the
lack of a robust Urdu text normalizer** as open problems. We deliver: a larger
code-switched conversational benchmark, an Urdu ASR text normalizer, fine-tuned
open Whisper/w2v-BERT models, a deployed voice tool, and a paper.

Read `PROJECT_PLAN.md` for the full spec. It is the source of truth.

## Repository map
- `src/normalize_urdu.py` — text normalizer + code-switch detector (reused everywhere).
- `src/evaluate_baseline.py` — Phase 0: zero-shot WER/CER baselines.
- `src/collect_audio.py` — Phase 1: prepare raw audio chunks for manual transcription.
- `src/train_whisper_lora.py` — Phase 2: LoRA fine-tuning (has `--smoke-test`).
- `src/evaluate_model.py` — Phase 3: evaluate fine-tuned model, code-switch split, per-utterance CSV.
- `app/app.py` — Phase 4: Gradio voice demo.
- `tests/` — unit tests (`pytest -q`).

## Non-negotiable conventions
1. **Always normalize before scoring.** Any WER/CER must run through
   `scoring_normalizer`. Never compare raw strings.
2. **Always smoke-test before a long run.** `python src/train_whisper_lora.py --smoke-test --dataset ...`
   must show loss decreasing on 20 samples. If it can't overfit 20 samples, the
   pipeline is broken — fix it before launching a real run.
3. **Single GPU, fixed seed.** Set `--seed` and keep runs single-GPU on free tiers.
4. **Pin versions.** Use `requirements.txt`. If you hit fp16 NaNs, prefer bf16
   where supported; on T4/P100 (no bf16) keep fp16 loss-scaling default and reduce LR.
5. **Never commit `data/`, `checkpoints/`, `results/`, or audio.** They're gitignored.
6. **Report WER and CER.** CER matters for Urdu script. Always break results into
   overall / code-switched / monolingual.
7. **Provenance for data.** Every collected clip needs a source URL + license note
   in the dataset card. Respect licensing; prefer an audio-less release if unsure.

## How to work through a task
- Implement one phase at a time, per `PROJECT_PLAN.md`.
- After changing `normalize_urdu.py`, run `pytest -q`.
- Prefer small, verifiable runs (`--max-samples`) before full runs.
- When adding a component, also add its acceptance check from the plan.

## Command cheat sheet
```bash
# setup
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Phase 0 baseline (FLEURS Urdu)
python src/evaluate_baseline.py --model openai/whisper-small \
  --dataset google/fleurs --config ur_pk --split test \
  --text-column transcription --max-samples 200 \
  --out results/baseline_whisper_small.json

# Phase 2 sanity check, then real run
python src/train_whisper_lora.py --smoke-test \
  --dataset google/fleurs --config ur_pk --text-column transcription
python src/train_whisper_lora.py --base-model openai/whisper-small \
  --dataset google/fleurs --config ur_pk --text-column transcription \
  --output-dir checkpoints/whisper-small-ur-lora --epochs 3

# Phase 3 evaluate fine-tuned
python src/evaluate_model.py --base-model openai/whisper-small \
  --adapter checkpoints/whisper-small-ur-lora \
  --dataset google/fleurs --config ur_pk --split test \
  --text-column transcription --out-json results/ft.json --out-csv results/ft.csv

# tests + demo
pytest -q
python app/app.py
```
