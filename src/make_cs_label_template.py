"""Write an empty code-switch labelling sheet for a seeded sample of csalt-voice.

Picks 100 of the 471 utterances (numpy default_rng(42), without replacement,
sorted) and writes data/codeswitch_labels_template.csv with columns
utterance_id, has_english. `utterance_id` is the 0-based index in the order
used by reeval_wws.py (WWS prepare_dataset order; same as `utt_id` there).
`has_english` is left blank for manual labelling (yes / no); the filled sheet
is used to measure precision/recall of the code-switch detectors. No
reference text is written, so the sheet can be shared without redistributing
the dataset.

    python src/make_cs_label_template.py
"""

from __future__ import annotations

import argparse
import csv
import os

import numpy as np

N_UTTERANCES = 471


def sample_ids(n_total: int = N_UTTERANCES, k: int = 100, seed: int = 42) -> list[int]:
    rng = np.random.default_rng(seed)
    return sorted(int(i) for i in rng.choice(n_total, size=k, replace=False))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/codeswitch_labels_template.csv")
    p.add_argument("--n", type=int, default=100)
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["utterance_id", "has_english"])
        for i in sample_ids(k=a.n, seed=a.seed):
            w.writerow([i, ""])
    print(f"wrote {a.n} rows to {a.out}")


if __name__ == "__main__":
    main()
