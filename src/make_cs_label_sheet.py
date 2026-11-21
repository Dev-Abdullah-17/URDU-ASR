"""Write a LOCAL code-switch labelling sheet with reference text (never commit).

Joins the 100 ids in data/codeswitch_labels_template.csv (seed-42 sample, see
make_cs_label_template.py) with their csalt-voice reference text and writes
data/codeswitch_labels_local.csv with columns:

    utterance_id, reference, has_english   (has_english left empty: yes / no)

The output contains dataset reference text, so it is gitignored (data/* in
.gitignore) and must not be committed or shared. The committed template stays
ids-only; copy your yes/no labels back into it to share them.

References are read from results/csalt_voice_refs.json (cached by
reeval_wws.py, in the same order as utterance_id). If that file is missing,
run `python src/reeval_wws.py --wws-dir external/WER-We-Stand --out-dir results`
first (needs huggingface.co access).

    python src/make_cs_label_sheet.py

Writes UTF-8 with a BOM so that spreadsheet programs (Excel, LibreOffice) detect
the encoding and display Urdu correctly. An existing output file is never
overwritten (your labels may be in it) unless --force is given.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

N_UTTERANCES = 471


def build_rows(template_path: str, refs: list[str]) -> list[dict]:
    """Template ids joined with their reference text, in template order."""
    if len(refs) != N_UTTERANCES:
        raise ValueError(f"expected {N_UTTERANCES} references, got {len(refs)}")
    rows = []
    with open(template_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            i = int(r["utterance_id"])
            if not 0 <= i < len(refs):
                raise ValueError(f"utterance_id {i} out of range")
            rows.append({"utterance_id": i, "reference": refs[i],
                         "has_english": r.get("has_english", "") or ""})
    if len({r["utterance_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate utterance_id in template")
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--template", default="data/codeswitch_labels_template.csv")
    p.add_argument("--refs", default="results/csalt_voice_refs.json")
    p.add_argument("--out", default="data/codeswitch_labels_local.csv")
    p.add_argument("--force", action="store_true", help="overwrite an existing sheet")
    a = p.parse_args(argv)

    if os.path.exists(a.out) and not a.force:
        print(f"{a.out} already exists (it may hold your labels); "
              "use --force to overwrite", file=sys.stderr)
        return 1
    if not os.path.exists(a.refs):
        print(f"{a.refs} not found: run src/reeval_wws.py first", file=sys.stderr)
        return 1
    with open(a.refs, encoding="utf-8") as f:
        refs = json.load(f)
    rows = build_rows(a.template, refs)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["utterance_id", "reference", "has_english"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {a.out} (contains reference text: do not commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
