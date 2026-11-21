"""Property-based (hypothesis) and edge-case tests for the metric code in
src/reeval_wws.py and src/reeval_analysis.py (synthetic data only).

Properties found to be false are kept as xfail(strict=True) with the minimal
counterexample.
"""

import os
import sys
import warnings

import numpy as np
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from hypothesis.extra import numpy as hnp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import reeval_analysis as ra  # noqa: E402
import reeval_wws as rw  # noqa: E402
from normalize_urdu import UrduNormalizer  # noqa: E402

FAST = settings(max_examples=100, deadline=None,
                suppress_health_check=[HealthCheck.too_slow])

URDU_LETTERS = "ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھءیےآئؤ"
ALPHABET = (URDU_LETTERS + "يكهأ" + "0123456789۱۲۳" + "َِّ"
            + "​‌" + "۔،؟.,!#" + "abcXY" + " \t\n")
word = st.text(st.sampled_from(URDU_LETTERS + "abc"), min_size=1, max_size=6)
sentence = st.lists(word, min_size=1, max_size=8).map(" ".join)   # space-separated
raw_text = st.text(st.sampled_from(ALPHABET), max_size=40)


def levenshtein(a: list, b: list) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


@st.composite
def per_utt(draw, min_n=1, max_n=25, min_wl=1):
    """Per-utterance arrays like reeval_per_utt.csv: errors and ref lengths."""
    n = draw(st.integers(min_n, max_n))
    ints = lambda lo, hi: hnp.arrays(np.float64, n, elements=st.integers(lo, hi))  # noqa: E731
    return {"we": draw(ints(0, 30)), "wl": draw(ints(min_wl, 20)),
            "ce": draw(ints(0, 90)), "cl": draw(ints(max(min_wl, 1), 80))}


# --------------------------------------------------------------------------- #
# 2. build_conditions: identical ref/hyp function, raw ref only for as_released
# --------------------------------------------------------------------------- #

EXPECTED_NAMES = ["raw", "N1_unicode", "N2_punct", "N3_lower", "N4_confusables",
                  "N5_diacritics", "N6_digits", "N7_numwords", "N7+hamza_merge",
                  "N8_latin_drop"]


@pytest.mark.parametrize("label", ["as_released", "as_released~"])
def test_condition_names_and_order(label):
    conds = rw.build_conditions(set("abc "), label)
    assert [c.name for c in conds] == [label] + EXPECTED_NAMES


@pytest.mark.parametrize("label", ["as_released", "as_released~"])
def test_same_function_object_for_ref_and_hyp_except_as_released(label):
    for c in rw.build_conditions(set("abc "), label):
        if c.name == label:
            assert c.ref_fn is not c.hyp_fn
        else:
            assert c.ref_fn is c.hyp_fn, c.name


@FAST
@given(chars_src=raw_text, xs=st.lists(raw_text, min_size=1, max_size=5))
def test_conditions_apply_identical_function_to_ref_and_hyp(chars_src, xs):
    chars = set(chars_src) | {" "}
    for label in ("as_released", "as_released~"):
        for c in rw.build_conditions(chars, label):
            for x in xs:
                if c.name == label:
                    # by design: reference raw, hypothesis cleaned
                    assert c.ref_fn(x) is x
                    assert c.hyp_fn(x) == rw.wws_clean_hyp(x, chars)
                else:
                    assert c.ref_fn(x) == c.hyp_fn(x), c.name


def test_as_released_leaves_reference_raw_but_cleans_hypothesis():
    chars = set("آپ کیسے ہیں")
    c = rw.build_conditions(chars, "as_released~")[0]
    s = "آپ   کیسے؟ ہیں #tag abc"
    assert c.ref_fn(s) == s                        # untouched, punctuation and all
    assert c.hyp_fn(s) == "آپ کیسے ہیں"


def test_normalizer_steps_are_cumulative():
    conds = {c.name: c.ref_fn for c in rw.build_conditions(set(), "x")}
    fields = ["map_confusables", "merge_hamza_madda", "strip_diacritics",
              "normalize_digits", "digits_to_words", "remove_punct", "lower_latin",
              "latin_tokens", "collapse_whitespace"]
    prev = None
    for name, _, step in rw._STEPS:
        cfg = {f: getattr(conds[name], f) for f in fields}
        if prev is not None:
            changed = {f for f in fields if cfg[f] != prev[f]}
            assert changed == set(step), name
        prev = cfg
    hamza, n7 = conds["N7+hamza_merge"], conds["N7_numwords"]
    assert hamza.merge_hamza_madda and not n7.merge_hamza_madda
    assert {f: getattr(hamza, f) for f in fields if f != "merge_hamza_madda"} == \
           {f: getattr(n7, f) for f in fields if f != "merge_hamza_madda"}
    assert conds["N8_latin_drop"].latin_tokens == "drop"
    assert conds["N7_numwords"].latin_tokens == "keep"


@FAST
@given(refs=st.lists(raw_text, min_size=1, max_size=6), data=st.data())
def test_scoring_pipeline_never_mutates_inputs(refs, data):
    hyps = data.draw(st.lists(raw_text, min_size=len(refs), max_size=len(refs)))
    refs0, hyps0 = list(refs), list(hyps)
    chars = set("".join(refs)) | {" "}
    boot = rw.bootstrap_indices(len(refs), 20)
    for c in rw.build_conditions(chars, "as_released~"):
        r_norm = [c.ref_fn(r) for r in refs]
        nonempty = np.array([bool(r.strip()) for r in r_norm])
        rr = [r if k else "x" for r, k in zip(r_norm, nonempty)]
        rr0 = list(rr)
        h_norm = [c.hyp_fn(h) for h in hyps]
        h_norm0 = list(h_norm)
        we, wl = rw.edit_counts(rr, h_norm, "word")
        ce, cl = rw.edit_counts(rr, h_norm, "char")
        arrays0 = [a.copy() for a in (we, wl, ce, cl, nonempty, boot)]
        if nonempty.any():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                rw.score(we, wl, ce, cl, nonempty, boot)
        assert rr == rr0 and h_norm == h_norm0
        for a, a0 in zip((we, wl, ce, cl, nonempty, boot), arrays0):
            assert np.array_equal(a, a0)
    assert refs == refs0 and hyps == hyps0


# --------------------------------------------------------------------------- #
# wws_clean_hyp
# --------------------------------------------------------------------------- #

@FAST
@given(h=raw_text, chars_src=raw_text)
def test_wws_clean_hyp_invariants(h, chars_src):
    chars = set(chars_src) | {" "}
    y = rw.wws_clean_hyp(h, chars)
    assert set(y) <= chars
    assert y == y.strip() and "  " not in y
    assert not any(t.startswith("#") and len(t) > 1 for t in y.split())
    assert rw.wws_clean_hyp(y, chars) == y          # idempotent when " " in chars


def test_wws_clean_hyp_edge_cases():
    assert rw.wws_clean_hyp("", set("ab ")) == ""
    assert rw.wws_clean_hyp("abc", set()) == ""
    assert rw.wws_clean_hyp("a #b c", set("abc #")) == "a c"
    assert rw.wws_clean_hyp("a # c", set("ac #")) == "a # c"   # bare '#' is not a tag


# --------------------------------------------------------------------------- #
# edit_counts
# --------------------------------------------------------------------------- #

@FAST
@given(xs=st.lists(raw_text.filter(lambda s: s.strip()), min_size=1, max_size=6))
def test_wer_and_cer_of_identical_strings_is_zero(xs):
    for unit in ("word", "char"):
        errs, lens = rw.edit_counts(xs, xs, unit)
        assert not errs.any()
        assert (lens > 0).all()


@FAST
@given(pairs=st.lists(st.tuples(sentence, sentence), min_size=1, max_size=6))
def test_word_errors_equal_levenshtein_and_lengths_equal_ref_words(pairs):
    refs, hyps = [p[0] for p in pairs], [p[1] for p in pairs]
    errs, lens = rw.edit_counts(refs, hyps, "word")
    for e, n, r, h in zip(errs, lens, refs, hyps):
        assert e == levenshtein(r.split(), h.split())
        assert n == len(r.split())
    errs_rev, _ = rw.edit_counts(hyps, refs, "word")
    assert np.array_equal(errs, errs_rev)          # edit distance is symmetric


@FAST
@given(pairs=st.lists(st.tuples(sentence, sentence), min_size=1, max_size=6))
def test_char_errors_equal_levenshtein(pairs):
    refs, hyps = [p[0] for p in pairs], [p[1] for p in pairs]
    errs, lens = rw.edit_counts(refs, hyps, "char")
    for e, n, r, h in zip(errs, lens, refs, hyps):
        assert e == levenshtein(list(r), list(h))
        assert n == len(r)


def test_edit_counts_empty_hypothesis_is_all_deletions():
    errs, lens = rw.edit_counts(["آپ کیسے ہیں"], [""], "word")
    assert errs[0] == lens[0] == 3


@pytest.mark.xfail(strict=True, reason=(
    "The 'raw' condition is documented as 'whitespace split', but jiwer splits "
    "only on ' ' (and collapses runs of 2+ whitespace): edit_counts(['آپ\\tکیسے'], "
    "['آپ کیسے'], 'word') -> errors [2.0], ref words [1.0]; with '\\t\\t' it is 0 "
    "errors. Inconsistent tokenisation of raw text containing tabs/newlines/NBSP."))
def test_raw_condition_tokenises_on_any_whitespace():
    raw = next(c for c in rw.build_conditions(set(), "x") if c.name == "raw")
    r, h = raw.ref_fn("آپ\tکیسے"), raw.hyp_fn("آپ کیسے")
    errs, lens = rw.edit_counts([r], [h], "word")
    assert errs[0] == 0 and lens[0] == 2


# --------------------------------------------------------------------------- #
# score (reeval_wws)
# --------------------------------------------------------------------------- #

@st.composite
def per_utt_with_mask(draw, **kw):
    d = draw(per_utt(**kw))
    n = len(d["we"])
    mask = draw(hnp.arrays(bool, n))
    assume(mask.any())
    return d, mask


@FAST
@given(dm=per_utt_with_mask(), seed=st.integers(0, 2**16))
def test_score_point_estimates_match_definitions(dm, seed):
    d, mask = dm
    boot = rw.bootstrap_indices(len(mask), 30, seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        s = rw.score(d["we"], d["wl"], d["ce"], d["cl"], mask, boot)
    assert s["n"] == mask.sum()
    assert s["corpus_wer"] == pytest.approx(100 * d["we"][mask].sum() / d["wl"][mask].sum())
    assert s["corpus_cer"] == pytest.approx(100 * d["ce"][mask].sum() / d["cl"][mask].sum())
    assert s["utt_wer"] == pytest.approx(100 * np.mean(d["we"][mask] / d["wl"][mask]))


@FAST
@given(d=per_utt(), seed=st.integers(0, 2**16))
def test_score_cis_are_ordered_and_finite_for_full_mask(d, seed):
    mask = np.ones(len(d["we"]), bool)
    s = rw.score(d["we"], d["wl"], d["ce"], d["cl"], mask, rw.bootstrap_indices(len(mask), 50, seed))
    for k in ("utt_wer", "corpus_wer", "corpus_cer"):
        lo, hi = s[k + "_ci"]
        assert np.isfinite(lo) and np.isfinite(hi) and lo <= hi


@FAST
@given(n=st.integers(1, 25), length=st.integers(1, 20), data=st.data(), seed=st.integers(0, 999))
def test_utt_avg_equals_corpus_wer_when_ref_lengths_equal(n, length, data, seed):
    """Holds (up to float rounding) for point estimates and for every bootstrap
    resample, in both modules, when every *scored* reference (wl, i.e. after
    normalization) has the same length. It does not extend to CER."""
    we = data.draw(hnp.arrays(np.float64, n, elements=st.integers(0, 3 * length)))
    wl = np.full(n, float(length))
    mask = data.draw(hnp.arrays(bool, n))
    assume(mask.any())
    boot = rw.bootstrap_indices(n, 40, seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        s = rw.score(we, wl, we, wl, mask, boot)
        d = {"we": we, "wl": wl, "ce": we, "cl": wl}
        bu = ra.metric(d, "utt_wer", boot, mask)
        bc = ra.metric(d, "corpus_wer", boot, mask)
    assert s["utt_wer"] == pytest.approx(s["corpus_wer"])
    assert np.allclose(s["utt_wer_ci"], s["corpus_wer_ci"], equal_nan=True)  # NaN: see xfail below
    assert ra.metric(d, "utt_wer", mask=mask) == pytest.approx(ra.metric(d, "corpus_wer", mask=mask))
    assert np.allclose(bu, bc, equal_nan=True)


def test_utt_avg_differs_from_corpus_when_lengths_differ():
    d = {"we": np.array([1.0, 1.0]), "wl": np.array([1.0, 9.0])}
    d["ce"], d["cl"] = d["we"], d["wl"]
    assert ra.metric(d, "utt_wer") == pytest.approx(100 * (1 + 1 / 9) / 2)
    assert ra.metric(d, "corpus_wer") == pytest.approx(100 * 2 / 10)


@pytest.mark.xfail(strict=True, reason=(
    "BUG reeval_wws.py:256-260 (+ ci() at 238-240): if any bootstrap resample "
    "contains no utterance of the subset, b_n == 0 / wl sum == 0 gives NaN and "
    "np.percentile propagates it, so the whole CI is (nan, nan). Minimal: n=471, "
    "mask with a single True, seed-42 N_BOOT resamples -> utt_wer_ci == (nan, nan). "
    "Hits small subsets (e.g. code_switched_latin_only). reeval_analysis.pct_ci "
    "drops non-finite resamples instead."))
def test_score_ci_finite_for_small_subset():
    n = rw.N_UTTERANCES
    we, wl = np.ones(n), np.full(n, 5.0)
    mask = np.zeros(n, bool)
    mask[0] = True
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        s = rw.score(we, wl, we, wl, mask, rw.bootstrap_indices(n))
    assert all(np.isfinite(s[k + "_ci"]).all() for k in ("utt_wer", "corpus_wer", "corpus_cer"))


@FAST
@given(dm=per_utt_with_mask())
def test_score_agrees_with_analysis_metric(dm):
    d, mask = dm
    boot = rw.bootstrap_indices(len(mask), 10)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        s = rw.score(d["we"], d["wl"], d["ce"], d["cl"], mask, boot)
    for k in ra.METRICS:
        assert s[k] == pytest.approx(ra.metric(d, k, mask=mask))


@pytest.mark.xfail(strict=True, reason=(
    "Latent inconsistency: for an utterance with 0 reference words, "
    "reeval_wws.score (line 248) counts per-utterance WER as word_err (divides "
    "by 1) while reeval_analysis.metric (line 101) counts it as 0. we=[2], wl=[0] "
    "-> score utt_wer 200.0 vs metric 0.0. Not reached by main() today because "
    "empty references are masked out."))
def test_score_and_metric_agree_on_empty_reference():
    d = {"we": np.array([2.0]), "wl": np.array([0.0]),
         "ce": np.array([2.0]), "cl": np.array([1.0])}
    mask = np.ones(1, bool)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        s = rw.score(d["we"], d["wl"], d["ce"], d["cl"], mask, rw.bootstrap_indices(1, 5))
    assert s["utt_wer"] == pytest.approx(ra.metric(d, "utt_wer"))


# --------------------------------------------------------------------------- #
# bootstrap_indices, ranks, tau
# --------------------------------------------------------------------------- #

@settings(max_examples=50, deadline=None)
@given(n=st.integers(1, 500), n_boot=st.integers(1, 200), seed=st.integers(0, 2**32 - 1))
def test_bootstrap_deterministic_shape_and_range(n, n_boot, seed):
    a = rw.bootstrap_indices(n, n_boot, seed)
    b = rw.bootstrap_indices(n, n_boot, seed)
    assert np.array_equal(a, b)
    assert a.shape == (n_boot, n)
    assert a.min() >= 0 and a.max() < n


def test_bootstrap_default_is_seed_42_and_shared_by_analysis():
    assert np.array_equal(rw.bootstrap_indices(471), rw.bootstrap_indices(471, rw.N_BOOT, 42))
    assert ra.bootstrap_indices is rw.bootstrap_indices
    assert (ra.N_BOOT, ra.SEED) == (rw.N_BOOT, rw.SEED) == (1000, 42)
    assert not np.array_equal(rw.bootstrap_indices(471, 50, 1), rw.bootstrap_indices(471, 50, 2))


model_vals = st.dictionaries(
    st.text("abcdefgh-", min_size=1, max_size=6),
    st.floats(0, 300, allow_nan=False) | st.sampled_from([10.0, 20.0]),
    min_size=1, max_size=17)


@FAST
@given(vals=model_vals)
def test_ranks_are_a_consistent_permutation(vals):
    r = rw.ranks(vals)
    assert sorted(r.values()) == list(range(1, len(vals) + 1))
    for a in vals:
        for b in vals:
            if vals[a] < vals[b] or (vals[a] == vals[b] and a < b):
                assert r[a] < r[b]


@FAST
@given(vals=model_vals)
def test_ranks_invariant_under_monotone_transform(vals):
    assert rw.ranks(vals) == rw.ranks({m: 2 * v for m, v in vals.items()})  # exact in floating point


@FAST
@given(vals=model_vals)
def test_tau_self_and_reversed(vals):
    assume(len(set(vals.values())) >= 2)
    neg = {m: -v for m, v in vals.items()}
    assert rw.tau(vals, vals) == pytest.approx(1.0)
    assert rw.tau(vals, neg) == pytest.approx(-1.0)
    other = {m: (v * 7919) % 13 for m, v in vals.items()}
    assume(len(set(other.values())) >= 2)
    assert rw.tau(vals, other) == pytest.approx(rw.tau(other, vals))
    assert -1 <= rw.tau(vals, other) <= 1


def test_tau_constant_ranking_is_nan():
    assert np.isnan(rw.tau({"a": 1.0, "b": 1.0}, {"a": 1.0, "b": 2.0}))


# --------------------------------------------------------------------------- #
# reeval_analysis: metric, pairwise, bucket_masks, standardised
# --------------------------------------------------------------------------- #

@FAST
@given(d=per_utt(), seed=st.integers(0, 999))
def test_metric_bootstrap_row_equals_point_on_resampled_data(d, seed):
    idx = rw.bootstrap_indices(len(d["we"]), 5, seed)
    for name in ra.METRICS:
        boot_vals = ra.metric(d, name, idx)
        for row, v in zip(idx, boot_vals):
            resampled = {k: a[row] for k, a in d.items()}
            assert v == pytest.approx(ra.metric(resampled, name))


@FAST
@given(d=per_utt())
def test_metric_corpus_wer_is_errors_over_ref_words(d):
    assert ra.metric(d, "corpus_wer") == pytest.approx(100 * d["we"].sum() / d["wl"].sum())
    assert ra.metric(d, "corpus_cer") == pytest.approx(100 * d["ce"].sum() / d["cl"].sum())


@FAST
@given(d=per_utt(), seed=st.integers(0, 999), data=st.data())
def test_paired_self_difference_is_exactly_zero(d, seed, data):
    n = len(d["we"])
    mask = data.draw(hnp.arrays(bool, n))
    boot = rw.bootstrap_indices(n, 50, seed)
    for name in ra.METRICS:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            diff = ra.metric(d, name, boot, mask) - ra.metric(dict(d), name, boot, mask)
        assert (diff[np.isfinite(diff)] == 0).all()


def _data_for(models: dict) -> dict:
    return {c: {m: {k: v.copy() for k, v in d.items()} for m, d in models.items()}
            for c in ra.CONDITIONS}


@FAST
@given(a=per_utt(min_n=3, max_n=15), data=st.data())
def test_pairwise_model_vs_its_copy_is_zero(a, data):
    n = len(a["we"])
    b = data.draw(per_utt(min_n=n, max_n=n))
    rows = ra.pairwise(_data_for({"m": a, "m_copy": a, "other": b}),
                       rw.bootstrap_indices(n, 100))
    self_rows = [r for r in rows if {r["model_upper"], r["model_lower"]} == {"m", "m_copy"}]
    # the copy ties exactly, so it is adjacent in every ranking
    assert len(self_rows) == len(ra.CONDITIONS) * len(ra.METRICS) ** 2
    for r in self_rows:
        assert r["delta"] == 0 and r["ci_low"] == 0 and r["ci_high"] == 0
        assert r["ci_includes_0"] and r["p_boot_delta_le_0"] == 1.0


@FAST
@given(ms=st.lists(per_utt(min_n=6, max_n=6), min_size=2, max_size=5))
def test_pairwise_rows_consistent(ms):
    models = {f"m{i}": d for i, d in enumerate(ms)}
    rows = ra.pairwise(_data_for(models), rw.bootstrap_indices(6, 60))
    assert len(rows) == len(ra.CONDITIONS) * len(ra.METRICS) ** 2 * (len(ms) - 1)
    for r in rows:
        assert r["ci_low"] <= r["ci_high"]
        assert r["delta"] == pytest.approx(r["value_lower"] - r["value_upper"], abs=0.011)
        assert 0 <= r["p_boot_delta_le_0"] <= 1
        if r["metric"] == r["ranking"]:
            assert r["value_upper"] <= r["value_lower"]


@settings(max_examples=100, deadline=None)
@given(length=hnp.arrays(np.int64, st.integers(1, 60), elements=st.integers(0, 500)))
def test_bucket_masks_partition_lengths(length):
    for scheme in ra.SCHEMES:
        masks = list(ra.bucket_masks(length, scheme).values())
        total = np.sum(masks, axis=0)
        assert (total == 1).all(), scheme


def test_bucket_masks_boundaries():
    length = np.array([0, 5, 6, 15, 16, 30, 31, 50, 51])
    spec = ra.bucket_masks(length, "spec")
    assert list(length[spec["<=5"]]) == [0, 5]
    assert list(length[spec["6-15"]]) == [6, 15]
    fine = ra.bucket_masks(length, "fine")
    assert list(length[fine["16-30"]]) == [16, 30]
    assert list(length[fine[">50"]]) == [51]


@FAST
@given(n=st.integers(4, 30), rate=st.integers(0, 4), data=st.data())
def test_standardised_constant_rate_returns_that_rate(n, rate, data):
    """If corpus WER is the same r in every bucket, any weights summing to 1
    give r."""
    wl = data.draw(hnp.arrays(np.float64, n, elements=st.integers(1, 20)))
    d = {"we": rate * wl, "wl": wl, "ce": rate * wl, "cl": wl}
    length = data.draw(hnp.arrays(np.int64, n, elements=st.integers(0, 60)))
    masks = ra.bucket_masks(length, "fine")
    used = [b for b, m in masks.items() if m.any()]
    raw_w = data.draw(st.lists(st.floats(0.1, 1), min_size=len(used), max_size=len(used)))
    weights = {b: w / sum(raw_w) for b, w in zip(used, raw_w)}
    group = np.ones(n, bool)
    assert ra.standardised(d, "corpus_wer", masks, weights, group) == pytest.approx(100 * rate)


@FAST
@given(d=per_utt(min_n=4, max_n=20), data=st.data())
def test_standardised_is_weighted_sum_and_self_difference_zero(d, data):
    n = len(d["we"])
    length = data.draw(hnp.arrays(np.int64, n, elements=st.integers(0, 60)))
    flags = data.draw(hnp.arrays(bool, n))
    masks = ra.bucket_masks(length, "spec")
    used = [b for b, m in masks.items() if (m & flags).any()]
    assume(used)
    weights = {b: 1 / len(used) for b in used}
    expected = sum(w * ra.metric(d, "corpus_wer", mask=masks[b] & flags)
                   for b, w in weights.items())
    assert ra.standardised(d, "corpus_wer", masks, weights, flags) == pytest.approx(expected)
    boot = rw.bootstrap_indices(n, 30)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        diff = (ra.standardised(d, "corpus_wer", masks, weights, flags, boot)
                - ra.standardised(d, "corpus_wer", masks, weights, flags, boot))
    assert (diff[np.isfinite(diff)] == 0).all()


def test_pct_ci_ignores_non_finite():
    assert np.isnan(ra.pct_ci(np.array([np.nan, np.inf]))).all()
    lo, hi = ra.pct_ci(np.array([np.nan, 1.0, 1.0, np.inf]))
    assert lo == hi == 1.0
