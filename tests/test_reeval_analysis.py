"""Tests for src/reeval_analysis.py (synthetic arrays only; no results)."""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import reeval_analysis as ra  # noqa: E402


def _d(we, wl, ce=None, cl=None):
    we, wl = np.array(we, float), np.array(wl, float)
    return {"we": we, "wl": wl, "ce": we if ce is None else np.array(ce, float),
            "cl": wl if cl is None else np.array(cl, float)}


def test_metric_point_estimates():
    d = _d([1, 3], [2, 10])
    assert ra.metric(d, "utt_wer") == pytest.approx(100 * (0.5 + 0.3) / 2)
    assert ra.metric(d, "corpus_wer") == pytest.approx(100 * 4 / 12)
    assert ra.metric(d, "corpus_wer", mask=np.array([True, False])) == pytest.approx(50)


def test_metric_bootstrap_matches_point_on_identity_resample():
    d = _d([1, 3, 0], [2, 10, 5])
    idx = np.array([[0, 1, 2]])
    for name in ra.METRICS:
        assert ra.metric(d, name, idx)[0] == pytest.approx(ra.metric(d, name))


def test_paired_difference_of_identical_models_is_zero():
    rng = np.random.default_rng(0)
    we, wl = rng.integers(0, 5, 50), rng.integers(5, 20, 50)
    data = {c: {"a": _d(we, wl), "b": _d(we, wl)} for c in ra.CONDITIONS}
    rows = ra.pairwise(data, ra.bootstrap_indices(50, 200))
    assert all(r["delta"] == 0 and r["ci_low"] == 0 and r["ci_high"] == 0 for r in rows)


def test_paired_difference_detects_consistent_gap():
    wl = np.full(100, 10)
    data = {c: {"good": _d(np.full(100, 1), wl), "bad": _d(np.full(100, 3), wl)}
            for c in ra.CONDITIONS}
    rows = ra.pairwise(data, ra.bootstrap_indices(100, 200))
    r = next(r for r in rows if r["ranking"] == "corpus_wer" and r["metric"] == "corpus_wer")
    assert (r["model_upper"], r["model_lower"]) == ("good", "bad")
    assert r["delta"] == pytest.approx(20) and r["ci_includes_0"] is False


def test_bucket_masks_partition():
    length = np.array([1, 5, 6, 15, 16, 30, 31, 50, 51, 140])
    for scheme in ra.SCHEMES:
        masks = ra.bucket_masks(length, scheme)
        assert (sum(m.astype(int) for m in masks.values()) == 1).all()
    assert ra.bucket_masks(length, "spec")["<=5"].sum() == 2


def test_standardisation_removes_pure_length_effect():
    # error rate depends only on length bucket, flagged utts are all long:
    # raw comparison shows a gap, standardised comparison shows none.
    length = np.array([10] * 50 + [40] * 50)
    flags = np.array([False] * 50 + [False] * 25 + [True] * 25)
    we = np.where(length == 10, 5, 4)                       # 50% short, 10% long
    d = _d(we, length)
    masks = ra.bucket_masks(length, "fine")
    raw_gap = ra.metric(d, "corpus_wer", mask=flags) - ra.metric(d, "corpus_wer", mask=~flags)
    assert raw_gap < 0
    weights = {"31-50": 1.0}                                # only bucket with both groups
    std = (ra.standardised(d, "corpus_wer", masks, weights, flags)
           - ra.standardised(d, "corpus_wer", masks, weights, ~flags))
    assert std == pytest.approx(0)
