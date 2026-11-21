"""Tests for the pure-Python parts of src/run_fleurs.py (no torch, no network)."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import run_fleurs as rf  # noqa: E402


def test_module_imports_without_torch():
    # Heavy deps are imported lazily inside functions only.
    src = open(rf.__file__, encoding="utf-8").read()
    top = src.split("# Pure-Python helpers")[0]
    assert "import torch" not in top and "from datasets" not in top


def test_lang_codes():
    assert rf.lang_code("whisper", "ur_pk") == "urdu"
    assert rf.lang_code("whisper", "sd_in") == "sindhi"
    assert rf.lang_code("mms", "ur_pk") == "urd-script_arabic"
    assert rf.lang_code("mms", "sd_in") == "snd"
    assert rf.lang_code("seamlessm4t", "ur_pk") == "urd"
    assert rf.lang_code("seamless", "sd_in") == "snd"          # alias
    with pytest.raises(ValueError):
        rf.lang_code("whisper", "hi_in")
    with pytest.raises(ValueError):
        rf.lang_code("wav2vec", "ur_pk")


def test_family_inference_and_aliases():
    assert rf.infer_family("openai/whisper-large-v3") == "whisper"
    assert rf.infer_family("facebook/mms-1b-all") == "mms"
    assert rf.infer_family("facebook/seamless-m4t-v2-large") == "seamlessm4t"
    assert rf.infer_family("facebook/hf-seamless-m4t-medium") == "seamlessm4t"
    assert rf.canonical_family("Seamless") == "seamlessm4t"
    with pytest.raises(ValueError):
        rf.infer_family("someone/conformer-ctc")


def test_output_paths_match_wws_layout(tmp_path):
    p = rf.output_paths(str(tmp_path), "whisper", "openai/whisper-tiny", "ur_pk")
    assert p["hyps"] == os.path.join(str(tmp_path), "outputs", "whisper", "whisper-tiny",
                                     "fleurs-ur_pk.json")
    assert p["meta"].endswith(os.path.join("whisper-tiny", "fleurs-ur_pk.meta.json"))
    assert p["refs"] == os.path.join(str(tmp_path), "refs", "fleurs-ur_pk-test.json")
    p = rf.output_paths("r", "seamless", "facebook/seamless-m4t-v2-large", "sd_in")
    assert p["hyps"] == os.path.join("r", "outputs", "seamlessm4t", "seamless-m4t-v2-large",
                                     "fleurs-sd_in.json")
    assert rf.model_basename("local/dir/my-model/") == "my-model"


def test_string_list_writer_roundtrip_and_format(tmp_path):
    hyps = [" ایک دو", "", "abc ٹیسٹ"]
    path = tmp_path / "outputs" / "whisper" / "m" / "fleurs-ur_pk.json"
    rf.write_string_list(str(path), hyps)
    raw = path.read_text(encoding="utf-8")
    assert raw.startswith('["') and "\\u06cc" in raw   # json.dump default, like WWS inference.py
    assert json.loads(raw) == hyps
    assert rf.load_string_list(str(path)) == hyps
    assert not os.path.exists(str(path) + ".tmp")
    with pytest.raises(TypeError):
        rf.write_string_list(str(path), ["ok", None])


def test_load_string_list_rejects_non_wws_format(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps([{"id": "ایک"}]), encoding="utf-8")   # WWS 'arl' dict format
    with pytest.raises(ValueError):
        rf.load_string_list(str(p))


def test_batched_keeps_order():
    assert list(rf.batched(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    with pytest.raises(ValueError):
        list(rf.batched([1], 0))
