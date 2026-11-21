"""Follow-up analyses on the WER We Stand re-evaluation (needs reeval_wws.py output).

Reads results/reeval_per_utt.csv (local, contains reference text) and writes
aggregate-only tables (no reference text):

1. reeval_pairwise.{csv,md}
   Paired bootstrap of the metric difference between *adjacent* models in each
   ranking (utt_wer, corpus_wer, corpus_cer), for conditions as_released~ and
   N7_numwords. Each resample draws one set of utterance indices and scores
   both models on it (the same 1000 x 471 index matrix, seed 42, that
   reeval_wws.py uses for its CIs). Reports delta = upper - lower model
   (positive = the lower-ranked model is worse), its 95% percentile CI and
   whether the CI includes 0. For each adjacent pair the differences in all
   three metrics are reported, not only the ranking metric.

2. reeval_length_buckets.{csv,md}
   Per model and condition, WER/CER by reference-length bucket (<=5, 6-15,
   >15 words; length = raw reference word count): n utterances, share of
   utterances vs share of reference words (the weights that utterance-averaged
   and corpus-level WER respectively give each bucket), utterance-averaged WER,
   corpus WER and corpus CER within the bucket.

3. reeval_cs_by_length.{csv,md}
   Code-switch flag (extended detector; flagged = method != "none") vs
   unflagged within the same length buckets ("spec" = <=5/6-15/>15, plus a
   "fine" split <=15/16-30/31-50/>50 because few references are short), and a
   length-standardised
   difference: each group's per-bucket corpus WER (CER) is weighted by the
   pooled word share of the bucket (direct standardisation), with a bootstrap
   CI over the same resampled index sets.

    python src/reeval_analysis.py --results-dir results
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict

import numpy as np

from reeval_wws import N_BOOT, SEED, bootstrap_indices

CONDITIONS = ("as_released~", "N7_numwords")
METRICS = ("utt_wer", "corpus_wer", "corpus_cer")
# "spec": the requested buckets. Most references are long (median 27 words;
# only 12 have <=5 words), so "fine" additionally splits the range into
# quartile-like buckets; reported separately and labelled.
SCHEMES = {
    "spec": (("<=5", 0, 5), ("6-15", 6, 15), (">15", 16, 10**9)),
    "fine": (("<=15", 0, 15), ("16-30", 16, 30), ("31-50", 31, 50), (">50", 51, 10**9)),
}
MIN_CELL = 5  # min utterances per group in a bucket for it to enter standardisation


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def load_per_utt(path: str):
    """-> data[cond][model] = dict of arrays (we, wl, ce, cl) indexed by utt_id,
    plus raw reference word counts and cs flags per utt_id."""
    rows = defaultdict(lambda: defaultdict(list))
    raw_len, cs = {}, {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            i = int(r["utt_id"])
            cs[i] = r["cs_method"] != "none"
            if r["condition"] == "raw":
                raw_len[i] = int(r["ref_words"])
            if r["condition"] in CONDITIONS:
                rows[r["condition"]][r["model"]].append(
                    (i, int(r["word_err"]), int(r["ref_words"]),
                     int(r["char_err"]), int(r["ref_chars"])))
    n = max(cs) + 1
    assert sorted(cs) == list(range(n)) and sorted(raw_len) == list(range(n))
    data = {}
    for c, by_model in rows.items():
        data[c] = {}
        for m, lst in by_model.items():
            lst.sort()
            assert [x[0] for x in lst] == list(range(n)), f"{c}/{m}: missing utterances"
            a = np.array([x[1:] for x in lst], dtype=float)
            data[c][m] = {"we": a[:, 0], "wl": a[:, 1], "ce": a[:, 2], "cl": a[:, 3]}
    length = np.array([raw_len[i] for i in range(n)])
    flags = np.array([cs[i] for i in range(n)])
    return data, length, flags


# --------------------------------------------------------------------------- #
# Metric helpers (vectorised over bootstrap rows)
# --------------------------------------------------------------------------- #

def metric(d: dict, name: str, idx=None, mask=None) -> np.ndarray | float:
    """Metric for one model. idx: (B, n) bootstrap indices or None (point
    estimate). mask: boolean (n,) subset applied before aggregation."""
    we, wl, ce, cl = d["we"], d["wl"], d["ce"], d["cl"]
    m = np.ones_like(we, bool) if mask is None else mask
    # empty reference: errors / max(ref_len, 1) (insertions still count), as
    # in reeval_wws.score; main() excludes empty references in any case
    utt = we / np.maximum(wl, 1)
    if idx is None:
        if name == "utt_wer":
            return 100 * utt[m].mean()
        if name == "corpus_wer":
            return 100 * we[m].sum() / wl[m].sum()
        return 100 * ce[m].sum() / cl[m].sum()
    mm = m[idx]
    with np.errstate(divide="ignore", invalid="ignore"):
        if name == "utt_wer":
            return 100 * (utt[idx] * mm).sum(1) / mm.sum(1)
        if name == "corpus_wer":
            return 100 * (we[idx] * mm).sum(1) / (wl[idx] * mm).sum(1)
        return 100 * (ce[idx] * mm).sum(1) / (cl[idx] * mm).sum(1)


ALPHA = 0.05


def boot_p_two_sided(diff: np.ndarray) -> float:
    """Two-sided bootstrap p-value for H0: delta = 0, from the resampled
    differences: 2 * min(#(d<=0)+1, #(d>=0)+1) / (B+1), capped at 1. The +1
    avoids p = 0; with B = 1000 the smallest attainable p is 2/1001."""
    d = diff[np.isfinite(diff)]
    b = len(d)
    if b == 0:
        return float("nan")      # untestable; excluded from Holm families
    lo, hi = (d <= 0).sum() + 1, (d >= 0).sum() + 1
    return float(min(1.0, 2 * min(lo, hi) / (b + 1)))


def holm(pvals: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values (step-down, monotone, capped at 1)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj, running = [0.0] * m, 0.0
    for k, i in enumerate(order):
        running = max(running, min(1.0, (m - k) * pvals[i]))
        adj[i] = running
    return adj


def add_holm(rows: list[dict], family_keys: tuple[str, ...]) -> None:
    """Add p_holm / reject_holm_05 in place; one family per distinct value of
    family_keys among rows that carry a finite p. Holm runs on the unrounded
    p (private key "_p"); p_boot/p_holm are rounded only for output."""
    fams = defaultdict(list)
    for r in rows:
        p = r.pop("_p", None)
        if p is not None and np.isfinite(p):
            r["_p_exact"] = p
            fams[tuple(r[k] for k in family_keys)].append(r)
        elif p is not None:
            r["p_boot"] = ""
    for r in rows:
        r.setdefault("family_size", "")
        r.setdefault("p_holm", "")
        r.setdefault("reject_holm_05", "")
    for fam in fams.values():
        adj = holm([r.pop("_p_exact") for r in fam])
        for r, a in zip(fam, adj):
            r["family_size"] = len(fam)
            r["p_holm"] = round(a, 4)
            r["reject_holm_05"] = a < ALPHA


def pct_ci(x: np.ndarray) -> tuple[float, float]:
    """95% percentile CI over finite resamples (a resample can leave a small
    subset empty -> NaN; callers report how many resamples were usable)."""
    x = x[np.isfinite(x)]
    if not len(x):
        return float("nan"), float("nan")
    lo, hi = np.percentile(x, [2.5, 97.5])
    return float(lo), float(hi)


def bucket_masks(length: np.ndarray, scheme: str) -> dict[str, np.ndarray]:
    return {name: (length >= lo) & (length <= hi) for name, lo, hi in SCHEMES[scheme]}


# --------------------------------------------------------------------------- #
# 1. Pairwise adjacent-model paired bootstrap
# --------------------------------------------------------------------------- #

def pairwise(data, boot) -> list[dict]:
    out = []
    for c in CONDITIONS:
        models = sorted(data[c])
        for rank_metric in METRICS:
            point = {m: metric(data[c][m], rank_metric) for m in models}
            order = sorted(models, key=lambda m: (point[m], m))
            for k in range(len(order) - 1):
                a, b = order[k], order[k + 1]
                for met in METRICS:
                    pa, pb = metric(data[c][a], met), metric(data[c][b], met)
                    diff = metric(data[c][b], met, boot) - metric(data[c][a], met, boot)
                    lo, hi = pct_ci(diff)
                    out.append({
                        "condition": c, "ranking": rank_metric, "rank_upper": k + 1,
                        "model_upper": a, "model_lower": b, "metric": met,
                        "value_upper": round(pa, 2), "value_lower": round(pb, 2),
                        "delta": round(pb - pa, 2), "ci_low": round(lo, 2),
                        "ci_high": round(hi, 2), "ci_includes_0": lo <= 0 <= hi,
                        "p_boot_delta_le_0": round(float((diff <= 0).mean()), 3),
                        "p_boot": round(boot_p_two_sided(diff), 4),
                        "_p": boot_p_two_sided(diff),
                    })
    # one family = the 16 adjacent-pair tests of one metric within one ranking
    add_holm(out, ("condition", "ranking", "metric"))
    return out


# --------------------------------------------------------------------------- #
# 2. Length buckets
# --------------------------------------------------------------------------- #

def length_buckets(data, length) -> list[dict]:
    n_utt, n_words = len(length), length.sum()
    out = []
    for scheme in SCHEMES:
      masks = bucket_masks(length, scheme)
      for c in CONDITIONS:
        for m in sorted(data[c]):
            d = data[c][m]
            for b, mask in masks.items():
                out.append({
                    "scheme": scheme, "condition": c, "model": m, "bucket": b,
                    "n_utts": int(mask.sum()),
                    "utt_share": round(mask.sum() / n_utt, 3),
                    "word_share": round(length[mask].sum() / n_words, 3),
                    "utt_wer": round(metric(d, "utt_wer", mask=mask), 2),
                    "corpus_wer": round(metric(d, "corpus_wer", mask=mask), 2),
                    "corpus_cer": round(metric(d, "corpus_cer", mask=mask), 2),
                    "insert_heavy_utts": int(((d["we"] > d["wl"]) & mask).sum()),
                })
    return out


# --------------------------------------------------------------------------- #
# 3. Code-switch flag controlled for length
# --------------------------------------------------------------------------- #

def standardised(d, name, masks, weights, group, idx=None):
    """Direct standardisation: sum_b w_b * metric(group & bucket b)."""
    tot = 0.0
    for b, w in weights.items():
        tot = tot + w * metric(d, name, idx=idx, mask=masks[b] & group)
    return tot


def cs_by_length(data, length, flags, boot) -> list[dict]:
    out = []
    for scheme in SCHEMES:
        masks = bucket_masks(length, scheme)
        # Standardise only over buckets where both groups have >= MIN_CELL
        # utterances; weights = pooled word share of those buckets (renormalised).
        used = [b for b, mk in masks.items()
                if (mk & flags).sum() >= MIN_CELL and (mk & ~flags).sum() >= MIN_CELL]
        wsum = sum(length[masks[b]].sum() for b in used)
        weights = {b: length[masks[b]].sum() / wsum for b in used}
        for c in CONDITIONS:
            for m in sorted(data[c]):
                d = data[c][m]
                for met in ("corpus_wer", "corpus_cer"):
                    for b, mask in masks.items():
                        f, u = mask & flags, mask & ~flags
                        both = f.any() and u.any()
                        out.append({
                            "scheme": scheme, "condition": c, "model": m, "bucket": b,
                            "metric": met, "n_flagged": int(f.sum()), "n_unflagged": int(u.sum()),
                            "flagged": round(metric(d, met, mask=f), 2) if f.any() else "",
                            "unflagged": round(metric(d, met, mask=u), 2) if u.any() else "",
                            "delta": round(metric(d, met, mask=f) - metric(d, met, mask=u), 2)
                            if both else "",
                            "ci_low": "", "ci_high": "", "ci_includes_0": "",
                            "n_valid_resamples": "", "buckets_used": "", "p_boot": "",
                        })
                    sf = standardised(d, met, masks, weights, flags)
                    su = standardised(d, met, masks, weights, ~flags)
                    diff = (standardised(d, met, masks, weights, flags, boot)
                            - standardised(d, met, masks, weights, ~flags, boot))
                    lo, hi = pct_ci(diff)
                    out.append({
                        "scheme": scheme, "condition": c, "model": m, "bucket": "standardised",
                        "metric": met,
                        "n_flagged": int(sum((masks[b] & flags).sum() for b in used)),
                        "n_unflagged": int(sum((masks[b] & ~flags).sum() for b in used)),
                        "flagged": round(sf, 2), "unflagged": round(su, 2),
                        "delta": round(sf - su, 2), "ci_low": round(lo, 2),
                        "ci_high": round(hi, 2), "ci_includes_0": lo <= 0 <= hi,
                        "n_valid_resamples": int(np.isfinite(diff).sum()),
                        "buckets_used": "+".join(used),
                        "p_boot": round(boot_p_two_sided(diff), 4),
                        "_p": boot_p_two_sided(diff),
                    })
    # one family = the 17 per-model standardised tests of one metric within one
    # (bucket scheme, condition); per-bucket descriptive rows are not tested
    add_holm(out, ("scheme", "condition", "metric"))
    return out


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def md_table(rows, cols) -> list[str]:
    L = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        L.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return L + [""]


def write_pairwise_md(path, rows):
    L = ["# Paired bootstrap: adjacent models in each ranking", "",
         f"delta = lower-ranked minus higher-ranked model (percentage points); "
         f"95% percentile CI over {N_BOOT} paired resamples of utterances (seed {SEED}). "
         "`p_boot_delta_le_0` = share of resamples where the lower-ranked model "
         "is not worse. `p_boot` = two-sided bootstrap p-value "
         "(2·min(#Δ≤0+1, #Δ≥0+1)/(B+1)); `p_holm` = Holm–Bonferroni adjusted, "
         "one family per (condition, ranking, metric) = all adjacent pairs of "
         f"that ranking (`family_size`); `reject_holm_05` = p_holm < {ALPHA}. "
         f"With B = {N_BOOT} the smallest p_boot is {2 / (N_BOOT + 1):.4f}. Adjacent "
         "pairs are chosen by the point-estimate ranking on the same data, so "
         "delta >= 0 on the ranking's own metric by construction.", ""]
    cols = ["rank_upper", "model_upper", "model_lower", "metric", "value_upper",
            "value_lower", "delta", "ci_low", "ci_high", "ci_includes_0",
            "p_boot_delta_le_0", "p_boot", "p_holm", "reject_holm_05"]
    for c in CONDITIONS:
        for rk in METRICS:
            sel = [r for r in rows if r["condition"] == c and r["ranking"] == rk]
            L += [f"## {c} — ranking by {rk}", ""] + md_table(sel, cols)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def write_length_md(path, rows):
    L = ["# WER/CER by reference-length bucket", "",
         "Length = raw reference word count. `utt_share` / `word_share` are the "
         "weights a bucket gets in utterance-averaged vs corpus-level WER. "
         "`insert_heavy_utts` = utterances with more word errors than reference words "
         "(per-utterance WER > 100%).", ""]
    cols = ["model", "bucket", "n_utts", "utt_share", "word_share", "utt_wer",
            "corpus_wer", "corpus_cer", "insert_heavy_utts"]
    for scheme in SCHEMES:
        for c in CONDITIONS:
            sel = [r for r in rows if r["condition"] == c and r["scheme"] == scheme]
            L += [f"## {c} — buckets: {scheme}", ""] + md_table(sel, cols)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def write_cs_md(path, rows):
    L = ["# Code-switch flag vs length", "",
         "Flagged = extended detector (Latin letters or Urdu-script loanword) on the "
         "raw reference. Per-bucket rows compare flagged vs unflagged utterances of "
         "the same length bucket. `standardised` rows weight each group's per-bucket "
         "corpus metric by the pooled word share of the bucket, using only buckets "
         f"where both groups have >= {MIN_CELL} utterances (`buckets_used`), with a "
         f"{N_BOOT}-resample bootstrap CI (seed {SEED}) of the difference; resamples "
         "that leave a cell empty are dropped (`n_valid_resamples`). For the "
         "standardised rows, `p_boot` is the two-sided bootstrap p-value and "
         "`p_holm` the Holm–Bonferroni adjustment over all models (one family "
         f"per scheme × condition × metric, size in `family_size`); `reject_holm_05` = p_holm < {ALPHA}.", ""]
    cols = ["model", "bucket", "n_flagged", "n_unflagged", "flagged", "unflagged",
            "delta", "ci_low", "ci_high", "ci_includes_0", "p_boot", "p_holm",
            "reject_holm_05", "n_valid_resamples", "buckets_used"]
    for scheme in SCHEMES:
        for c in CONDITIONS:
            for met in ("corpus_wer", "corpus_cer"):
                sel = [r for r in rows if r["condition"] == c and r["metric"] == met
                       and r["scheme"] == scheme]
                L += [f"## {c} — {met} — buckets: {scheme}", ""] + md_table(sel, cols)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results-dir", default="results")
    a = p.parse_args()
    data, length, flags = load_per_utt(os.path.join(a.results_dir, "reeval_per_utt.csv"))
    boot = bootstrap_indices(len(length))

    pw = pairwise(data, boot)
    write_csv(os.path.join(a.results_dir, "reeval_pairwise.csv"), pw)
    write_pairwise_md(os.path.join(a.results_dir, "reeval_pairwise.md"), pw)

    lb = length_buckets(data, length)
    write_csv(os.path.join(a.results_dir, "reeval_length_buckets.csv"), lb)
    write_length_md(os.path.join(a.results_dir, "reeval_length_buckets.md"), lb)

    cs = cs_by_length(data, length, flags, boot)
    write_csv(os.path.join(a.results_dir, "reeval_cs_by_length.csv"), cs)
    write_cs_md(os.path.join(a.results_dir, "reeval_cs_by_length.md"), cs)
    print("wrote reeval_pairwise, reeval_length_buckets, reeval_cs_by_length (.csv/.md)")


if __name__ == "__main__":
    main()
