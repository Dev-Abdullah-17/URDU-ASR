"""Voice tool: speak Urdu -> transcription (Phase 4 MVP).

A minimal Gradio app that loads the fine-tuned Whisper model and transcribes
microphone or uploaded audio. Extend `answer()` to add retrieval + a spoken
response for the low-literacy assistant use case.

Environment:
    BASE_MODEL   base Whisper checkpoint (default openai/whisper-small)
    ADAPTER      path to LoRA adapter directory (optional)

Run:
    python app/app.py
"""

from __future__ import annotations

import os
import sys

import gradio as gr
import numpy as np
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from normalize_urdu import display_normalizer  # noqa: E402

BASE_MODEL = os.environ.get("BASE_MODEL", "openai/whisper-small")
ADAPTER = os.environ.get("ADAPTER", "")

_device = "cuda" if torch.cuda.is_available() else "cpu"
_processor = WhisperProcessor.from_pretrained(
    ADAPTER or BASE_MODEL, language="urdu", task="transcribe"
)
_model = WhisperForConditionalGeneration.from_pretrained(BASE_MODEL)
if ADAPTER:
    from peft import PeftModel

    _model = PeftModel.from_pretrained(_model, ADAPTER).merge_and_unload()
_model.to(_device).eval()


def transcribe(audio):
    if audio is None:
        return ""
    sr, array = audio  # gradio numpy audio -> (sample_rate, np.ndarray)
    array = array.astype(np.float32)
    if array.ndim > 1:
        array = array.mean(axis=1)
    peak = np.max(np.abs(array)) or 1.0
    array = array / peak
    if sr != 16_000:
        import librosa

        array = librosa.resample(array, orig_sr=sr, target_sr=16_000)
    feats = _processor.feature_extractor(
        array, sampling_rate=16_000, return_tensors="pt"
    ).input_features.to(_device)
    with torch.no_grad():
        gen = _model.generate(
            feats, language="urdu", task="transcribe", max_new_tokens=225
        )
    text = _processor.tokenizer.batch_decode(gen, skip_special_tokens=True)[0]
    return display_normalizer(text)


with gr.Blocks(title="Urdu Voice Transcriber") as demo:
    gr.Markdown(
        "## Urdu Voice Transcriber\n"
        "Speak or upload audio to get an Urdu transcript. "
        "Fine-tuned Whisper (low-resource conversational Urdu ASR)."
    )
    audio_in = gr.Audio(sources=["microphone", "upload"], type="numpy", label="Audio")
    btn = gr.Button("Transcribe", variant="primary")
    out = gr.Textbox(label="Transcript", lines=4, rtl=True)
    btn.click(transcribe, inputs=audio_in, outputs=out)


if __name__ == "__main__":
    demo.launch()
