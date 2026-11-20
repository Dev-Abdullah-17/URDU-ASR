"""Evaluate a fine-tuned Whisper LoRA model (Phase 3).

Loads the base model + LoRA adapter, transcribes a test set, and reports WER/CER
overall, on the code-switched subset, and on the monolingual subset. Writes a
results JSON and a per-utterance CSV for error analysis -- the core table and the
code-switch figure for the paper.

Example:
    python src/evaluate_model.py \
        --base-model openai/whisper-small \
        --adapter checkpoints/whisper-small-ur-lora \
        --dataset google/fleurs --config ur_pk --split test \
        --text-column transcription \
        --out-json results/ft_whisper_small.json \
        --out-csv results/ft_whisper_small_per_utt.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os

import jiwer
import torch
from datasets import Audio, load_dataset
from tqdm import tqdm
from transformers import WhisperForConditionalGeneration, WhisperProcessor

from normalize_urdu import is_code_switched, scoring_normalizer


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base-model", default="openai/whisper-small")
    p.add_argument("--adapter", default=None, help="Path to LoRA adapter (optional)")
    p.add_argument("--dataset", required=True)
    p.add_argument("--config", default=None)
    p.add_argument("--split", default="test")
    p.add_argument("--audio-column", default="audio")
    p.add_argument("--text-column", default="transcription")
    p.add_argument("--language", default="urdu")
    p.add_argument("--max-samples", type=int, default=None)
    p.add_argument("--out-json", default="results/eval.json")
    p.add_argument("--out-csv", default="results/eval_per_utt.csv")
    return p.parse_args()


def agg(subset):
    if not subset:
        return None
    rs = [r["ref"] for r in subset]
    hs = [r["hyp"] for r in subset]
    return {"wer": jiwer.wer(rs, hs), "cer": jiwer.cer(rs, hs), "n": len(subset)}


def main():
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    processor = WhisperProcessor.from_pretrained(
        args.adapter or args.base_model, language=args.language, task="transcribe"
    )
    model = WhisperForConditionalGeneration.from_pretrained(args.base_model)
    if args.adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, args.adapter).merge_and_unload()
    model.to(device).eval()

    ds = load_dataset(args.dataset, args.config, split=args.split)
    ds = ds.cast_column(args.audio_column, Audio(sampling_rate=16_000))
    if args.max_samples:
        ds = ds.select(range(min(args.max_samples, len(ds))))

    rows = []
    for row in tqdm(ds, desc="evaluating"):
        audio = row[args.audio_column]
        feats = processor.feature_extractor(
            audio["array"], sampling_rate=16_000, return_tensors="pt"
        ).input_features.to(device)
        with torch.no_grad():
            gen = model.generate(
                feats, language=args.language, task="transcribe", max_new_tokens=225
            )
        hyp_raw = processor.tokenizer.batch_decode(gen, skip_special_tokens=True)[0]
        ref_raw = row[args.text_column]
        ref, hyp = scoring_normalizer(ref_raw), scoring_normalizer(hyp_raw)
        if not ref:
            continue
        rows.append(
            {
                "ref": ref,
                "hyp": hyp,
                "ref_raw": ref_raw,
                "hyp_raw": hyp_raw,
                "code_switched": is_code_switched(ref_raw),
                "wer": jiwer.wer(ref, hyp),
                "cer": jiwer.cer(ref, hyp),
            }
        )

    cs = [r for r in rows if r["code_switched"]]
    mono = [r for r in rows if not r["code_switched"]]
    results = {
        "base_model": args.base_model,
        "adapter": args.adapter,
        "dataset": f"{args.dataset}/{args.config}:{args.split}",
        "overall": agg(rows),
        "code_switched": agg(cs),
        "monolingual": agg(mono),
    }

    os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    fieldnames = list(rows[0].keys()) if rows else [
        "ref", "hyp", "ref_raw", "hyp_raw", "code_switched", "wer", "cer"
    ]
    os.makedirs(os.path.dirname(args.out_csv) or ".", exist_ok=True)
    with open(args.out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
