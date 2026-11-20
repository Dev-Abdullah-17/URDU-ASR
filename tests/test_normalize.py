"""Unit tests for the Urdu normalizer. Run: pytest -q"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from normalize_urdu import UrduNormalizer, is_code_switched  # noqa: E402

n = UrduNormalizer()


def test_arabic_yeh_to_urdu():
    assert n("\u064A") == "\u06CC"  # Arabic yeh -> Urdu yeh


def test_arabic_kaf_to_urdu():
    assert n("\u0643") == "\u06A9"  # Arabic kaf -> Urdu keheh


def test_digits_normalized():
    assert n("\u06F1\u06F2\u06F3") == "123"  # Urdu digits -> ASCII


def test_diacritics_stripped():
    assert n("\u0645\u064E") == "\u0645"  # meem + fatha -> meem


def test_whitespace_collapsed():
    assert n("a   b") == "a b"


def test_punct_removed_for_scoring():
    assert n("salam,   dosto!") == "salam dosto"


def test_code_switch_detection():
    assert is_code_switched("yeh ek meeting hai") is True
    assert is_code_switched("\u06CC\u06C1 \u0627\u06CC\u06A9") is False


# --- merge_hamza_madda -------------------------------------------------------

def test_alef_madda_preserved_by_default():
    assert n("آپ") == "آپ"          # aap ("you") must not become اپ
    assert n("آج") == "آج"          # aaj ("today")


def test_yeh_hamza_preserved_by_default():
    assert n("گئی") == "گئی"        # gayi ("went") must not become گیی
    assert n("آئے") == "آئے"        # aaye ("came")


def test_decomposed_yeh_hamza_not_stripped():
    # ی + combining hamza (U+0654) is canonicalised to ئ, not stripped to ی
    assert n("گیٔی") == "گئی"


def test_decomposed_alef_madda_composed():
    # ا + combining madda (U+0653) is NFC-composed to آ
    assert n("آپ") == "آپ"


def test_merge_hamza_madda_opt_in():
    m = UrduNormalizer(merge_hamza_madda=True)
    assert m("آپ") == "اپ"
    assert m("گئی") == "گیی"
    assert m("آئے") == "ایے"
