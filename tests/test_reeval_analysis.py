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


# --- Holm-Bonferroni / bootstrap p-values ------------------------------------

def test_holm_known_values():
    # classic example: p = .01, .04, .03, .005 (m = 4)
    adj = ra.holm([0.01, 0.04, 0.03, 0.005])
    assert adj == pytest.approx([0.03, 0.06, 0.06, 0.02])


def test_holm_monotone_and_capped():
    p = [0.5, 0.001, 0.2, 0.9, 0.04]
    adj = ra.holm(p)
    order = sorted(range(len(p)), key=lambda i: p[i])
    assert all(adj[order[k]] <= adj[order[k + 1]] for k in range(len(p) - 1))
    assert all(a >= q for a, q in zip(adj, p)) and max(adj) <= 1.0


def test_boot_p_two_sided():
    assert ra.boot_p_two_sided(np.zeros(1000)) == 1.0
    assert ra.boot_p_two_sided(np.ones(1000)) == pytest.approx(2 / 1001)
    assert ra.boot_p_two_sided(np.r_[np.ones(900), -np.ones(100)]) == pytest.approx(2 * 101 / 1001)


def test_add_holm_families_are_separate():
    rows = [{"f": "a", "p_boot": 0.01, "_p": 0.01}, {"f": "a", "p_boot": 0.02, "_p": 0.02},
            {"f": "b", "p_boot": 0.01, "_p": 0.01}, {"f": "b", "p_boot": ""}]
    ra.add_holm(rows, ("f",))
    assert [r["family_size"] for r in rows] == [2, 2, 1, ""]
    assert rows[0]["p_holm"] == pytest.approx(0.02) and rows[2]["p_holm"] == pytest.approx(0.01)
    assert rows[3]["p_holm"] == ""


def test_add_holm_uses_unrounded_p():
    # exact p = 10/1001 ~ 0.00999 -> Holm (m=5) 0.04995 < 0.05 (reject);
    # rounding p to 0.0100 first would give 0.0500 (no reject)
    p = 10 / 1001
    rows = [{"f": "a", "p_boot": round(p, 4), "_p": p}] + \
           [{"f": "a", "p_boot": 0.9, "_p": 0.9} for _ in range(4)]
    ra.add_holm(rows, ("f",))
    assert rows[0]["reject_holm_05"] is True
    assert all("_p" not in r and "_p_exact" not in r for r in rows)


def test_add_holm_excludes_untestable():
    rows = [{"f": "a", "p_boot": 0.01, "_p": 0.01},
            {"f": "a", "p_boot": float("nan"), "_p": float("nan")}]
    ra.add_holm(rows, ("f",))
    assert rows[0]["family_size"] == 1 and rows[1]["p_holm"] == "" and rows[1]["p_boot"] == ""
    assert np.isnan(ra.boot_p_two_sided(np.full(10, np.nan)))
