# Conversational Urdu ASR (code-switched)

Low-resource ASR for conversational, code-switched Urdu. We extend the "WER We
Stand" benchmark (COLING 2025) with a larger code-switched conversational test
set, an Urdu text normalizer, fine-tuned open models, a deployed voice tool, and
a paper.

- **Full plan:** [`PROJECT_PLAN.md`](PROJECT_PLAN.md)
- **Claude Code context:** [`CLAUDE.md`](CLAUDE.md)

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q                                   # verify the normalizer
python src/evaluate_baseline.py --model openai/whisper-small \
  --dataset google/fleurs --config ur_in --split test \
  --text-column transcription --max-samples 200 \
  --out results/baseline.json               # Phase 0: get your baseline numbers
```
