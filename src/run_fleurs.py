"""Run an HF ASR model on Google FLEURS (ur_pk / sd_in, test split) and save the
hypotheses in WER-We-Stand's output format.

Output layout (everything under --out-root, default ``results/fleurs``; results/
is gitignored, never commit it):

    <out-root>/outputs/<family>/<model-basename>/fleurs-<config>.json
        JSON list of hypothesis strings, one per utterance, in dataset order.
        Exactly the format of WER-We-Stand's released
        ``outputs/<family>/<model>/csalt-voice.json`` (their src/inference.py:
        ``json.dump(list_of_str, f)``, ASCII-escaped). <family> uses their
        directory names: ``whisper``, ``mms``, ``seamlessm4t``.
    <out-root>/outputs/<family>/<model-basename>/fleurs-<config>.meta.json
        Provenance: model id + revision, dataset id + resolved revision, loader,
        config, split, n, utterance ids (ints, no text), generation settings,
        forced language/task, seed, library versions, device, wall time.
    <out-root>/refs/fleurs-<config>-test.json
        JSON list of the ``transcription`` column, same order and length as the
        hypotheses of the run that wrote it (a --max-samples run writes a
        truncated refs file; meta records ``complete``).

Model families and forced language codes (see LANG_CODES):

    family        ur_pk                sd_in   how it is forced
    whisper       urdu                 sindhi  generate(language=..., task="transcribe")
    mms           urd-script_arabic    snd     tokenizer.set_target_lang + load_adapter
    seamlessm4t   urd                  snd     generate(tgt_lang=...)

The MMS codes are the adapter names in facebook/mms-1b-all (adapter.<code>.safetensors);
both vocabularies are Perso-Arabic script. ``seamless`` is accepted as an alias
of ``seamlessm4t``. Decoding is deterministic: greedy (num_beams=1, do_sample=False)
unless --num-beams; CTC (MMS) is argmax.

Status: whisper smoke-tested (openai/whisper-tiny, CPU); mms (facebook/mms-1b-all)
and seamlessm4t (facebook/hf-seamless-m4t-medium, SeamlessM4TForSpeechToText)
smoke-tested on 3 utterances per config; the v2 path (SeamlessM4Tv2ForSpeechToText,
chosen when "v2" is in the model id) is untested. SeamlessM4T's tokenizer needs
``sentencepiece`` (and ``protobuf``), which are not in requirements.txt:
``pip install sentencepiece protobuf``. The WWS fine-tuned seamless checkpoints
(seamless_communication / fairseq2) are out of scope.

FLEURS loading
--------------
``google/fleurs`` used to be a loading-script dataset; datasets>=4 no longer runs
scripts. Since Hub commit "Convert dataset to Parquet (#31)" the *main* branch
itself ships ``parquet-data/<config>/<split>-*.parquet`` with ``configs:`` in the
README, so a plain ``load_dataset("google/fleurs", config, split="test",
revision=<sha>)`` works with datasets 5.x. We pin --revision to that commit
(FLEURS_REVISION) and record the resolved sha in meta. ``refs/convert/parquet``
(the Hub's automatic conversion) is a fallback (--revision refs/convert/parquet).
Audio is read with ``Audio(decode=False)`` and decoded here with soundfile,
resampled to 16 kHz with librosa when needed; this avoids datasets 5.x's
torchcodec/FFmpeg audio decoder dependency.

Scoring these outputs with src/reeval_wws.py (NOT done here; reeval_wws.py is
deliberately unchanged)
--------------------------------------------------------------------------------
reeval_wws.py is hard-wired to csalt-voice. To score FLEURS outputs it needs:

1. ``load_hypotheses(wws_dir)`` globs ``outputs/*/*/csalt-voice.json``: add a
   ``--dataset-name`` option (e.g. ``fleurs-ur_pk``) used in that glob, and point
   ``--wws-dir`` at this script's --out-root (the layout is identical). The glob
   pattern ``<name>.json`` does not match our ``<name>.meta.json``.
2. ``assert len(hyps) == N_MODELS`` (17): make N_MODELS optional (``--n-models``,
   default 17 for csalt-voice, None = any number >= 1).
3. ``assert len(refs) == N_UTTERANCES`` (471) in main(): make it ``--n-utterances``
   (default 471; FLEURS test has 299 for ur_pk and 980 for sd_in) or drop it and
   keep only the per-model ``len(h) == len(refs)`` alignment check.
4. References: ``--refs-json <out-root>/refs/fleurs-<config>-test.json`` already
   works (list[str] accepted). Change ``--cache-refs``'s csalt default when
   scoring FLEURS so csalt_voice_refs.json is not overwritten; prepare_dataset_like_wws
   (validation-split logic) is csalt-specific and should not be used for FLEURS.
5. PAPER_WER is keyed by csalt model names; ``paper_wer`` should be blank for
   FLEURS (it is looked up with .get, so it already is).
6. The ``as_released~`` condition derives a character inventory from the
   references: fine for FLEURS; no WWS chars.json exists for Sindhi.
7. Caveat for sd_in: the N4 confusable map (and repo-wide ``scoring_normalizer``)
   is Urdu-tuned. It maps Arabic kaf ك -> ک (keheh), which in Sindhi is a
   different letter (kh) from Sindhi kaf ڪ, and Arabic heh ه -> ہ. Applied to both
   sides it is symmetric, but Sindhi WER under N4+ is not a Sindhi-correct
   normalization; report sd_in under N1-N3 too.
8. The code-switch subsets (Latin / Urdu loanword detector) are Urdu-specific
   and nearly empty on FLEURS (read Wikipedia sentences).

Examples
--------
    # Whisper, both configs, fp16 on GPU
    python src/run_fleurs.py --model openai/whisper-small --config ur_pk
    python src/run_fleurs.py --model openai/whisper-small --config sd_in
    # MMS / SeamlessM4T
    python src/run_fleurs.py --model facebook/mms-1b-all --config sd_in
    python src/run_fleurs.py --model facebook/seamless-m4t-v2-large --config ur_pk
    # CPU smoke test on 5 utterances
    python src/run_fleurs.py --model openai/whisper-tiny --config ur_pk \\
        --max-samples 5 --device cpu --out-root /tmp/fleurs_smoke
"""

from __future__ import annotations

import argparse
import io
import json
import os
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

DATASET_ID = "google/fleurs"
# Hub commit "Convert dataset to Parquet (#31)" on main (native parquet configs).
FLEURS_REVISION = "70bb2e84b976b7e960aa89f1c648e09c59f894dd"
SPLIT = "test"
TEXT_COLUMN = "transcription"
SAMPLING_RATE = 16_000
CONFIGS = ("ur_pk", "sd_in")
FAMILIES = ("whisper", "mms", "seamlessm4t")
FAMILY_ALIASES = {"seamless": "seamlessm4t", "seamless-m4t": "seamlessm4t",
                  "seamless_m4t": "seamlessm4t"}

# Forced target language per family x FLEURS config.
LANG_CODES = {
    "whisper": {"ur_pk": "urdu", "sd_in": "sindhi"},
    "mms": {"ur_pk": "urd-script_arabic", "sd_in": "snd"},
    "seamlessm4t": {"ur_pk": "urd", "sd_in": "snd"},
}
WHISPER_MAX_NEW_TOKENS = 440  # 448 target positions minus the 4 forced prompt tokens


# --------------------------------------------------------------------------- #
# Pure-Python helpers (no torch / datasets / network; unit-tested)
# --------------------------------------------------------------------------- #

def canonical_family(family: str) -> str:
    f = family.strip().lower()
    f = FAMILY_ALIASES.get(f, f)
    if f not in FAMILIES:
        raise ValueError(f"unknown model family {family!r}; expected one of {FAMILIES}")
    return f


def infer_family(model_id: str) -> str:
    m = model_id.lower()
    if "whisper" in m:
        return "whisper"
    if "mms" in m:
        return "mms"
    if "seamless" in m:
        return "seamlessm4t"
    raise ValueError(f"cannot infer family from {model_id!r}; pass --family")


def lang_code(family: str, config: str) -> str:
    family = canonical_family(family)
    if config not in CONFIGS:
        raise ValueError(f"unsupported FLEURS config {config!r}; expected one of {CONFIGS}")
    return LANG_CODES[family][config]


def model_basename(model_id: str) -> str:
    """Last path component, like WWS's ``model_name.split('/')[-1]``."""
    base = model_id.rstrip("/").split("/")[-1]
    if not base:
        raise ValueError(f"bad model id {model_id!r}")
    return base


def dataset_name(config: str) -> str:
    return f"fleurs-{config}"


def output_paths(out_root: str, family: str, model_id: str, config: str,
                 split: str = SPLIT) -> dict[str, str]:
    family = canonical_family(family)
    d = os.path.join(out_root, "outputs", family, model_basename(model_id))
    name = dataset_name(config)
    return {
        "hyps": os.path.join(d, f"{name}.json"),
        "meta": os.path.join(d, f"{name}.meta.json"),
        "refs": os.path.join(out_root, "refs", f"{name}-{split}.json"),
    }


def _atomic_write_json(path: str, obj, **kw) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, **kw)
    os.replace(tmp, path)


def write_string_list(path: str, items) -> None:
    """Write a JSON list[str] exactly like WWS inference.py (json.dump, ASCII-escaped)."""
    items = list(items)
    if not all(isinstance(s, str) for s in items):
        raise TypeError("expected a list of str")
    _atomic_write_json(path, items)


def load_string_list(path: str) -> list[str]:
    """reeval_wws.load_hypotheses-style check: JSON list[str]."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not all(isinstance(s, str) for s in data):
        raise ValueError(f"{path}: expected a JSON list of str")
    return data


def batched(seq, n: int):
    if n < 1:
        raise ValueError("batch size must be >= 1")
    buf = []
    for x in seq:
        buf.append(x)
        if len(buf) == n:
            yield buf
            buf = []
    if buf:
        yield buf


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #

def load_fleurs(config: str, revision: str, max_samples: int | None, streaming: bool):
    from datasets import Audio, load_dataset

    ds = load_dataset(DATASET_ID, config, split=SPLIT, revision=revision, streaming=streaming)
    ds = ds.cast_column("audio", Audio(sampling_rate=SAMPLING_RATE, decode=False))
    n_full = None
    try:
        n_full = ds.info.splits[SPLIT].num_examples
    except Exception:
        pass
    if max_samples is not None:
        ds = ds.take(max_samples) if streaming else ds.select(range(min(max_samples, len(ds))))
    elif not streaming:
        n_full = len(ds)
    return ds, n_full


def decode_audio(audio: dict):
    import numpy as np
    import soundfile as sf

    if audio.get("bytes"):
        x, sr = sf.read(io.BytesIO(audio["bytes"]), dtype="float32", always_2d=False)
    else:
        x, sr = sf.read(audio["path"], dtype="float32", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SAMPLING_RATE:
        import librosa
        x = librosa.resample(x, orig_sr=sr, target_sr=SAMPLING_RATE)
    return np.ascontiguousarray(x, dtype=np.float32)


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #

class WhisperASR:
    def __init__(self, model_id, lang, device, dtype, num_beams, max_new_tokens):
        from transformers import WhisperForConditionalGeneration, WhisperProcessor

        self.processor = WhisperProcessor.from_pretrained(model_id)
        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_id, torch_dtype=dtype).to(device).eval()
        self.device, self.dtype = device, dtype
        self.gen = {"language": lang, "task": "transcribe", "num_beams": num_beams,
                    "do_sample": False, "max_new_tokens": max_new_tokens}
        self.n_longform = 0

    def __call__(self, arrays):
        import torch

        fe = self.processor.feature_extractor
        longest = max(len(a) for a in arrays)
        if longest <= fe.n_samples:          # <= 30 s: standard padded short-form
            feats = self.processor(arrays, sampling_rate=SAMPLING_RATE, return_tensors="pt",
                                   return_attention_mask=True)
        else:                                 # > 30 s: sequential long-form decoding
            self.n_longform += sum(len(a) > fe.n_samples for a in arrays)
            feats = self.processor(arrays, sampling_rate=SAMPLING_RATE, return_tensors="pt",
                                   truncation=False, padding="longest",
                                   return_attention_mask=True)
        inp = feats.input_features.to(self.device, dtype=self.dtype)
        am = feats.attention_mask.to(self.device)
        with torch.inference_mode():
            out = self.model.generate(inp, attention_mask=am, **self.gen)
        seqs = out["sequences"] if isinstance(out, dict) else out
        return self.processor.batch_decode(seqs, skip_special_tokens=True)


class MMSASR:
    def __init__(self, model_id, lang, device, dtype, num_beams, max_new_tokens):
        from transformers import AutoProcessor, Wav2Vec2ForCTC

        if num_beams != 1:
            raise ValueError("MMS (CTC) decoding is greedy argmax; --num-beams must be 1")
        self.processor = AutoProcessor.from_pretrained(model_id, target_lang=lang)
        self.model = Wav2Vec2ForCTC.from_pretrained(
            model_id, target_lang=lang, ignore_mismatched_sizes=True, torch_dtype=dtype)
        self.processor.tokenizer.set_target_lang(lang)
        self.model.load_adapter(lang)
        self.model.to(device).eval()
        self.device, self.dtype = device, dtype
        self.gen = {"target_lang": lang, "decoding": "ctc_greedy_argmax"}

    def __call__(self, arrays):
        import torch

        feats = self.processor(arrays, sampling_rate=SAMPLING_RATE, return_tensors="pt",
                               padding=True, return_attention_mask=True)
        inp = feats.input_values.to(self.device, dtype=self.dtype)
        am = feats.attention_mask.to(self.device)
        with torch.inference_mode():
            logits = self.model(inp, attention_mask=am).logits
        return self.processor.batch_decode(logits.argmax(dim=-1))


class SeamlessASR:
    def __init__(self, model_id, lang, device, dtype, num_beams, max_new_tokens):
        from transformers import (AutoProcessor, SeamlessM4TForSpeechToText,
                                  SeamlessM4Tv2ForSpeechToText)

        cls = SeamlessM4Tv2ForSpeechToText if "v2" in model_id.lower() else SeamlessM4TForSpeechToText
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = cls.from_pretrained(model_id, torch_dtype=dtype).to(device).eval()
        self.device, self.dtype = device, dtype
        self.gen = {"tgt_lang": lang, "num_beams": num_beams, "do_sample": False}
        if max_new_tokens:
            self.gen["max_new_tokens"] = max_new_tokens

    def __call__(self, arrays):
        import torch

        feats = self.processor(audios=arrays, sampling_rate=SAMPLING_RATE, return_tensors="pt",
                               padding=True)
        feats = {k: (v.to(self.device, dtype=self.dtype) if v.is_floating_point()
                     else v.to(self.device)) for k, v in feats.items()}
        with torch.inference_mode():
            out = self.model.generate(**feats, **self.gen)
        seqs = out[0] if isinstance(out, tuple) else out
        return self.processor.batch_decode(seqs, skip_special_tokens=True)


MODEL_CLASSES = {"whisper": WhisperASR, "mms": MMSASR, "seamlessm4t": SeamlessASR}


# --------------------------------------------------------------------------- #
# Provenance + scoring
# --------------------------------------------------------------------------- #

def _hub_sha(repo_id: str, revision: str | None, repo_type: str) -> str:
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        info = (api.dataset_info(repo_id, revision=revision) if repo_type == "dataset"
                else api.model_info(repo_id, revision=revision))
        return info.sha
    except Exception as e:  # provenance only; never fatal
        return f"unavailable: {e.__class__.__name__}"


def _git_rev() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", os.path.dirname(os.path.abspath(__file__)), "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _versions() -> dict:
    v = {"python": platform.python_version()}
    for mod in ("torch", "transformers", "datasets", "huggingface_hub", "soundfile",
                "librosa", "numpy"):
        try:
            v[mod] = __import__(mod).__version__
        except Exception:
            v[mod] = None
    return v


def quick_score(refs: list[str], hyps: list[str]) -> dict:
    """Corpus WER/CER (%) after scoring_normalizer, overall / code-switched / monolingual."""
    import jiwer

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from normalize_urdu import is_code_switched_extended, scoring_normalizer

    rows = [(scoring_normalizer(r), scoring_normalizer(h), is_code_switched_extended(r))
            for r, h in zip(refs, hyps)]
    rows = [x for x in rows if x[0]]
    out = {}
    for sub, keep in (("overall", lambda cs: True), ("code_switched", lambda cs: cs),
                      ("monolingual", lambda cs: not cs)):
        sel = [(r, h) for r, h, cs in rows if keep(cs)]
        if not sel:
            out[sub] = {"n": 0}
            continue
        rr, hh = [r for r, _ in sel], [h for _, h in sel]
        out[sub] = {"n": len(sel), "corpus_wer": round(100 * jiwer.wer(rr, hh), 2),
                    "corpus_cer": round(100 * jiwer.cer(rr, hh), 2)}
    out["n_excluded_empty_ref"] = len(refs) - len(rows)
    out["normalizer"] = "normalize_urdu.scoring_normalizer (Urdu-tuned)"
    return out


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--model", required=True, help="HF model id, e.g. openai/whisper-small")
    p.add_argument("--family", default=None,
                   help=f"one of {FAMILIES} (alias: seamless); inferred from --model if omitted")
    p.add_argument("--config", required=True, choices=CONFIGS)
    p.add_argument("--revision", default=FLEURS_REVISION,
                   help="google/fleurs revision (default: pinned parquet commit on main; "
                        "fallback: refs/convert/parquet)")
    p.add_argument("--out-root", default="results/fleurs")
    p.add_argument("--max-samples", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--num-beams", type=int, default=1)
    p.add_argument("--max-new-tokens", type=int, default=None,
                   help=f"default: {WHISPER_MAX_NEW_TOKENS} for whisper, model default otherwise")
    p.add_argument("--device", default="auto", help="auto | cpu | cuda | cuda:N")
    p.add_argument("--dtype", default="auto", choices=("auto", "float32", "float16", "bfloat16"),
                   help="auto = float16 on CUDA, float32 on CPU")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--streaming", default="auto", choices=("auto", "on", "off"),
                   help="auto = stream only when --max-samples is set")
    p.add_argument("--no-score", action="store_true", help="skip the quick WER/CER printout")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    t_start = time.time()
    family = canonical_family(args.family) if args.family else infer_family(args.model)
    lang = lang_code(family, args.config)
    paths = output_paths(args.out_root, family, args.model, args.config)
    streaming = {"on": True, "off": False}.get(args.streaming, args.max_samples is not None)

    import numpy as np
    import torch
    from transformers import set_seed

    random.seed(args.seed)
    np.random.seed(args.seed)
    set_seed(args.seed)
    torch.use_deterministic_algorithms(False)  # inference only; greedy decoding is deterministic

    device = args.device
    if device == "auto":
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype_name = args.dtype
    if dtype_name == "auto":
        dtype_name = "float16" if device.startswith("cuda") else "float32"
    dtype = getattr(torch, dtype_name)
    max_new_tokens = args.max_new_tokens or (WHISPER_MAX_NEW_TOKENS if family == "whisper" else None)

    print(f"[run] {args.model} ({family}, lang={lang}) on {DATASET_ID}/{args.config}:{SPLIT} "
          f"device={device} dtype={dtype_name} streaming={streaming}")
    ds, n_full = load_fleurs(args.config, args.revision, args.max_samples, streaming)

    t_load = time.time()
    asr = MODEL_CLASSES[family](args.model, lang, device, dtype, args.num_beams, max_new_tokens)
    t_model = time.time()

    hyps, refs, ids, paths_col, durations = [], [], [], [], []
    for rows in batched(iter(ds), args.batch_size):
        arrays = [decode_audio(r["audio"]) for r in rows]
        out = asr(arrays)
        assert len(out) == len(rows)
        hyps.extend(str(h) for h in out)
        refs.extend(r[TEXT_COLUMN] for r in rows)
        ids.extend(int(r["id"]) for r in rows)
        paths_col.extend(os.path.basename(r.get("path") or "") for r in rows)
        durations.extend(len(a) / SAMPLING_RATE for a in arrays)
        print(f"[run] {len(hyps)} done ({time.time() - t_model:.1f}s)", flush=True)
    t_inf = time.time()

    write_string_list(paths["hyps"], hyps)
    write_string_list(paths["refs"], refs)
    assert len(load_string_list(paths["hyps"])) == len(load_string_list(paths["refs"])) == len(hyps)

    meta = {
        "model_id": args.model,
        "model_revision": _hub_sha(args.model, None, "model"),
        "family": family,
        "dataset_id": DATASET_ID,
        "dataset_revision_requested": args.revision,
        "dataset_revision_resolved": _hub_sha(DATASET_ID, args.revision, "dataset"),
        "dataset_loader": (f"datasets.load_dataset('{DATASET_ID}', '{args.config}', "
                           f"split='{SPLIT}', revision=<requested>, streaming={streaming}); "
                           "native parquet (parquet-data/<config>/<split>-*.parquet); "
                           "Audio(decode=False) + soundfile, librosa resample to 16 kHz"),
        "dataset_name": dataset_name(args.config),
        "config": args.config,
        "split": SPLIT,
        "text_column": TEXT_COLUMN,
        "n": len(hyps),
        "n_full_split": n_full,
        "max_samples": args.max_samples,
        "complete": (n_full is not None and len(hyps) == n_full),
        "utterance_ids": ids,
        "audio_files": paths_col,
        "audio_seconds_total": round(sum(durations), 2),
        "audio_seconds_max": round(max(durations), 2) if durations else None,
        "language_forced": lang,
        "task": "transcribe" if family == "whisper" else ("asr_ctc" if family == "mms" else "s2tt (tgt=src)"),
        "generation": {**asr.gen, "batch_size": args.batch_size},
        "whisper_longform_utterances": getattr(asr, "n_longform", None),
        "seed": args.seed,
        "device": device,
        "device_name": (torch.cuda.get_device_name(torch.device(device))
                        if device.startswith("cuda") else platform.processor() or "cpu"),
        "dtype": dtype_name,
        "versions": _versions(),
        "repo_commit": _git_rev(),
        "command": " ".join([os.path.basename(sys.argv[0])] + (argv if argv is not None else sys.argv[1:])),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "wall_time_s": {"total": round(t_inf - t_start, 2), "data_setup": round(t_load - t_start, 2),
                        "model_load": round(t_model - t_load, 2),
                        "inference": round(t_inf - t_model, 2)},
        "outputs": paths,
    }
    if not args.no_score:
        meta["quick_score"] = quick_score(refs, hyps)
        print(f"[score] {json.dumps(meta['quick_score'], ensure_ascii=False)}")
    _atomic_write_json(paths["meta"], meta, ensure_ascii=False, indent=2)
    print(f"[out] {paths['hyps']}\n[out] {paths['refs']}\n[out] {paths['meta']}")
    return meta


if __name__ == "__main__":
    main()
