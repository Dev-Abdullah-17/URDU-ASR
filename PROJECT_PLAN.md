# Master Build Plan — Conversational, Code-Switched Urdu ASR

**One-line thesis:** Extend the "WER We Stand" Urdu ASR benchmark (Arif et al.,
COLING 2025, arXiv:2409.11252) to *conversational, code-switched* speech — the
exact gap its authors flagged — and ship a benchmark, a text normalizer, fine-tuned
open models, a deployed voice tool, and a paper.

This document is the source of truth. Hand it (and `CLAUDE.md`) to Claude Code and
work one phase at a time.

---

## 0. TL;DR — what you are building and why it's novel

Everyone builds text NLP; almost nobody with real ASR experience touches
low-resource *speech*. That is your unfair advantage (NexAura ASR work). The
"WER We Stand" paper published everything — models, a first conversational Urdu
set (**only ~471 clips / ~1.3 hours**), and eval scripts — and explicitly named
three unsolved problems: **code-switching, spontaneous-speech disfluencies, and
the absence of a robust Urdu text-normalization system.** You stand on that work
and push exactly where they pointed. This is defensible novelty, not a Kaggle rerun.

Precedent that this path produces papers: the Pashto Common Voice effort built an
open corpus and fine-tuned Whisper from ~99% word-error-rate (zero-shot) down to
~13% — and spun off multiple arXiv papers. Same shape, applied to Urdu code-switch.

**Target venue:** CHiPSAL (Challenges in Processing South Asian Languages) — it
already publishes Urdu/Pashto/Punjabi ASR work — plus an arXiv preprint. Interspeech
low-resource tracks are a stretch goal.

---

## 1. Definition of Done (the "fully audited / operational" bar)

The project is complete when **all** of these are true and reproducible from a
clean checkout:

- [ ] **Baseline established.** Zero-shot WER + CER for ≥3 models (Whisper-small,
      Whisper-medium, MMS) on FLEURS-ur and Common Voice-ur, saved as JSON.
- [ ] **Benchmark built.** ≥3 hours of transcribed conversational, code-switched
      Urdu, released on Hugging Face with a dataset card (license + provenance).
      Bigger than the existing 1.3h; the code-switch split is labelled.
- [ ] **Normalizer shipped.** `normalize_urdu.py` passes its unit tests and is used
      in every WER/CER computation. Documented and reusable.
- [ ] **Fine-tuned model beats zero-shot.** A LoRA-fine-tuned Whisper checkpoint
      improves overall WER over its zero-shot baseline on the held-out test set,
      released on HF Hub with a model card and honest numbers.
- [ ] **Code-switch analysis done.** Results reported as overall / code-switched /
      monolingual, with a per-utterance CSV and a bootstrap confidence interval on
      the headline WER.
- [ ] **Tool deployed.** A public Gradio/HF Space where you speak Urdu and get a
      transcript, running on your fine-tuned model.
- [ ] **Reproducible.** Pinned `requirements.txt`, fixed seeds, logged configs,
      saved raw outputs; anyone can rerun eval and get the same numbers.
- [ ] **Written up.** arXiv preprint + workshop submission + a dev.to post + a
      LinkedIn post; repo has a clear README.

If a box isn't checked, it isn't done. Track these in your issue tracker.

---

## 2. The five deliverables (how one body of work produces all of them)

1. **Dataset / benchmark** — code-switched conversational Urdu audio + transcripts (HF).
2. **Text normalizer** — small, citable, reused by everyone doing Urdu ASR (`src/normalize_urdu.py`).
3. **Fine-tuned models** — Whisper-small/-medium (and optionally w2v-BERT) LoRA adapters on HF Hub.
4. **Deployed voice tool** — `app/app.py`, aimed at low-literacy access (health/civic info).
5. **Paper** — extends WER We Stand; benchmark + normalizer + models + error analysis.

---

## 3. System architecture (data flow)

```
                 ┌─────────────────────────────────────────────────────────┐
                 │                     DATA LAYER                           │
  Open corpora   │  Common Voice (ur)  ·  FLEURS (ur_pk)  ·  ARL/CSaLT      │
  (read speech)  │            │                                            │
                 │            ▼                                            │
  Collected      │  YouTube/podcasts ──▶ collect_audio.py ──▶ manifest ──▶ │
  (conversational│                        (chunks)         manual transcribe│
   code-switch)  │                                            │            │
                 └────────────────────────────────────────────┼────────────┘
                                                               ▼
                 ┌─────────────────────────────────────────────────────────┐
                 │            normalize_urdu.py  (shared)                    │
                 └───────────────┬──────────────────────────┬──────────────┘
                                 ▼                          ▼
                 ┌───────────────────────┐    ┌───────────────────────────┐
                 │  train_whisper_lora.py │    │   evaluate_baseline.py     │
                 │   (Whisper + LoRA)     │    │   (zero-shot WER/CER)      │
                 └───────────┬───────────┘    └───────────────────────────┘
                             ▼
                 ┌───────────────────────┐    ┌───────────────────────────┐
                 │  checkpoints/ (adapter)│───▶│    evaluate_model.py       │
                 └───────────┬───────────┘    │  WER/CER + code-switch      │
                             ▼                 │  split + per-utt CSV        │
                 ┌───────────────────────┐    └───────────────────────────┘
                 │      app/app.py        │
                 │  (deployed voice tool) │
                 └───────────────────────┘
```

---

## 4. Repository structure

```
urdu-asr/
├── PROJECT_PLAN.md         # this file — the spec
├── CLAUDE.md               # Claude Code operating context + conventions
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── normalize_urdu.py       # text normalizer + code-switch detector
│   ├── evaluate_baseline.py    # Phase 0: zero-shot baselines
│   ├── collect_audio.py        # Phase 1: prep audio for transcription
│   ├── train_whisper_lora.py   # Phase 2: LoRA fine-tuning (+ --smoke-test)
│   └── evaluate_model.py       # Phase 3: eval fine-tuned + code-switch split
├── app/
│   └── app.py                  # Phase 4: Gradio voice demo
├── tests/
│   └── test_normalize.py
├── notebooks/                  # Kaggle/Colab notebooks wrapping the scripts
├── data/                       # (gitignored) corpora + collected audio + manifests
├── checkpoints/                # (gitignored) LoRA adapters
└── results/                    # (gitignored) JSON metrics + per-utterance CSVs
```

---

## 5. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.10–3.11 | Ecosystem standard for ASR |
| DL framework | PyTorch ≥ 2.1 | HF + PEFT backend |
| Models / training | Hugging Face `transformers` | Whisper, MMS, Seamless in one API |
| Efficient FT | `peft` (LoRA) | Fits Whisper on a single free GPU |
| Datasets | HF `datasets` | Common Voice, FLEURS, streaming |
| Metrics | `jiwer` | WER + CER, no network needed |
| Audio | `librosa`, `soundfile` | Resample / IO to 16 kHz mono |
| Data collection | `yt-dlp` + `ffmpeg` | Pull + chunk conversational audio |
| Demo / deploy | `gradio` → HF Spaces | You've shipped Streamlit/HF before |
| Compute | Kaggle (P100/T4, 30h/wk) | Free; primary. Colab as backup |
| Tracking | JSON/CSV in `results/` (+ optional W&B) | Reproducible, offline-friendly |

**Model choices, concretely.** WER We Stand found Seamless-large best on read
speech and Whisper-large best on conversational speech. You will:
- Use their released large models as *reference baselines* (don't retrain them).
- Fine-tune **Whisper-small / -medium with LoRA** yourself (fits free GPU).
- Optionally add **facebook/w2v-bert-2.0** (the Pashto SOTA backbone) as a second model.
- Keep MMS (`facebook/mms-1b-all`) as a strong zero-shot baseline.

---

## 6. Environment setup

```bash
# Local / Kaggle
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Common Voice is no longer on the Hugging Face Hub (see §7 note); download it
# from the Mozilla Data Collective and load it from a local path.
# Other gated HF datasets still need: huggingface-cli login

# System deps for data collection:
#   apt-get install -y ffmpeg    (or use conda / Kaggle image which has ffmpeg)
```

**Free-GPU reality & the gotchas you've hit before:**
- Kaggle gives ~30 GPU-hours/week, 12h sessions. Whisper-small LoRA fits easily;
  Whisper-medium needs `gradient_checkpointing=True` (already set) and possibly
  `--batch-size 4 --grad-accum 4`.
- **fp16 NaNs:** T4/P100 have no bf16, so the trainer falls back to fp16. If you
  see NaN loss, lower `--lr` (try `5e-5`), keep the default loss-scaling, and never
  disable it. (This is the same class of issue as your DeBERTa fp16 NaN — but the
  `transformers==4.44.2` pin was DeBERTa-specific; don't carry it here.)
- **Always single-GPU** on free tiers; set `CUDA_VISIBLE_DEVICES=0` if a second
  device appears.
- **Always `--seed`.** Determinism is part of the audit.

---

## 7. Datasets

| Name | Type | Role | License | Access | Size |
|---|---|---|---|---|---|
| Mozilla Common Voice (ur) | Read | Fine-tune fuel + baseline | CC0 | **Mozilla Data Collective** (left HF Hub Oct 2025; `mozilla-foundation/common_voice_*` no longer usable) | Growing; hours-scale |
| Google FLEURS (ur_pk) | Read | Standard benchmark | CC-BY | HF (`google/fleurs`, `ur_pk`) | ~10h test/dev/train |
| ARL Urdu Speech DB | Read | Extra read baseline | Research | Request from source | ~160k files |
| CSaLT Urdu | Read | Extra read baseline | Research | Request | — |
| WER We Stand release | Conversational + models + scripts | **Reproduce baselines; extend the conversational set** | Per repo | arXiv:2409.11252 links | ~1.3h conv. |
| `humairawan/Urdu-aud01` | Synthetic | Optional extra training (disclose synthetic) | Per card | HF | ~59k samples |
| **Your collected slice** | **Conversational, code-switched** | **The novel contribution** | You set it | YouTube/podcasts via `collect_audio.py` | Target ≥3h |

> **Common Voice moved (Oct 2025).** Mozilla removed Common Voice from the
> Hugging Face Hub; it is now distributed through the Mozilla Data Collective.
> `train_whisper_lora.py` therefore has **no default dataset** — `--dataset` is
> required. Download CV-ur from the Data Collective and pass a local path.

**Text-column names differ:** FLEURS uses `transcription`; Common Voice uses
`sentence`. The scripts expose `--text-column` for this.

### Data collection protocol (the part that earns the paper)
1. Curate 30–60 minutes of *naturally code-switched* Pakistani content — podcasts,
   talk shows, vlogs (urban Urdu-English mixing is the norm). Prefer Creative
   Commons / permissively licensed sources.
2. `python src/collect_audio.py --urls urls.txt --out data/raw --chunk-seconds 20`
   → produces 16 kHz mono chunks + a `manifest.csv`.
3. **Transcribe manually.** Optionally pre-fill with a base model, then correct.
   Correction is far faster than transcribing from scratch and is where quality
   comes from. Mark code-switched utterances.
4. Split into dev/test. Keep the *novel* test set small but pristine (≥3h total is
   plenty for a benchmark; do not chase size at the cost of quality).
5. **Ethics/licensing:** every clip needs a source URL + license note in the
   dataset card; record consent where applicable. If a license forbids
   redistribution, release transcripts + URLs + timestamps ("audio-less" benchmark)
   instead of raw audio. This is standard and keeps you clean.

---

## 8. Text normalization spec (`src/normalize_urdu.py`)

WER We Stand named the lack of a robust Urdu normalizer as a core problem, so this
is a real sub-contribution. It must handle:
- Unicode NFC composition; removal of zero-width marks (ZWNJ etc.).
- **Arabic↔Urdu confusables** (Arabic yeh→Urdu yeh, Arabic kaf→Urdu keheh, heh
  variants, hamza-carriers) — a major source of *spurious* WER.
- Diacritics/harakat stripping.
- Urdu/Arabic-Indic digits → ASCII.
- Punctuation removal for scoring (kept for display).
- Lowercasing Latin tokens (so code-switched English isn't double-counted).

Two presets ship: `scoring_normalizer` (punctuation removed, for WER/CER) and
`display_normalizer` (punctuation kept, for the app). Verified by `tests/test_normalize.py`.

---

## 9. Phase-by-phase build guide

Each phase lists: **Goal → Steps → Acceptance check → Claude Code prompt.**

### Phase 0 — Baseline (this week, 2–3 sessions)
**Goal:** the zero-shot gap numbers that motivate everything.
**Steps:**
- Set up the env; run `pytest -q` (normalizer green).
- Run `evaluate_baseline.py` for Whisper-small and MMS on FLEURS-ur (start with
  `--max-samples 200` to move fast, then full).
**Acceptance check:** `results/baseline_*.json` exists with overall/code-switched/
monolingual WER + CER for ≥2 models. You can state "zero-shot Whisper-small = X% WER".
**Claude Code prompt:** *"Read PROJECT_PLAN.md §9 Phase 0. Set up the venv, run the
normalizer tests, then run evaluate_baseline.py for openai/whisper-small and
facebook/mms-1b-all on FLEURS ur_pk test with --max-samples 200, and summarize the
WER/CER results in a markdown table."*

### Phase 1 — Data assembly & collection (weeks 1–3)
**Goal:** the open corpora wired in + a first code-switched conversational slice.
**Steps:**
- Load Common Voice-ur and FLEURS-ur; confirm audio casts to 16 kHz.
- Curate `urls.txt`; run `collect_audio.py`; manually transcribe ~30–60 min.
- Define dev/test splits and the code-switch labelling rule.
**Acceptance check:** a `data/manifest.csv` with real transcripts; a documented
split; a draft dataset card (license + provenance).
**Claude Code prompt:** *"Per §7 protocol, add a script that pre-fills the manifest
transcripts with whisper-small so I can correct them, and write a first dataset
card template with license/provenance fields."*

### Phase 2 — Fine-tune with LoRA (weeks 3–6)
**Goal:** a model that beats zero-shot.
**Steps:**
- **Smoke test first:** `python src/train_whisper_lora.py --smoke-test` — confirm
  loss drops on 20 samples. If not, fix before any real run.
- Real run on Common Voice(+FLEURS) with Whisper-small; then try -medium.
- Save adapter to `checkpoints/`.
**Acceptance check:** training completes; eval WER during training trends down;
adapter saved and loadable.
**Claude Code prompt:** *"Run the smoke test in train_whisper_lora.py and confirm
loss decreases. Then launch a 3-epoch run on Common Voice ur with whisper-small,
LoRA r=32, lr=1e-4, and report the best eval WER."*

### Phase 3 — Evaluation & error analysis (weeks 6–9)
**Goal:** the paper's core table + code-switch figure.
**Steps:**
- Run `evaluate_model.py` (base vs adapter) on your held-out test set *and* FLEURS.
- Produce overall / code-switched / monolingual WER+CER and the per-utterance CSV.
- Add a bootstrap confidence interval on headline WER (resample utterances).
- Inspect top error types (insertions/deletions/substitutions; where code-switch hurts).
**Acceptance check:** `results/ft_*.json` + `*_per_utt.csv`; a comparison table
zero-shot → fine-tuned, split by code-switch; a CI on the headline number.
**Claude Code prompt:** *"Add a bootstrap_ci helper (1000 resamples) to
evaluate_model.py for the overall WER, then build a results table comparing
zero-shot vs fine-tuned Whisper-small, split overall/code-switched/monolingual."*

### Phase 4 — Deploy the voice tool (weeks 6–9, in parallel)
**Goal:** a public demo on your fine-tuned model.
**Steps:**
- Run `app/app.py` locally with `ADAPTER=checkpoints/...`.
- Push to a Hugging Face Space; extend `answer()` toward the low-literacy
  health/civic assistant if time allows.
**Acceptance check:** a live URL that transcribes spoken Urdu; RTL output; works on
uploaded and mic audio.
**Claude Code prompt:** *"Prepare app/app.py for HF Spaces deployment: add a
requirements file for the Space, an app description, and a fallback to the base
model if no adapter is set."*

### Phase 5 — Paper & release (weeks 9–12)
**Goal:** the artifacts that convert this into a career differentiator.
**Steps:**
- HF dataset card + model card with metrics and limitations.
- GitHub README with repro instructions; tag a release.
- Write the paper (structure below); post to arXiv; submit to CHiPSAL/workshop.
- dev.to write-up + LinkedIn post.
**Acceptance check:** every §1 box ticked; preprint link live.
**Paper skeleton:** Abstract · Introduction (the Urdu conversational/code-switch
gap) · Related work (WER We Stand, Whisper/MMS/Seamless, Pashto CV) · Data (your
benchmark + collection protocol) · Normalization · Experiments (zero-shot vs LoRA,
per-model) · Results & error analysis (code-switch split, CI) · Limitations ·
Conclusion · Ethics & data statement.

---

## 10. Evaluation & audit framework

- **Metrics:** WER **and** CER (CER matters for Urdu script), always via
  `scoring_normalizer`, always split overall / code-switched / monolingual.
- **Significance:** bootstrap confidence interval on the headline WER (resample
  utterances ~1000×). Never report a single number with no spread.
- **Error analysis:** counts of insertions/deletions/substitutions; the most
  frequent wrong tokens; qualitative code-switch failure examples.
- **Reproducibility:** pinned deps, fixed seed, saved configs + raw per-utterance
  outputs in `results/`. A clean checkout + the commands must reproduce the tables.
- **Cards:** HF dataset card (license, provenance, splits, code-switch stats) and
  model card (base, data, metrics, intended use, limitations).

---

## 11. Deployment spec (the voice tool)

- **MVP:** mic/upload → fine-tuned Whisper → normalized Urdu transcript (RTL).
- **Stretch (assistant):** transcript → retrieval over a small curated Urdu
  health/civic FAQ → short spoken/text answer. Keeps the low-literacy-access story
  concrete and ties to your NexAura domain.
- **Host:** Hugging Face Space (Gradio). Set `BASE_MODEL` and `ADAPTER` env vars.

---

## 12. Reproducibility & audit checklist (run before "done")

- [ ] `pip install -r requirements.txt` on a clean env succeeds.
- [ ] `pytest -q` passes.
- [ ] Every metric in the paper is regenerable by a saved command in `results/`.
- [ ] Seeds fixed; configs logged; per-utterance outputs saved.
- [ ] Dataset + model cards complete with limitations and licensing.
- [ ] No data/checkpoints committed to git.
- [ ] Repo README lets a stranger reproduce Phase 0 and Phase 3.

---

## 13. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Transcription is slow (main bottleneck) | High | Keep the novel set small but pristine (≥3h); pre-fill + correct; lean on open corpora for training volume |
| fp16 NaNs during training | Medium | Lower LR, keep loss-scaling, smoke-test first |
| Free-GPU limits / timeouts | Medium | Whisper-small + LoRA; checkpoint each epoch; `--max-samples` for dev |
| Licensing of collected audio | Medium | Prefer CC sources; audio-less release if needed; document provenance |
| Scope creep (adding Sindhi/Pashto) | Medium | One language, one axis (code-switched conversational). Resist. |
| Weak WER improvement | Low–Med | The *benchmark + normalizer + analysis* are contributions even if gains are modest; report honestly |

---

## 14. Twelve-week timeline (parallel track, a few sessions/week)

| Week | Focus |
|---|---|
| 0 | Phase 0 baselines; env + tests green |
| 1–3 | Phase 1 data: open corpora + first collected/transcribed slice |
| 3–6 | Phase 2 fine-tuning (smoke test → real runs) |
| 6–9 | Phase 3 evaluation + Phase 4 deploy (parallel) |
| 9–12 | Phase 5 paper, cards, releases, posts |

---

## 15. Using this with Claude Code

1. Put this repo in an empty folder; open Claude Code there. It reads `CLAUDE.md`
   automatically for context and conventions.
2. Work phase by phase. Point Claude Code at a phase: *"Do §9 Phase 0."*
3. After any change to `normalize_urdu.py`, tell it to run `pytest -q`.
4. Keep runs small first (`--max-samples`, `--smoke-test`); scale once green.
5. Ask it to add each phase's **acceptance check** as it implements — that's how
   "fully audited / operational" actually happens.

---

## 16. References (starting points)

- Arif et al., *WER We Stand: Benchmarking Urdu ASR Models*, COLING 2025 — arXiv:2409.11252 (models, data, scripts released).
- *Benchmarking Whisper for Low-Resource Speech Recognition: N-Shot on Pashto, Punjabi, Urdu*, CHiPSAL 2025.
- Pashto Common Voice corpus + Whisper fine-tuning (open low-resource ASR precedent).
- Radford et al., *Whisper* (robust multilingual ASR).
- Pratap et al., *MMS: Scaling Speech Technology to 1000+ Languages*.
- Mozilla Common Voice; Google FLEURS (Conneau et al.).
