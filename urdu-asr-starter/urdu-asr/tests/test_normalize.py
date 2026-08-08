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
