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
}

# Alef madda, yeh-hamza and waw-hamza are *distinct letters* in Urdu, not
# confusables: merging them rewrites real words (آپ -> اپ, گئی -> گیی,
# آئے -> ایے, جاؤ -> جاو) and can
# hide genuine recognition errors. Only applied when merge_hamza_madda=True.
_HAMZA_MADDA_MAP = {
    "\u0622": "\u0627",  # Alef + madda      -> alef   (آ -> ا)
    "\u0626": "\u06CC",  # Yeh + hamza       -> yeh    (ئ -> ی)
    "\u0624": "\u0648",  # Waw + hamza       -> waw    (ؤ -> و)
}

# NFC does not compose Urdu yeh (U+06CC) + combining hamza above (U+0654) into
# U+0626, so a decomposed گئی would otherwise lose its hamza in diacritic
# stripping. Canonicalise it to the precomposed letter first.
_DECOMPOSED_YEH_HAMZA = "\u06CC\u0654"

# Urdu / Arabic-Indic digits -> ASCII.
_DIGIT_MAP = {
    "\u0660": "0", "\u0661": "1", "\u0662": "2", "\u0663": "3", "\u0664": "4",
    "\u0665": "5", "\u0666": "6", "\u0667": "7", "\u0668": "8", "\u0669": "9",
    "\u06F0": "0", "\u06F1": "1", "\u06F2": "2", "\u06F3": "3", "\u06F4": "4",
    "\u06F5": "5", "\u06F6": "6", "\u06F7": "7", "\u06F8": "8", "\u06F9": "9",
}

# Urdu cardinal number words 0-100. Urdu numbers below 100 are irregular, so
# they are listed in full (common spellings; one canonical form each).
_URDU_NUMS = (
    "صفر ایک دو تین چار پانچ چھ سات آٹھ نو "                       # 0-9
    "دس گیارہ بارہ تیرہ چودہ پندرہ سولہ سترہ اٹھارہ انیس "        # 10-19
    "بیس اکیس بائیس تئیس چوبیس پچیس چھبیس ستائیس اٹھائیس انتیس "  # 20-29
    "تیس اکتیس بتیس تینتیس چونتیس پینتیس چھتیس سینتیس اڑتیس انتالیس "  # 30-39
    "چالیس اکتالیس بیالیس تینتالیس چوالیس پینتالیس چھیالیس سینتالیس اڑتالیس انچاس "  # 40-49
    "پچاس اکاون باون ترپن چوون پچپن چھپن ستاون اٹھاون انسٹھ "     # 50-59
    "ساٹھ اکسٹھ باسٹھ ترسٹھ چونسٹھ پینسٹھ چھیاسٹھ سڑسٹھ اڑسٹھ انہتر "  # 60-69
    "ستر اکہتر بہتر تہتر چوہتر پچہتر چھہتر ستتر اٹھہتر اناسی "     # 70-79
    "اسی اکیاسی بیاسی تراسی چوراسی پچاسی چھیاسی ستاسی اٹھاسی نواسی "  # 80-89
    "نوے اکیانوے بانوے ترانوے چورانوے پچانوے چھیانوے ستانوے اٹھانوے ننانوے "  # 90-99
    "سو"                                                            # 100
).split()
assert len(_URDU_NUMS) == 101
_HUNDRED, _THOUSAND, _LAKH, _CRORE = "سو", "ہزار", "لاکھ", "کروڑ"
_DECIMAL_POINT = "اعشاریہ"
_MAX_SPOKEN = 10**9 - 1   # up to 99 crore ...; longer strings read digit-by-digit


def urdu_number_words(n: int) -> str:
    """Spell a non-negative integer in Urdu words (South-Asian grouping).

    0-100 come from the table (100 -> "سو"); 101-999 use "<n> سو <rest>"
    (e.g. 101 -> "ایک سو ایک", 350 -> "تین سو پچاس"); then ہزار (10^3),
    لاکھ (10^5) and کروڑ (10^7). Numbers > _MAX_SPOKEN are read digit by digit.
    """
    if n < 0:
        raise ValueError("negative numbers not supported")
    if n <= 100:
        return _URDU_NUMS[n]
    if n > _MAX_SPOKEN:
        return " ".join(_URDU_NUMS[int(d)] for d in str(n))
    parts = []
    for size, word in ((10**7, _CRORE), (10**5, _LAKH), (10**3, _THOUSAND)):
        if n >= size:
            parts += [urdu_number_words(n // size), word]
            n %= size
    if n >= 100:
        parts += [_URDU_NUMS[n // 100], _HUNDRED]
        n %= 100
    if n:
        parts.append(_URDU_NUMS[n])
    return " ".join(parts)


# A number: digits with optional thousands separators and an optional decimal
# part. Applied after digits have been mapped to ASCII.
_NUMBER_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
# Ordinal suffixes that attach directly to a number (5واں -> پانچواں).
_ORDINAL_SUFFIX_RE = re.compile(r"(?:واں|ویں|وی)")


def _spell_number(token: str) -> str:
    whole, _, frac = token.replace(",", "").partition(".")
    digits = whole.lstrip("0") or "0"
    if len(digits) > len(str(_MAX_SPOKEN)):
        # read digit by digit without int(): Python refuses int() on strings
        # longer than sys.get_int_max_str_digits() (4300 by default)
        words = " ".join(_URDU_NUMS[int(d)] for d in digits)
    else:
        words = urdu_number_words(int(digits))
    if frac:
        words += " " + _DECIMAL_POINT + " " + " ".join(_URDU_NUMS[int(d)] for d in frac)
    return words


def digits_to_urdu_words(text: str) -> str:
    """Replace ASCII digit sequences with Urdu number words, space-separated
    from neighbouring letters (except a directly attached ordinal suffix)."""
    def repl(m: re.Match) -> str:
        words = _spell_number(m.group(0))
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end():]
        pre = "" if before.isspace() else " "
        post = "" if (not after or after[0].isspace()
                      or _ORDINAL_SUFFIX_RE.match(after)) else " "
        return pre + words + post
    return _NUMBER_RE.sub(repl, text)


# Diacritics / harakat to strip (Arabic combining marks subset).
_DIACRITICS = "".join([
    "\u064B", "\u064C", "\u064D", "\u064E", "\u064F", "\u0650",
    "\u0651", "\u0652", "\u0653", "\u0654", "\u0655", "\u0670",
])

# Zero-width and directional formatting characters.
_ZERO_WIDTH = "".join(["\u200B", "\u200C", "\u200D", "\u200E", "\u200F", "\uFEFF"])

# Punctuation (Urdu + ASCII) removed for scoring.
_PUNCT = r"""!"#$%&'()*+,\-./:;<=>?@[\]^_`{|}~۔،؟؛«»…“”‘’"""

# Disfluency tags as emitted by Seamless-M4T (e.g. "#um", "#آہ"): a "#" followed
# by non-space characters. Removed as a whole token by strip_disfluency_tags.
_DISFLUENCY_TAG_RE = re.compile(r"#\S+")

_CHAR_TABLE = str.maketrans(_CHAR_MAP)
_DIGIT_TABLE = str.maketrans(_DIGIT_MAP)
_HAMZA_MADDA_TABLE = str.maketrans(_HAMZA_MADDA_MAP)
_DIAC_RE = re.compile(f"[{_DIACRITICS}]")
_ZW_RE = re.compile(f"[{_ZERO_WIDTH}]")
_PUNCT_RE = re.compile(f"[{re.escape(_PUNCT)}]")
_WS_RE = re.compile(r"\s+")


_LATIN_TOKEN_MODES = ("keep", "drop")
_LATIN_TOKEN_RE = re.compile(r"\S*[A-Za-z]\S*")


@dataclass
class UrduNormalizer:
    strip_disfluency_tags: bool = False  # drop "#\S+" tags (Seamless disfluencies) first
    map_confusables: bool = True
    merge_hamza_madda: bool = False  # آ->ا, ئ->ی, ؤ->و (lossy; off by default)
    strip_diacritics: bool = True
    normalize_digits: bool = True
    digits_to_words: bool = False    # 25 -> پچیس (WER We Stand refs spell numbers out)
    remove_punct: bool = True     # True for scoring; often False for display
    lower_latin: bool = True
    latin_tokens: str = "keep"      # "keep" | "drop": drop tokens with Latin letters
    collapse_whitespace: bool = True

    def __post_init__(self):
        if self.latin_tokens not in _LATIN_TOKEN_MODES:
            raise ValueError(f"latin_tokens must be one of {_LATIN_TOKEN_MODES}, "
                             f"got {self.latin_tokens!r}")

    # Upper bound on passes in __call__; real text converges after 1-2.
    _MAX_PASSES = 4

    def __call__(self, text: str) -> str:
        """Normalize `text`. Idempotent: the single-pass pipeline is re-applied
        until the output stops changing (later steps such as Latin lowercasing
        or the confusable map can otherwise leave text that a second pass would
        change, e.g. via NFC recomposition)."""
        if not text:
            return ""
        for _ in range(self._MAX_PASSES):
            out = self._one_pass(text)
            if out == text:
                break
            text = out
        return text

    def _one_pass(self, text: str) -> str:
        if self.strip_disfluency_tags:                      # 0. drop "#um"-style tags
            text = _DISFLUENCY_TAG_RE.sub(" ", text)
        text = _ZW_RE.sub("", text)                         # 1. drop zero-width (before
        text = unicodedata.normalize("NFC", text)          #    NFC so marks recompose)
        if self.normalize_digits or self.digits_to_words:   # 2. digits -> ASCII
            text = text.translate(_DIGIT_TABLE)
        if self.digits_to_words:                            # 3. digits -> words
            text = digits_to_urdu_words(text)               #    (before char maps,
                                                            #    so words get mapped too)
        if self.map_confusables:                            # 4. Arabic -> Urdu
            text = text.translate(_CHAR_TABLE)
        # 4b. compose hamza AFTER the confusable map, so Arabic and Urdu
        # spellings agree (ه+ٔ -> ہ+ٔ -> ۂ; ى+ٔ -> ی+ٔ -> ئ)
        text = text.replace(_DECOMPOSED_YEH_HAMZA, "\u0626")
        text = unicodedata.normalize("NFC", text)
        if self.merge_hamza_madda:                          # 5. آ->ا, ئ->ی, ؤ->و
            text = text.translate(_HAMZA_MADDA_TABLE)
        if self.strip_diacritics:                           # 6. strip harakat
            text = _DIAC_RE.sub("", text)
        if self.lower_latin:                                # 7. lowercase Latin
            text = "".join(c.lower() if c.isascii() and c.isalpha() else c
                           for c in text)
        if self.remove_punct:                               # 8. drop punctuation
            text = _PUNCT_RE.sub(" ", text)
        if self.latin_tokens == "drop":                     # 8b. drop Latin tokens
            text = _LATIN_TOKEN_RE.sub(" ", text)
        if self.collapse_whitespace:                        # 9. collapse spaces
            text = _WS_RE.sub(" ", text).strip()
        return unicodedata.normalize("NFC", text)          # 10. final canonical form


# Convenience singletons.
scoring_normalizer = UrduNormalizer(remove_punct=True)
display_normalizer = UrduNormalizer(remove_punct=False)


def is_code_switched(text: str, min_latin_chars: int = 2) -> bool:
    """Original heuristic: utterance contains a run of Latin letters.

    Kept unchanged for comparison. It misses English written in Urdu script
    (e.g. میٹنگ), which is how most Urdu transcripts encode code-switching;
    see `code_switch_method` for the extended detector.
    """
    latin = re.findall(r"[A-Za-z]+", text or "")
    return sum(len(w) for w in latin) >= min_latin_chars


# English loanwords commonly written in Urdu script in conversational speech.
# Deliberately small and conservative: words that are also native Urdu words
# (بس "enough", کال "time/famine", سر "head", کار "work") are excluded, as are
# long-assimilated words that are not perceived as switching (ڈاکٹر, سکول,
# ہسپتال, ٹرین). Spelling variants are listed explicitly. Matching is done after
# normalising both sides with merge_hamza_madda=True, so آ/ا and ئ/ی variants
# also match. Extend this list as the benchmark grows.
URDU_SCRIPT_LOANWORDS = frozenset("""
میٹنگ آفس آفیس کمپیوٹر لیپٹاپ موبائل فون ٹائم پلیز سوری تھینک تھینکس تھینکیو
اوکے پرابلم سسٹم پروگرام پراجیکٹ پروجیکٹ رپورٹ میسج میسیج ٹیکسٹ ویڈیو انٹرنیٹ
آنلائن ویبسائٹ کمپنی مینیجر منیجر باس بزنس مارکیٹ کلاس ٹیچر میڈم ٹیسٹ ریزلٹ
اسائنمنٹ ڈیڈلائن فائل ڈیٹا سافٹویئر ایپ ایپلیکیشن سپورٹ ٹیم پلان پلاننگ آئیڈیا
ریسٹورنٹ شاپنگ ٹینشن فرینڈ فرینڈز فیملی ہیلو بائے گڈ ویری ریئلی ایکچوئلی ایکچولی
بیسیکلی ویکینڈ ڈیپارٹمنٹ پریزنٹیشن جاب آفر سیلری انٹرویو کانفرنس ایونٹ پارٹی
لیول پرسنٹ پرسنٹیج ٹاپک سبجیکٹ ایکسپیرینس ڈسکس ڈسکشن مینیج کنفرم اپڈیٹ
""".split())

# Two-token spellings of loanwords (matched as token bigrams).
URDU_SCRIPT_LOAN_PHRASES = frozenset({
    "لیپ ٹاپ", "ای میل", "آن لائن", "ویب سائٹ", "ڈیڈ لائن", "سافٹ ویئر",
    "ویک اینڈ", "بیک گراؤنڈ", "اپ ڈیٹ",
})

_LOAN_NORM = UrduNormalizer(merge_hamza_madda=True)
_LOAN_TOKENS = frozenset(_LOAN_NORM(w) for w in URDU_SCRIPT_LOANWORDS)
_LOAN_BIGRAMS = frozenset(_LOAN_NORM(p) for p in URDU_SCRIPT_LOAN_PHRASES)


def find_loanwords(text: str) -> list[str]:
    """Return Urdu-script English loanwords (normalised) found in `text`."""
    toks = _LOAN_NORM(text or "").split()
    hits = [" ".join(toks[i:i + 2]) for i in range(len(toks) - 1)
            if " ".join(toks[i:i + 2]) in _LOAN_BIGRAMS]
    hits += [t for t in toks if t in _LOAN_TOKENS]
    return hits


def code_switch_method(text: str, min_latin_chars: int = 2) -> str:
    """Which detector flags `text` as code-switched.

    Returns "latin" (original Latin-letter heuristic only), "loanword"
    (Urdu-script loanword list only), "both", or "none".
    """
    latin = is_code_switched(text, min_latin_chars)
    loan = bool(find_loanwords(text))
    return {(True, True): "both", (True, False): "latin",
            (False, True): "loanword", (False, False): "none"}[(latin, loan)]


def is_code_switched_extended(text: str, min_latin_chars: int = 2) -> bool:
    """Latin-letter heuristic OR Urdu-script loanword list."""
    return code_switch_method(text, min_latin_chars) != "none"


if __name__ == "__main__":
    import sys

    normalizer = UrduNormalizer()
    for line in sys.stdin:
        print(normalizer(line.rstrip("\n")))
