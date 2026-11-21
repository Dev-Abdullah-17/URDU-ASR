"""Tests for src/reeval_wws.py helpers (synthetic data only; no results)."""

import json
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import reeval_wws as rw  # noqa: E402


def test_wws_clean_hyp_matches_their_logic():
    chars = set("آپ کیسے ہیں")
    # chars outside the set dropped, #tags removed, whitespace collapsed
    assert rw.wws_clean_hyp("آپ   کیسے؟ ہیں abc", chars) == "آپ کیسے ہیں"
    assert rw.wws_clean_hyp("آپ #ٹیگ ہیں", chars | {"#", "ٹ", "گ"}) == "آپ ہیں"


def test_edit_counts_and_corpus_vs_utt_average():
    refs = ["آپ کیسے ہیں", "ٹھیک"]
    hyps = ["آپ کیسے ہو", "ٹھیک ہے"]
    we, wl = rw.edit_counts(refs, hyps, "word")
    assert list(we) == [1, 1] and list(wl) == [3, 1]
    ce, cl = rw.edit_counts(refs, hyps, "char")
    mask = np.ones(2, bool)
    s = rw.score(we, wl, ce, cl, mask, rw.bootstrap_indices(2, 50))
    assert s["corpus_wer"] == pytest.approx(100 * 2 / 4)
    assert s["utt_wer"] == pytest.approx(100 * (1 / 3 + 1) / 2)   # differs from corpus
    lo, hi = s["corpus_wer_ci"]
    assert lo <= hi


def test_bootstrap_deterministic():
    a = rw.bootstrap_indices(471)
    b = rw.bootstrap_indices(471)
    assert a.shape == (1000, 471) and (a == b).all()


def test_kendall_tau_and_ranks():
    a = {"m1": 10.0, "m2": 20.0, "m3": 30.0}
    assert rw.tau(a, a) == pytest.approx(1.0)
    assert rw.tau(a, {"m1": 30.0, "m2": 20.0, "m3": 10.0}) == pytest.approx(-1.0)
    assert rw.ranks(a) == {"m1": 1, "m2": 2, "m3": 3}


def test_conditions_cumulative_and_symmetric():
    conds = rw.build_conditions(set("abc "), "as_released~")
    names = [c.name for c in conds]
    assert names[:3] == ["as_released~", "raw", "N1_unicode"]
    assert "N8_latin_drop" in names and "N7+hamza_merge" in names
    n7 = next(c for c in conds if c.name == "N7_numwords")
    n8 = next(c for c in conds if c.name == "N8_latin_drop")
    assert n7.ref_fn is n7.hyp_fn                     # same normalizer both sides
    assert n7.ref_fn("کل 2 Meeting، ہے") == "کل دو meeting ہے"
    assert n8.ref_fn("کل 2 Meeting، ہے") == "کل دو ہے"
    as_rel = conds[0]
    assert as_rel.ref_fn("Ref، raw") == "Ref، raw"    # reference untouched


def test_prepare_dataset_branching(monkeypatch):
    import datasets

    class Split(list):
        num_rows = property(len)

    calls = {}
    monkeypatch.setattr(datasets, "load_dataset",
                        lambda name: {"validation": Split(range(471))})
    monkeypatch.setattr(datasets, "concatenate_datasets",
                        lambda xs: calls.setdefault("concat", xs))
    assert len(rw.prepare_dataset_like_wws("urdu-asr/csalt-voice")) == 471
    assert "concat" not in calls

    monkeypatch.setattr(datasets, "load_dataset",
                        lambda name: {"train": Split([1]), "test": Split([2]),
                                      "validation": Split([3])})
    out = rw.prepare_dataset_like_wws("x")
    assert out == [Split([1]), Split([2])]            # train then test


def test_main_end_to_end_on_synthetic_data(tmp_path, monkeypatch):
    """Exercise the whole pipeline on synthetic strings (not real data)."""
    base = ["کل میٹنگ ہے", "آپ کیسے ہیں", "یہ meeting ہے", "میں 25 سال کا ہوں"]
    refs = [base[i % 4] + f" {i}" for i in range(rw.N_UTTERANCES)]
    wws = tmp_path / "wws"
    for k in range(rw.N_MODELS):
        d = wws / "outputs" / "fam" / f"model{k:02d}"
        d.mkdir(parents=True)
        hyps = [r if (i + k) % (k + 2) else r.split()[0] for i, r in enumerate(refs)]
        (d / "csalt-voice.json").write_text(json.dumps(hyps, ensure_ascii=False))
    rj = tmp_path / "refs.json"
    rj.write_text(json.dumps(refs, ensure_ascii=False))
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["reeval_wws.py", "--wws-dir", str(wws),
                                      "--refs-json", str(rj), "--out-dir", str(out)])
    rw.main()
    for f in ("reeval_table.csv", "reeval_table.md", "reeval_per_utt.csv",
              "reeval_codeswitch_flags.csv", "reeval_meta.json"):
        assert (out / f).exists(), f
    import csv
    rows = list(csv.DictReader(open(out / "reeval_table.csv", encoding="utf-8")))
    subs = {r["subset"] for r in rows}
    assert subs == {"overall", "code_switched", "monolingual", "code_switched_latin_only"}
    t = [r for r in rows if r["subset"] == "overall" and r["condition"] == "as_released~"
         and r["metric"] == "utt_wer"]
    assert len(t) == rw.N_MODELS and all(float(r["kendall_tau_vs_as_released"]) == 1.0 for r in t)


def test_label_template_sample_is_deterministic():
    from make_cs_label_template import sample_ids
    a = sample_ids()
    assert a == sample_ids() and len(a) == 100 and len(set(a)) == 100
    assert a == sorted(a) and 0 <= a[0] and a[-1] < 471


def test_every_n_condition_strips_disfluency_tags_raw_does_not():
    conds = rw.build_conditions(set("abc #"), "as_released~")
    h = "#um کل ملتے ہیں"
    for c in conds:
        if c.name.startswith("N"):
            assert "um" not in c.hyp_fn(h) and c.hyp_fn(h) == c.ref_fn(h), c.name
    raw = next(c for c in conds if c.name == "raw")
    assert raw.hyp_fn(h) == h and raw.ref_fn(h) == h
