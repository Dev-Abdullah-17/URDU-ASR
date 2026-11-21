"""Count disfluency tags and Latin tokens in the released WER We Stand outputs.

Aggregate counts only (no hypothesis or reference text), per model, over the
471 csalt-voice hypotheses in outputs/<family>/<model>/csalt-voice.json:

    tag_tokens            whitespace tokens starting with "#" + non-space (#\\S+)
    utts_with_tag         utterances containing at least one tag token
    tags_latin_body       tag tokens whose body contains a Latin letter
    tags_arabic_body      tag tokens whose body has Arabic-script letters only
    tags_other_body       remaining tag tokens
    latin_tokens          whitespace tokens containing a Latin letter
    latin_tokens_tag      ... of which are tag tokens
    latin_tokens_non_tag  ... of which are not

Writes results/reeval_tag_counts.csv (committed; aggregate only).

    python src/count_disfluency_tags.py --wws-dir external/WER-We-Stand --out results/reeval_tag_counts.csv
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re

TAG_RE = re.compile(r"^#\S+$")
LATIN_RE = re.compile(r"[A-Za-z]")
ARABIC_ONLY_RE = re.compile(r"^[؀-ۿ]+$")

FIELDS = ["model", "n_utts", "tag_tokens", "utts_with_tag", "tags_latin_body",
          "tags_arabic_body", "tags_other_body", "latin_tokens", "latin_tokens_tag",
          "latin_tokens_non_tag"]


def count(hyps: list[str]) -> dict:
    c = {k: 0 for k in FIELDS[1:]}
    c["n_utts"] = len(hyps)
    for h in hyps:
        toks = h.split()
        tags = [t for t in toks if TAG_RE.match(t)]
        c["tag_tokens"] += len(tags)
        c["utts_with_tag"] += bool(tags)
        for t in tags:
            body = t[1:]
            if LATIN_RE.search(body):
                c["tags_latin_body"] += 1
            elif ARABIC_ONLY_RE.match(body):
                c["tags_arabic_body"] += 1
            else:
                c["tags_other_body"] += 1
        for t in toks:
            if LATIN_RE.search(t):
                c["latin_tokens"] += 1
                if TAG_RE.match(t):
                    c["latin_tokens_tag"] += 1
                else:
                    c["latin_tokens_non_tag"] += 1
    return c


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--wws-dir", default="external/WER-We-Stand")
    p.add_argument("--out", default="results/reeval_tag_counts.csv")
    a = p.parse_args(argv)
    rows = []
    for f in sorted(glob.glob(os.path.join(a.wws_dir, "outputs", "*", "*", "csalt-voice.json"))):
        with open(f, encoding="utf-8") as fh:
            rows.append({"model": os.path.basename(os.path.dirname(f)), **count(json.load(fh))})
    total = {"model": "TOTAL", **{k: sum(r[k] for r in rows) for k in FIELDS[1:]}}
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows + [total])
    print(f"wrote {len(rows)} models + TOTAL to {a.out}")


if __name__ == "__main__":
    main()
