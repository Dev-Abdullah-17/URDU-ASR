"""Tests for src/count_disfluency_tags.py (synthetic strings only)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from count_disfluency_tags import count  # noqa: E402


def test_count_tags_and_latin_tokens():
    c = count(["#um میں جا رہا ہوں", "اچھا #آہ ok ٹھیک", "سب ٹھیک ہے", "#um۔ پھر"])
    assert c["n_utts"] == 4
    assert c["tag_tokens"] == 3 and c["utts_with_tag"] == 3
    assert c["tags_latin_body"] == 2 and c["tags_arabic_body"] == 1 and c["tags_other_body"] == 0
    assert c["latin_tokens"] == 3 and c["latin_tokens_tag"] == 2 and c["latin_tokens_non_tag"] == 1


def test_lone_hash_is_not_a_tag():
    assert count(["نمبر # دو"])["tag_tokens"] == 0
