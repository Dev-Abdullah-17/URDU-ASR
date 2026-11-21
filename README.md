# Conversational Urdu ASR (code-switched)

Low-resource ASR for conversational, code-switched Urdu. We extend the "WER We
Stand" benchmark (COLING 2025) with a larger code-switched conversational test
set, an Urdu text normalizer, fine-tuned open models, a deployed voice tool, and
a paper.

- **Full plan:** [`PROJECT_PLAN.md`](PROJECT_PLAN.md)
- **Claude Code context:** [`CLAUDE.md`](CLAUDE.md)

## Dependencies
`requirements.txt` holds version ranges; `requirements.lock` is the exact
resolution (CPython 3.11, Linux x86_64) generated with
`uv pip compile requirements.txt --python-version 3.11 --python-platform x86_64-unknown-linux-gnu -o requirements.lock`.
CI (`.github/workflows/tests.yml`) installs the lock (minus torch/CUDA wheels,
which no test needs) and runs `pytest -q` on every push and pull request.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt            # or, exact pins (Linux, Python 3.11):
                                           #   pip install -r requirements.lock
pytest -q                                   # verify the normalizer
python src/evaluate_baseline.py --model openai/whisper-small \
  --dataset google/fleurs --config ur_pk --split test \
  --text-column transcription --max-samples 200 \
  --out results/baseline.json               # Phase 0: get your baseline numbers
```
