"""Urdu text normalization for ASR training and evaluation.

Addresses the "robust Urdu text normalization" gap flagged by Arif et al.
(WER We Stand, COLING 2025, arXiv:2409.11252). Used both to clean transcripts
before training and to normalize references + hypotheses before WER/CER scoring,
so that harmless orthographic variation is not counted as a recognition error.

Design goals:
- Deterministic and configurable (scoring vs. display may want different settings).
- Handle Arabic<->Urdu character confusables (a major source of spurious WER).
- Handle Urdu / Arabic-Indic digits, punctuation, diacritics, zero-width marks.
- Preserve code-switched Latin tokens (lowercased) rather than dropping them.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# Arabic -> Urdu canonical character map (common confusables).
_CHAR_MAP = {
    "\u064A": "\u06CC",  # Arabic yeh        -> Urdu yeh
    "\u0649": "\u06CC",  # Alef maksura      -> Urdu yeh
    "\u0643": "\u06A9",  # Arabic kaf        -> Urdu keheh
    "\u0629": "\u06C1",  # Teh marbuta       -> Urdu heh (goal)
    "\u0647": "\u06C1",  # Arabic heh        -> Urdu heh (goal)
    "\u06C3": "\u06C1",  # Teh marbuta goal  -> heh goal
    "\u0623": "\u0627",  # Alef + hamza above-> alef
    "\u0625": "\u0627",  # Alef + hamza below-> alef
    "\u0622": "\u0627",  # Alef + madda      -> alef
    "\u0624": "\u0648",  # Waw + hamza       -> waw
    "\u0626": "\u06CC",  # Yeh + hamza       -> yeh
}

# Urdu / Arabic-Indic digits -> ASCII.
_DIGIT_MAP = {
    "\u0660": "0", "\u0661": "1", "\u0662": "2", "\u0663": "3", "\u0664": "4",
    "\u0665": "5", "\u0666": "6", "\u0667": "7", "\u0668": "8", "\u0669": "9",
    "\u06F0": "0", "\u06F1": "1", "\u06F2": "2", "\u06F3": "3", "\u06F4": "4",
    "\u06F5": "5", "\u06F6": "6", "\u06F7": "7", "\u06F8": "8", "\u06F9": "9",
}

# Diacritics / harakat to strip (Arabic combining marks subset).
_DIACRITICS = "".join([
    "\u064B", "\u064C", "\u064D", "\u064E", "\u064F", "\u0650",
    "\u0651", "\u0652", "\u0653", "\u0654", "\u0655", "\u0670",
])

# Zero-width and directional formatting characters.
_ZERO_WIDTH = "".join(["\u200B", "\u200C", "\u200D", "\u200E", "\u200F", "\uFEFF"])

# Punctuation (Urdu + ASCII) removed for scoring.
_PUNCT = r"""!"#$%&'()*+,\-./:;<=>?@[\]^_`{|}~۔،؟؛«»…“”‘’"""

_DIAC_RE = re.compile(f"[{_DIACRITICS}]")
_ZW_RE = re.compile(f"[{_ZERO_WIDTH}]")
_PUNCT_RE = re.compile(f"[{re.escape(_PUNCT)}]")
_WS_RE = re.compile(r"\s+")


@dataclass
class UrduNormalizer:
    map_confusables: bool = True
    strip_diacritics: bool = True
    normalize_digits: bool = True
    remove_punct: bool = True     # True for scoring; often False for display
    lower_latin: bool = True
    collapse_whitespace: bool = True

    def __call__(self, text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize("NFC", text)          # 1. canonical compose
        text = _ZW_RE.sub("", text)                         # 2. drop zero-width
        if self.map_confusables:                            # 3. Arabic -> Urdu
            text = text.translate(str.maketrans(_CHAR_MAP))
        if self.strip_diacritics:                           # 4. strip harakat
            text = _DIAC_RE.sub("", text)
        if self.normalize_digits:                           # 5. digits -> ASCII
            text = text.translate(str.maketrans(_DIGIT_MAP))
        if self.lower_latin:                                # 6. lowercase Latin
            text = "".join(c.lower() if c.isascii() and c.isalpha() else c
                           for c in text)
        if self.remove_punct:                               # 7. drop punctuation
            text = _PUNCT_RE.sub(" ", text)
        if self.collapse_whitespace:                        # 8. collapse spaces
            text = _WS_RE.sub(" ", text).strip()
        return text


# Convenience singletons.
scoring_normalizer = UrduNormalizer(remove_punct=True)
display_normalizer = UrduNormalizer(remove_punct=False)


def is_code_switched(text: str, min_latin_chars: int = 2) -> bool:
    """Heuristic: utterance contains a run of Latin letters (English code-switch)."""
    latin = re.findall(r"[A-Za-z]+", text or "")
    return sum(len(w) for w in latin) >= min_latin_chars


if __name__ == "__main__":
    import sys

    normalizer = UrduNormalizer()
    for line in sys.stdin:
        print(normalizer(line.rstrip("\n")))
