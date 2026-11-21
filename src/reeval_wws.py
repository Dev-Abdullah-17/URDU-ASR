"""Re-evaluate the released outputs of "WER We Stand" (Arif et al., COLING 2025).

Their repo (github.com/sameearif/WER-We-Stand) ships 471 hypotheses x 17 models
for the conversational set at outputs/<family>/<model>/csalt-voice.json. This
script rescores them under several scoring conditions and asks: how much of the
reported WER, and of the model ranking, is an artefact of normalization and of
the WER aggregation?

Conditions
----------
as_released   Their src/wer.py::compute_wer_csalt: hypothesis filtered to the
              characters in src/chars.json, `#\\S+` tags removed, whitespace
              collapsed; reference used raw; per-utterance WER averaged.
              NOTE: chars.json is not in their repository. Pass --chars-json if
              you have it; otherwise the character inventory of the 471
              references is used as a stand-in and the condition is labelled
              `as_released~` everywhere.
raw           No normalization on either side (whitespace tokenisation only).
N1..N8        Our normalizer, steps added cumulatively, applied identically to
              reference AND hypothesis (see CONDITIONS below). N7 keeps Latin
              tokens, N8 drops them, so both are reported. Every N-condition
              first drops "#..." disfluency tags (Seamless), as the paper
              describes; `raw` keeps them.
N7+hamza      Ablation: N7 plus the legacy (lossy) آ->ا / ئ->ی / ؤ->و merge.

Metrics (for every condition x model)
-------------------------------------
utt_wer       mean of per-utterance WER (their metric)
corpus_wer    sum(S+D+I) / sum(reference words)
corpus_cer    character-level analogue of corpus_wer
Each is reported for subsets overall / code_switched / monolingual (extended
detector: Latin letters OR Urdu-script loanword) / code_switched_latin_only
(old heuristic). 95% bootstrap CIs (1000 resamples of utterances, seed 42; the same resampled
index sets are used for every model and condition, i.e. paired), model ranks,
and Kendall's tau of each condition's ranking vs the as-released ranking.

References are never modified on disk; normalization is applied in memory to
both sides. Utterances whose normalized reference is empty are excluded from
that condition (count reported as n_excluded).

Usage
-----
    git clone https://github.com/sameearif/WER-We-Stand external/WER-We-Stand
    python src/reeval_wws.py --wws-dir external/WER-We-Stand \\
        --hf-dataset urdu-asr/csalt-voice --out-dir results

    # offline: a JSON list of the 471 reference strings in dataset order
    # (e.g. written by a previous run to results/csalt_voice_refs.json)
    python src/reeval_wws.py --wws-dir external/WER-We-Stand \\
        --refs-json results/csalt_voice_refs.json --out-dir results
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Callable

import jiwer
import numpy as np
from scipy.stats import kendalltau

from normalize_urdu import UrduNormalizer, code_switch_method, is_code_switched

N_UTTERANCES = 471
N_MODELS = 17
SEED = 42
N_BOOT = 1000

# Paper Table 3, "Conversational Speech" column (arXiv:2409.11252), keyed by
# output directory name. Used only to sanity-check the as_released reproduction.
PAPER_WER = {
    "whisper-tiny": 163.18, "whisper-tiny-ur": 59.99,
    "whisper-base": 163.52, "whisper-base-ur": 48.61,
    "whisper-small": 55.67, "whisper-small-ur": 32.92,
    "whisper-medium": 40.22, "whisper-medium-ur": 28.87,
    "whisper-large-v3": 18.30, "whisper-large-v3-ur": 17.86,
    "mms-300m-ur": 66.40,
    "mms-1b-all": 46.44, "mms-1b-ur": 42.46,
    "hf-seamless-m4t-medium": 22.33, "seamless-m4t-medium-ur": 20.01,
    "seamless-m4t-v2-large": 29.99, "seamless-m4t-v2-large-ur": 18.75,
}


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #

def load_hypotheses(wws_dir: str) -> dict[str, list[str]]:
    paths = sorted(glob.glob(os.path.join(wws_dir, "outputs", "*", "*", "csalt-voice.json")))
    hyps = {}
    for p in paths:
        model = os.path.basename(os.path.dirname(p))
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        assert all(isinstance(h, str) for h in data), f"{p}: expected list[str]"
        hyps[model] = data
    assert len(hyps) == N_MODELS, f"expected {N_MODELS} models, found {len(hyps)}"
    return hyps


def prepare_dataset_like_wws(dataset_name: str):
    """Exact replica of WER-We-Stand src/utils.py::prepare_dataset (HF branch).

    train+test are concatenated *only if* a train split exists; otherwise the
    validation split is used, else test. For urdu-asr/csalt-voice the released
    notebook shows a single `validation` split of 471 rows.
    """
    from datasets import concatenate_datasets, load_dataset

    dataset = load_dataset(dataset_name)
    print(f"[refs] {dataset_name} splits: "
          f"{ {k: v.num_rows for k, v in dataset.items()} }")
    if "train" in dataset:
        print("[refs] using concatenate_datasets([train, test])")
        dataset = concatenate_datasets([dataset["train"], dataset["test"]])
    elif "validation" in dataset:
        print("[refs] using validation split")
        dataset = dataset["validation"]
    else:
        print("[refs] using test split")
        dataset = dataset["test"]
    return dataset


def load_references(args) -> tuple[list[str], dict]:
    if args.refs_json:
        with open(args.refs_json, encoding="utf-8") as f:
            data = json.load(f)
        refs = [d["transcription"] if isinstance(d, dict) else d for d in data]
        source = {"refs_json": os.path.abspath(args.refs_json)}
    else:
        ds = prepare_dataset_like_wws(args.hf_dataset)
        if "audio" in ds.column_names:
            ds = ds.remove_columns("audio")  # text only; never decode audio
        refs = list(ds["transcription"])     # column used by compute_wer_csalt
        source = {"hf_dataset": args.hf_dataset,
                  "fingerprint": getattr(ds, "_fingerprint", None)}
        try:
            from huggingface_hub import HfApi
            source["revision"] = HfApi().dataset_info(args.hf_dataset).sha
        except Exception as e:  # provenance only; never fatal
            source["revision"] = f"unavailable: {e.__class__.__name__}"
        if args.cache_refs:
            os.makedirs(os.path.dirname(args.cache_refs) or ".", exist_ok=True)
            with open(args.cache_refs, "w", encoding="utf-8") as f:
                json.dump(refs, f, ensure_ascii=False, indent=0)
            source["cached_to"] = args.cache_refs
    assert all(isinstance(r, str) for r in refs)
    return refs, source


# --------------------------------------------------------------------------- #
# Conditions
# --------------------------------------------------------------------------- #

_WWS_TAG_RE = re.compile(r"#\S+")


def wws_clean_hyp(h: str, chars: set[str]) -> str:
    """WER-We-Stand compute_wer_csalt hypothesis cleanup (reference untouched)."""
    h = "".join(c for c in h if c in chars)
    h = _WWS_TAG_RE.sub("", h)
    return " ".join(h.split())


def _norm(**kw) -> UrduNormalizer:
    # Every N-condition drops "#..." disfluency tags first (the paper removed
    # Seamless "#" disfluencies by regex before scoring; references contain no "#").
    base = dict(strip_disfluency_tags=True, map_confusables=False, merge_hamza_madda=False, strip_diacritics=False,
                normalize_digits=False, digits_to_words=False, remove_punct=False,
                lower_latin=False, latin_tokens="keep", collapse_whitespace=True)
    base.update(kw)
    return UrduNormalizer(**base)


# Cumulative normalizer steps. Disfluency-tag removal, NFC and zero-width
# removal are on in every N-condition, so they form step N1. `raw` and
# `as_released~` do not use UrduNormalizer and are unaffected.
_STEPS = [
    ("N1_unicode", "drop #-disfluency tags + NFC + zero-width removal", {}),
    ("N2_punct", "+ punctuation removal", {"remove_punct": True}),
    ("N3_lower", "+ lowercase Latin", {"lower_latin": True}),
    ("N4_confusables", "+ Arabic->Urdu confusables", {"map_confusables": True}),
    ("N5_diacritics", "+ strip diacritics", {"strip_diacritics": True}),
    ("N6_digits", "+ digits -> ASCII", {"normalize_digits": True}),
    ("N7_numwords", "+ digits -> Urdu words (Latin kept)", {"digits_to_words": True}),
    ("N8_latin_drop", "+ drop Latin tokens", {"latin_tokens": "drop"}),
]


@dataclass
class Condition:
    name: str
    description: str
    ref_fn: Callable[[str], str]
    hyp_fn: Callable[[str], str]


def build_conditions(chars: set[str], as_released_name: str) -> list[Condition]:
    ident = lambda s: s  # noqa: E731
    conds = [
        Condition(as_released_name, "WWS released scoring: hyp char-filter + tag removal; raw ref",
                  ident, lambda h: wws_clean_hyp(h, chars)),
        Condition("raw", "no normalization (whitespace split)", ident, ident),
    ]
    kw: dict = {}
    for name, desc, step in _STEPS:
        kw = {**kw, **step}
        f = _norm(**kw)
        conds.append(Condition(name, desc, f, f))
        if name == "N7_numwords":
            g = _norm(**kw, merge_hamza_madda=True)
            conds.append(Condition("N7+hamza_merge", "N7 + legacy آ->ا, ئ->ی, ؤ->و merge (ablation)", g, g))
    return conds


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #

def edit_counts(refs: list[str], hyps: list[str], unit: str) -> tuple[np.ndarray, np.ndarray]:
    """Per-utterance (errors, reference length) at word or char level.

    Tokenisation: any run of Unicode whitespace (tabs, newlines, NBSP, ...)
    separates words, as str.split() does; jiwer alone splits only on ' '."""
    errs, lens = np.zeros(len(refs)), np.zeros(len(refs))
    process = jiwer.process_words if unit == "word" else jiwer.process_characters
    for i, (r, h) in enumerate(zip(refs, hyps)):
        r, h = " ".join(r.split()), " ".join(h.split())
        o = process(r, h)
        errs[i] = o.substitutions + o.deletions + o.insertions
        lens[i] = o.substitutions + o.deletions + o.hits
    return errs, lens


def bootstrap_indices(n: int, n_boot: int = N_BOOT, seed: int = SEED) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, n, size=(n_boot, n))


def ci(samples: np.ndarray) -> tuple[float, float]:
    """95% percentile interval over the finite resamples. A resample that
    contains no utterance of a small subset gives 0/0 = NaN; it is dropped
    rather than turning the whole interval into NaN."""
    samples = samples[np.isfinite(samples)]
    if not len(samples):
        return float("nan"), float("nan")
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return float(lo), float(hi)


def score(word_err, word_len, char_err, char_len, mask, boot) -> dict:
    """Point estimates + paired bootstrap CIs over utterances where mask is True."""
    we, wl = word_err * mask, word_len * mask
    ce, cl = char_err * mask, char_len * mask
    with np.errstate(divide="ignore", invalid="ignore"):
        # empty reference: errors / max(ref_len, 1), as in reeval_analysis.metric
        utt = np.where(mask, word_err / np.maximum(word_len, 1), 0.0)
    n = mask.sum()
    res = {
        "n": int(n),
        "utt_wer": 100 * utt.sum() / n,
        "corpus_wer": 100 * we.sum() / wl.sum(),
        "corpus_cer": 100 * ce.sum() / cl.sum(),
    }
    b_mask = mask[boot]
    b_n = b_mask.sum(1)
    res["utt_wer_ci"] = ci(100 * utt[boot].sum(1) / b_n)
    res["corpus_wer_ci"] = ci(100 * we[boot].sum(1) / wl[boot].sum(1))
    res["corpus_cer_ci"] = ci(100 * ce[boot].sum(1) / cl[boot].sum(1))
    return res


def ranks(values: dict[str, float]) -> dict[str, int]:
    order = sorted(values, key=lambda m: (values[m], m))
    return {m: i + 1 for i, m in enumerate(order)}


def tau(a: dict[str, float], b: dict[str, float]) -> float:
    models = sorted(a)
    return float(kendalltau([a[m] for m in models], [b[m] for m in models]).statistic)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def git_rev(path: str) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--wws-dir", default="external/WER-We-Stand")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--hf-dataset", default="urdu-asr/csalt-voice")
    src.add_argument("--refs-json", default=None,
                     help="JSON list of the 471 reference strings, in dataset order")
    p.add_argument("--cache-refs", default="results/csalt_voice_refs.json",
                   help="where to write the loaded references (HF mode); '' to skip")
    p.add_argument("--chars-json", default=None,
                   help="WWS src/chars.json (not in their repo). If omitted, the "
                        "reference character inventory is used as a stand-in.")
    p.add_argument("--out-dir", default="results")
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    hyps = load_hypotheses(args.wws_dir)
    refs, ref_source = load_references(args)
    assert len(refs) == N_UTTERANCES, f"expected {N_UTTERANCES} references, got {len(refs)}"
    for m, h in hyps.items():
        assert len(h) == len(refs), f"{m}: {len(h)} hyps vs {len(refs)} refs"
    print(f"[align] {len(refs)} references x {len(hyps)} models: aligned")

    if args.chars_json:
        with open(args.chars_json, encoding="utf-8") as f:
            chars = set(json.load(f))
        as_rel = "as_released"
    else:
        chars = set("".join(refs))
        as_rel = "as_released~"
        print("[warn] --chars-json not given: using reference character inventory "
              f"({len(chars)} chars) as stand-in; condition labelled {as_rel!r}")

    conditions = build_conditions(chars, as_rel)
    models = sorted(hyps)
    boot = bootstrap_indices(len(refs))

    # Code-switch flags on raw references (old heuristic vs extended detector).
    cs_rows = [{"utt_id": i, "latin_heuristic": is_code_switched(r),
                "method": code_switch_method(r), "reference": r}
               for i, r in enumerate(refs)]

    cs_ext = np.array([r["method"] != "none" for r in cs_rows])
    cs_old = np.array([r["latin_heuristic"] for r in cs_rows])
    subsets = {"overall": np.ones(len(refs), bool), "code_switched": cs_ext,
               "monolingual": ~cs_ext, "code_switched_latin_only": cs_old}

    # results[subset][condition][model] -> metrics
    results: dict[str, dict[str, dict[str, dict]]] = {k: {} for k in subsets}
    per_utt_path = os.path.join(args.out_dir, "reeval_per_utt.csv")
    with open(per_utt_path, "w", newline="", encoding="utf-8") as fu:
        wu = csv.writer(fu)
        wu.writerow(["condition", "model", "utt_id", "cs_method", "word_err", "ref_words",
                     "char_err", "ref_chars", "ref_norm", "hyp_norm"])
        for c in conditions:
            r_norm = [c.ref_fn(r) for r in refs]
            nonempty = np.array([bool(r.strip()) for r in r_norm])
            rr = [r if k else "x" for r, k in zip(r_norm, nonempty)]  # placeholder; masked out
            for sub in subsets:
                results[sub][c.name] = {}
            for m in models:
                h_norm = [c.hyp_fn(h) for h in hyps[m]]
                we, wl = edit_counts(rr, h_norm, "word")
                ce, cl = edit_counts(rr, h_norm, "char")
                for sub, smask in subsets.items():
                    mask = nonempty & smask
                    if not mask.any():
                        continue
                    sc = score(we, wl, ce, cl, mask, boot)
                    sc["n_excluded"] = int((smask & ~nonempty).sum())
                    results[sub][c.name][m] = sc
                for i in range(len(refs)):
                    if nonempty[i]:
                        wu.writerow([c.name, m, i, cs_rows[i]["method"], int(we[i]), int(wl[i]),
                                     int(ce[i]), int(cl[i]), r_norm[i], h_norm[i]])
            print(f"[done] {c.name}")

    # Rankings + Kendall's tau vs as-released (overall, ranked by their utt_wer).
    base_vals = {m: results["overall"][as_rel][m]["utt_wer"] for m in models}
    rows = []
    for sub in subsets:
        for c in conditions:
            if len(results[sub][c.name]) != len(models):
                continue
            for metric in ("utt_wer", "corpus_wer", "corpus_cer"):
                vals = {m: results[sub][c.name][m][metric] for m in models}
                rk = ranks(vals)
                t = tau(base_vals, vals)
                for m in models:
                    sc = results[sub][c.name][m]
                    lo, hi = sc[f"{metric}_ci"]
                    rows.append({
                        "subset": sub, "condition": c.name, "description": c.description,
                        "metric": metric, "model": m, "value": round(sc[metric], 2),
                        "ci_low": round(lo, 2), "ci_high": round(hi, 2),
                        "rank": rk[m], "kendall_tau_vs_as_released": round(t, 3),
                        "n": sc["n"], "n_excluded": sc["n_excluded"],
                        "paper_wer": (PAPER_WER.get(m) if sub == "overall" and c.name == as_rel
                                      and metric == "utt_wer" else ""),
                    })

    table_csv = os.path.join(args.out_dir, "reeval_table.csv")
    with open(table_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    cs_path = os.path.join(args.out_dir, "reeval_codeswitch_flags.csv")
    with open(cs_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cs_rows[0]))
        w.writeheader()
        w.writerows(cs_rows)

    write_markdown(os.path.join(args.out_dir, "reeval_table.md"), results, conditions,
                   models, as_rel, base_vals, cs_rows, refs)

    meta = {
        "wws_dir": os.path.abspath(args.wws_dir), "wws_commit": git_rev(args.wws_dir),
        "references": ref_source, "n_utterances": len(refs), "models": models,
        "chars_json": args.chars_json, "as_released_label": as_rel,
        "bootstrap": {"n_resamples": N_BOOT, "seed": SEED, "paired": True},
        "conditions": [{"name": c.name, "description": c.description} for c in conditions],
    }
    with open(os.path.join(args.out_dir, "reeval_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[out] {table_csv}, reeval_table.md, {per_utt_path}, {cs_path}, reeval_meta.json")


def write_markdown(path, results, conditions, models, as_rel, base_vals, cs_rows, refs):
    from collections import Counter
    overall = results["overall"]
    L = ["# WER We Stand — re-evaluation of released conversational outputs", ""]
    L += [f"{len(refs)} utterances x {len(models)} models. Values in %, "
          "95% paired bootstrap CI (1000 resamples, seed 42) in brackets, rank in "
          "parentheses (1 = best). tau = Kendall's tau of the model ranking vs the "
          f"`{as_rel}` ranking (overall, utterance-averaged WER).", ""]
    if as_rel.endswith("~"):
        L += ["> `as_released~`: WWS `src/chars.json` is not in their repository; the "
              "reference character inventory is used as a stand-in for the hypothesis "
              "character filter. Compare against the `paper` column.", ""]

    L += ["## Ranking stability (Kendall's tau vs as-released, overall)", "",
          "| condition | description | utt_wer | corpus_wer | corpus_cer |", "|---|---|---|---|---|"]
    for c in conditions:
        ts = [tau(base_vals, {m: overall[c.name][m][k] for m in models})
              for k in ("utt_wer", "corpus_wer", "corpus_cer")]
        L.append(f"| {c.name} | {c.description} | " + " | ".join(f"{t:.3f}" for t in ts) + " |")
    L.append("")

    for metric in ("utt_wer", "corpus_wer", "corpus_cer"):
        L += [f"## Overall — {metric}", ""]
        head = ["model"] + (["paper"] if metric == "utt_wer" else []) + [c.name for c in conditions]
        L += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        rk = {c.name: ranks({mm: overall[c.name][mm][metric] for mm in models}) for c in conditions}
        for m in sorted(models, key=lambda m: base_vals[m]):
            cells = [m] + ([f"{PAPER_WER.get(m, '')}"] if metric == "utt_wer" else [])
            for c in conditions:
                sc = overall[c.name][m]
                lo, hi = sc[f"{metric}_ci"]
                cells.append(f"{sc[metric]:.2f} [{lo:.1f}, {hi:.1f}] ({rk[c.name][m]})")
            L.append("| " + " | ".join(cells) + " |")
        L.append("")

    show = [c.name for c in conditions if c.name in (as_rel, "raw", "N7_numwords", "N8_latin_drop")]
    L += ["## Code-switched vs monolingual — corpus WER / CER", "",
          "Subsets use the extended detector (Latin letters OR Urdu-script loanword) on "
          "the raw reference; `code_switched_latin_only` uses the old heuristic.", ""]
    for cname in show:
        L += [f"### {cname}", "",
              "| model | overall WER | code_switched WER | monolingual WER | cs_latin_only WER "
              "| overall CER | code_switched CER | monolingual CER |", "|---|---|---|---|---|---|---|---|"]
        for m in sorted(models, key=lambda m: base_vals[m]):
            def g(sub, k):
                sc = results[sub].get(cname, {}).get(m)
                return f"{sc[k]:.2f} (n={sc['n']})" if sc else "–"
            L.append(f"| {m} | " + " | ".join(
                [g("overall", "corpus_wer"), g("code_switched", "corpus_wer"),
                 g("monolingual", "corpus_wer"), g("code_switched_latin_only", "corpus_wer"),
                 g("overall", "corpus_cer"), g("code_switched", "corpus_cer"),
                 g("monolingual", "corpus_cer")]) + " |")
        L.append("")

    cnt = Counter(r["method"] for r in cs_rows)
    old = sum(r["latin_heuristic"] for r in cs_rows)
    L += ["## Code-switch detection on references", "",
          f"Old Latin-letter heuristic flags {old}/{len(refs)} utterances. Extended "
          "detector by method: " + ", ".join(f"{k}={cnt.get(k, 0)}"
                                             for k in ("latin", "loanword", "both", "none")),
          "", "Per-utterance flags: `reeval_codeswitch_flags.csv`.", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
