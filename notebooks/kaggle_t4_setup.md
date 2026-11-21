# Kaggle T4 setup for `src/run_fleurs.py`

Copy-paste cells for a Kaggle notebook with **GPU T4** (x1 is enough; the script
is single-GPU) and **Internet on**. Outputs go to `/kaggle/working/results/fleurs`
(download them from the Output tab; never commit `results/`).

## Cell 1: install

```bash
%%bash
set -euo pipefail
cd /kaggle/working
git clone https://github.com/Dev-Abdullah-17/urdu-asr.git
cd urdu-asr && git checkout run-fleurs   # or main once merged

nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv
python -c "import torch; print('preinstalled torch', torch.__version__, 'cuda', torch.version.cuda)" || true

# 1) CUDA 12 torch build. T4 is sm_75 (Turing), which CUDA 12 wheels support.
#    Skip this line if the preinstalled torch above already reports cuda 12.x.
pip install -q "torch==2.8.0" --index-url https://download.pytorch.org/whl/cu126

# 2) Repo requirements WITHOUT touching torch: constrain pip to the torch that is
#    now installed, so nothing in requirements.txt can replace it.
python -c "import torch; print(f'torch=={torch.__version__}')" > /tmp/torch-constraint.txt
# transformers<4.48 needs huggingface-hub<1.0, and datasets>=5.1 needs hub>=1.31,
# so pin the pair that requirements.lock uses (datasets 5.0.1 + hub 0.36.2).
pip install -q -r requirements.txt -c /tmp/torch-constraint.txt \
    "datasets==5.0.1" "huggingface-hub==0.36.2"
# Only for SeamlessM4T models (their tokenizer):
pip install -q sentencepiece protobuf

python -c "import torch, transformers, datasets; print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0), transformers.__version__, datasets.__version__)"
```

## Cell 2: run (fp16 on GPU, greedy, fixed seed)

`--dtype auto` picks float16 on CUDA. T4 has no bf16, so do not pass `--dtype bfloat16`.

```bash
%%bash
cd /kaggle/working/urdu-asr
for CFG in ur_pk sd_in; do
  python src/run_fleurs.py --model openai/whisper-small --config "$CFG" \
      --batch-size 16 --seed 42 --device auto --out-root /kaggle/working/results/fleurs
done
# Other families (same flags):
#   python src/run_fleurs.py --model facebook/mms-1b-all --config sd_in --batch-size 8
#   python src/run_fleurs.py --model facebook/seamless-m4t-v2-large --config ur_pk --batch-size 4
```

Do a 5-utterance run first (add `--max-samples 5`) to check the setup. FLEURS test
has 299 utterances for ur_pk and 980 for sd_in. Each run writes
`outputs/<family>/<model>/fleurs-<config>.json` (hypotheses),
`fleurs-<config>.meta.json` (provenance, wall time, a quick WER/CER) and
`refs/fleurs-<config>-test.json`.

## Why not `requirements.lock`'s torch here

The lock pins `torch==2.15.0` from PyPI, which is a **CUDA 13** build
(`torch.__version__` reports `+cu132`) and pulls the `nvidia-*-cu13` runtime wheels.
The T4 itself is supported by CUDA 13 (Turing, sm_75 is the oldest arch it
keeps), but a CUDA 13 runtime needs an NVIDIA **driver of the R580 series or newer**.
Kaggle images have shipped CUDA 12.x drivers. With an older driver,
`torch.cuda.is_available()` returns False (or CUDA init fails) and the run would
quietly fall back to CPU. Check `driver_version` in Cell 1: if it is 580 or newer,
the lock's torch would also work. A cu126 build runs on any driver from R525 up
(CUDA 12 minor-version compatibility), so it is the safe choice. Reinstalling
the whole lock would also replace much of Kaggle's preinstalled stack for no
gain. Everything else follows `requirements.txt`, with the datasets/hub pair taken
from the lock.
