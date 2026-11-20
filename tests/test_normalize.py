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


# --- digits_to_words ---------------------------------------------------------

from normalize_urdu import urdu_number_words  # noqa: E402

w = UrduNormalizer(digits_to_words=True)


def test_number_words_irregular_0_100():
    assert urdu_number_words(0) == "صفر"
    assert urdu_number_words(8) == "آٹھ"
    assert urdu_number_words(11) == "گیارہ"
    assert urdu_number_words(25) == "پچیس"
    assert urdu_number_words(49) == "انچاس"
    assert urdu_number_words(99) == "ننانوے"
    assert urdu_number_words(100) == "سو"


def test_number_words_hundreds_thousands():
    assert urdu_number_words(101) == "ایک سو ایک"
    assert urdu_number_words(350) == "تین سو پچاس"
    assert urdu_number_words(1000) == "ایک ہزار"
    assert urdu_number_words(2024) == "دو ہزار چوبیس"
    assert urdu_number_words(12345) == "بارہ ہزار تین سو پینتالیس"
    assert urdu_number_words(250000) == "دو لاکھ پچاس ہزار"


def test_digits_to_words_in_sentence():
    assert w("میں 25 سال کا ہوں") == "میں پچیس سال کا ہوں"
    assert w("۱۵ منٹ") == "پندرہ منٹ"                    # Urdu digits too
    assert w("1,500 روپے") == "ایک ہزار پانچ سو روپے"     # thousands separator
    assert w("2.5 کلو") == "دو اعشاریہ پانچ کلو"         # decimal


def test_digits_to_words_spacing_and_ordinals():
    assert w("صفحہ12پر") == "صفحہ بارہ پر"     # digits glued to letters get spaced
    assert w("5واں دن") == "پانچواں دن"         # ordinal suffix stays attached


def test_digits_to_words_off_by_default():
    assert n("میں 25 سال") == "میں 25 سال"


def test_digits_to_words_respects_hamza_merge():
    # number words containing ئ / آ follow the merge flag like any other word
    m = UrduNormalizer(digits_to_words=True, merge_hamza_madda=True)
    assert m("22") == "باییس"
    assert m("8") == "اٹھ"
    assert w("22") == "بائیس"


# --- latin_tokens ------------------------------------------------------------

import pytest  # noqa: E402


def test_latin_tokens_keep_default():
    assert n("کل Meeting ہے") == "کل meeting ہے"


def test_latin_tokens_drop():
    d = UrduNormalizer(latin_tokens="drop")
    assert d("کل Meeting ہے") == "کل ہے"
    assert d("یہ project بہت important ہے") == "یہ بہت ہے"
    assert d("e-mail بھیج دیں") == "بھیج دیں"      # punct split first, both parts dropped
    assert d("سب ٹھیک ہے") == "سب ٹھیک ہے"         # pure Urdu untouched


def test_latin_tokens_invalid_mode():
    with pytest.raises(ValueError):
        UrduNormalizer(latin_tokens="transliterate")


# --- code-switch detection ---------------------------------------------------

from normalize_urdu import (  # noqa: E402
    code_switch_method, find_loanwords, is_code_switched_extended,
)


def test_old_heuristic_misses_urdu_script_loanword():
    assert is_code_switched("کل میٹنگ ہے") is False   # the gap being fixed


def test_loanword_detected():
    assert find_loanwords("کل میٹنگ ہے") == ["میٹنگ"]
    assert code_switch_method("کل میٹنگ ہے") == "loanword"
    assert is_code_switched_extended("کل میٹنگ ہے") is True


def test_loanword_bigram():
    assert "ای میل" in find_loanwords("مجھے ای میل کر دیں")


def test_loanword_alef_madda_variant():
    # آفس written without madda still matches
    assert code_switch_method("وہ افس گیا") == "loanword"


def test_method_latin_and_both():
    assert code_switch_method("کل meeting ہے") == "latin"
    assert code_switch_method("meeting کے بعد آفس جاؤں گا") == "both"


def test_native_homographs_not_flagged():
    # بس ("enough"), سر ("head"), کار ("work") are native Urdu words
    assert code_switch_method("بس کرو میرا سر درد کر رہا ہے") == "none"
    assert code_switch_method("یہ میرا کاروبار ہے") == "none"
