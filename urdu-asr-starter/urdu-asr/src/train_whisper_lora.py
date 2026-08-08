"""Fine-tune Whisper for Urdu ASR with LoRA (Phase 2).

Trains on Common Voice + FLEURS (or any HF speech dataset) using PEFT/LoRA so it
fits a single free-tier GPU (Kaggle P100 / T4). Includes a --smoke-test flag that
overfits a tiny subset first. ALWAYS run the smoke test before a long run: if the
model cannot drive loss down on 20 samples, the pipeline is broken -- stop.

Examples:
    # Sanity check first (a few minutes):
    python src/train_whisper_lora.py --smoke-test

    # Real run:
    python src/train_whisper_lora.py \
        --base-model openai/whisper-small \
        --dataset mozilla-foundation/common_voice_17_0 --config ur \
        --text-column sentence --train-split train --eval-split validation \
        --output-dir checkpoints/whisper-small-ur-lora \
        --epochs 3 --batch-size 8 --grad-accum 2 --lr 1e-4
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

import jiwer
import torch
from datasets import Audio, load_dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    WhisperForConditionalGeneration,
    WhisperProcessor,
)

from normalize_urdu import scoring_normalizer


@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any

    def __call__(self, features):
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(
            labels_batch.attention_mask.ne(1), -100
        )
        # Remove the leading BOS if the tokenizer prepended one (it is re-added).
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]
        batch["labels"] = labels
        return batch


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base-model", default="openai/whisper-small")
    p.add_argument("--dataset", default="mozilla-foundation/common_voice_17_0")
    p.add_argument("--config", default="ur")
    p.add_argument("--audio-column", default="audio")
    p.add_argument("--text-column", default="sentence")
    p.add_argument("--train-split", default="train")
    p.add_argument("--eval-split", default="validation")
    p.add_argument("--output-dir", default="checkpoints/whisper-ur-lora")
    p.add_argument("--epochs", type=float, default=3.0)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--grad-accum", type=int, default=2)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--lora-r", type=int, default=32)
    p.add_argument("--lora-alpha", type=int, default=64)
    p.add_argument("--language", default="urdu")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--smoke-test", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    torch.manual_seed(args.seed)

    processor = WhisperProcessor.from_pretrained(
        args.base_model, language=args.language, task="transcribe"
    )

    train_split, eval_split = args.train_split, args.eval_split
    if args.smoke_test:
        train_split = f"{args.train_split}[:20]"
        eval_split = f"{args.eval_split}[:20]"

    train_ds = load_dataset(args.dataset, args.config, split=train_split)
    eval_ds = load_dataset(args.dataset, args.config, split=eval_split)
    train_ds = train_ds.cast_column(args.audio_column, Audio(sampling_rate=16_000))
    eval_ds = eval_ds.cast_column(args.audio_column, Audio(sampling_rate=16_000))

    def prepare(batch):
        audio = batch[args.audio_column]
        batch["input_features"] = processor.feature_extractor(
            audio["array"], sampling_rate=16_000
        ).input_features[0]
        # Train on cased text; normalization is applied only for scoring.
        batch["labels"] = processor.tokenizer(batch[args.text_column]).input_ids
        return batch

    train_ds = train_ds.map(prepare, remove_columns=train_ds.column_names, num_proc=1)
    eval_ds = eval_ds.map(prepare, remove_columns=eval_ds.column_names, num_proc=1)

    model = WhisperForConditionalGeneration.from_pretrained(args.base_model)
    model.config.use_cache = False
    model.generation_config.language = args.language
    model.generation_config.task = "transcribe"
    model.generation_config.forced_decoder_ids = None

    lora = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
    )
    model = get_peft_model(model, lora)
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()  # needed with gradient checkpointing
    model.print_trainable_parameters()

    collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

    def compute_metrics(pred):
        pred_ids, label_ids = pred.predictions, pred.label_ids
        label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
        pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)
        pairs = [(scoring_normalizer(r), scoring_normalizer(h))
                 for r, h in zip(label_str, pred_str) if scoring_normalizer(r)]
        if not pairs:
            return {"wer": 1.0, "cer": 1.0}
        rs, hs = zip(*pairs)
        return {"wer": jiwer.wer(list(rs), list(hs)),
                "cer": jiwer.cer(list(rs), list(hs))}

    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    use_fp16 = torch.cuda.is_available() and not use_bf16

    targs = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        warmup_ratio=0.1,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        fp16=use_fp16,
        bf16=use_bf16,
        predict_with_generate=True,
        generation_max_length=225,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=25,
        report_to="none",
        remove_unused_columns=False,
        label_names=["labels"],
        load_best_model_at_end=True,
        metric_for_best_model="wer",
        greater_is_better=False,
        seed=args.seed,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=targs,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=collator,
        compute_metrics=compute_metrics,
        # On transformers >= 4.46 use `processing_class=processor` instead:
        tokenizer=processor.feature_extractor,
    )

    trainer.train()
    model.save_pretrained(args.output_dir)
    processor.save_pretrained(args.output_dir)
    print(f"Saved LoRA adapter + processor to {args.output_dir}")


if __name__ == "__main__":
    main()
