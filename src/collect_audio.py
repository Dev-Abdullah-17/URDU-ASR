"""Collect candidate conversational / code-switched Urdu audio (Phase 1).

Downloads audio from a list of URLs (prefer Creative Commons / licensed content),
resamples to 16 kHz mono WAV, and splits into short chunks with a manifest ready
for MANUAL transcription. This script only prepares raw material; the transcription
itself is human work (that human-corrected slice IS your dataset contribution).

Ethics / licensing:
- Only collect content you have the right to use for research.
- If a source's license does not permit redistribution, release transcripts +
  source URLs + timestamps instead of raw audio (an "audio-less" benchmark).
- Record speaker consent where applicable; document provenance in the dataset card.

Requires `yt-dlp` and `ffmpeg` on PATH.

Example:
    python src/collect_audio.py --urls urls.txt --out data/raw --chunk-seconds 20
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import uuid


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--urls", required=True, help="Text file, one URL per line")
    p.add_argument("--out", default="data/raw")
    p.add_argument("--chunk-seconds", type=int, default=20)
    p.add_argument("--manifest", default="data/manifest.csv")
    return p.parse_args()


def download_audio(url: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, uuid.uuid4().hex)
    subprocess.run(
        [
            "yt-dlp", "-x", "--audio-format", "wav",
            "--postprocessor-args", "-ar 16000 -ac 1",
            "-o", stem + ".%(ext)s", url,
        ],
        check=True,
    )
    return stem + ".wav"


def chunk_audio(wav_path: str, chunk_seconds: int, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.basename(wav_path)[:-4]
    pattern = os.path.join(out_dir, base + "_%04d.wav")
    subprocess.run(
        [
            "ffmpeg", "-i", wav_path, "-f", "segment",
            "-segment_time", str(chunk_seconds), "-ar", "16000", "-ac", "1",
            pattern,
        ],
        check=True,
    )
    return sorted(
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith(base + "_") and f.endswith(".wav")
    )


def main():
    args = parse_args()
    with open(args.urls, encoding="utf-8") as f:
        urls = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]

    chunk_dir = os.path.join(args.out, "chunks")
    rows = []
    for url in urls:
        try:
            wav = download_audio(url, args.out)
            for chunk in chunk_audio(wav, args.chunk_seconds, chunk_dir):
                rows.append({"chunk_path": chunk, "source_url": url, "transcript": ""})
        except subprocess.CalledProcessError as exc:
            print(f"[warn] failed on {url}: {exc}")

    os.makedirs(os.path.dirname(args.manifest) or ".", exist_ok=True)
    with open(args.manifest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["chunk_path", "source_url", "transcript"])
        w.writeheader()
        w.writerows(rows)

    print(
        f"Wrote {len(rows)} chunks to {args.manifest} -- "
        f"now fill the 'transcript' column manually."
    )


if __name__ == "__main__":
    main()
