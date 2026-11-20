"""Zero-shot ASR baseline evaluation (Phase 0).

Runs a pretrained ASR model on a Hugging Face speech dataset and reports WER
and CER (overall + code-switched subset + monolingual subset), after Urdu text
normalization. These numbers are the "gap" that motivates the whole project.

Examples:
    # FLEURS Urdu (text column is `transcription`):
    python src/evaluate_baseline.py \
        --model openai/whisper-small \
        --dataset google/fleurs --config ur_pk --split test \
        --text-column transcription --max-samples 200 \
        --out results/baseline_whisper_small_fleurs.json

    # Common Voice Urdu (text column is `sentence`). NOTE: Common Voice left the
    # HF Hub in Oct 2025; download it from the Mozilla Data Collective and point
    # --dataset at a local copy (e.g. an `audiofolder` / loader script path):
    python src/evaluate_baseline.py \
        --model openai/whisper-small \
        --dataset data/common_voice_ur --split test \
        --text-column sentence --max-samples 200 \
        --out results/baseline_whisper_small_cv.json
"""

from __future__ import annotations

import argparse
import json
import os

import jiwer
from datasets import Audio, load_dataset
from tqdm import tqdm
from transformers import pipeline

from normalize_urdu import is_code_switched, scoring_normalizer


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--dataset", required=True)
    p.add_argument("--config", default=None)
    p.add_argument("--split", default="test")
    p.add_argument("--audio-column", default="audio")
    p.add_argument("--text-column", default="transcription")
    p.add_argument("--language", default="urdu")
    p.add_argument("--max-samples", type=int, default=None)
    p.add_argument("--device", type=int, default=0)
    p.add_argument("--out", default="results/baseline.json")
    return p.parse_args()


def score(refs, hyps):
    if not refs:
        return None
    return {"wer": jiwer.wer(refs, hyps), "cer": jiwer.cer(refs, hyps), "n": len(refs)}


def main():
    args = parse_args()

    ds = load_dataset(args.dataset, args.config, split=args.split)
    ds = ds.cast_column(args.audio_column, Audio(sampling_rate=16_000))
    if args.max_samples:
        ds = ds.select(range(min(args.max_samples, len(ds))))

    asr = pipeline(
        "automatic-speech-recognition",
        model=args.model,
        device=args.device,
        chunk_length_s=30,
    )
    gen_kwargs = {"task": "transcribe"}
    if "whisper" in args.model.lower():
        gen_kwargs["language"] = args.language

    refs, hyps, cs_flags = [], [], []
    for row in tqdm(ds, desc="transcribing"):
        audio = row[args.audio_column]
        out = asr(audio["array"], generate_kwargs=gen_kwargs)
        ref_raw = row[args.text_column]
        ref = scoring_normalizer(ref_raw)
        if not ref:
            continue
        refs.append(ref)
        hyps.append(scoring_normalizer(out["text"]))
        cs_flags.append(is_code_switched(ref_raw))

    cs = [(r, h) for r, h, f in zip(refs, hyps, cs_flags) if f]
    mono = [(r, h) for r, h, f in zip(refs, hyps, cs_flags) if not f]

    results = {
        "model": args.model,
        "dataset": f"{args.dataset}/{args.config}:{args.split}",
        "overall": score(refs, hyps),
        "code_switched": score([r for r, _ in cs], [h for _, h in cs]),
        "monolingual": score([r for r, _ in mono], [h for _, h in mono]),
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
