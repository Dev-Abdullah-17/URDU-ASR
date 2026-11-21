"""Property-based (hypothesis) and edge-case tests for src/normalize_urdu.py.

Strategies generate Urdu-script text (Urdu letters, Arabic confusables, three
digit scripts, harakat, zero-width marks, Urdu/ASCII punctuation, Latin letters
and several kinds of whitespace), not only ASCII.

Properties that turned out to be false are kept as xfail(strict=True) tests with
the minimal counterexample, next to a passing test of the domain where the
property does hold.
"""

import dataclasses
import os
import re
import sys
import unicodedata

import pytest
from hypothesis import HealthCheck, assume, example, given, settings
from hypothesis import strategies as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import normalize_urdu as nu  # noqa: E402
import reeval_wws as rw  # noqa: E402
from normalize_urdu import (  # noqa: E402
    UrduNormalizer,
    code_switch_method,
    digits_to_urdu_words,
    find_loanwords,
    is_code_switched,
    scoring_normalizer,
    urdu_number_words,
)

# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #

URDU_LETTERS = "ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھءیےآئؤۂۓ"
ARABIC_CONFUSABLES = "يىكةهۃأإ"
LETTERS = URDU_LETTERS + ARABIC_CONFUSABLES
DIGITS = "0123456789" + "۰۱۲۳۴۵۶۷۸۹" + "٠١٢٣٤٥٦٧٨٩"
DIACRITICS = nu._DIACRITICS
ZERO_WIDTH = nu._ZERO_WIDTH
PUNCT = "۔،؟؛«»…“”‘’" + ".,!?\"'()-:;/[]#@"
LATIN = "abcdeklmotxyzABKOXZ"
WHITESPACE = " \t\n  "
ALPHABET = LETTERS + DIGITS + DIACRITICS + ZERO_WIDTH + PUNCT + LATIN + WHITESPACE

urdu_text = st.text(st.sampled_from(ALPHABET), max_size=40)
# Wider net: anything in the Arabic block (incl. marks not in _DIACRITICS) mixed
# with the curated alphabet.
wide_text = st.text(
    st.characters(min_codepoint=0x0600, max_codepoint=0x06FF) | st.sampled_from(ALPHABET),
    max_size=40,
)
urdu_word = st.text(st.sampled_from(URDU_LETTERS), min_size=1, max_size=8)
latin_word = st.text(st.sampled_from(LATIN), min_size=1, max_size=8)


def configs(strip_diacritics=st.booleans()):
    return st.builds(
        UrduNormalizer,
        strip_disfluency_tags=st.booleans(),
        map_confusables=st.booleans(),
        merge_hamza_madda=st.booleans(),
        strip_diacritics=strip_diacritics,
        normalize_digits=st.booleans(),
        digits_to_words=st.booleans(),
        remove_punct=st.booleans(),
        lower_latin=st.booleans(),
        latin_tokens=st.sampled_from(["keep", "drop"]),
        collapse_whitespace=st.booleans(),
    )


# Scoring presets: the module singleton plus every normalizer condition that
# reeval_wws scores with (N1..N8 and the hamza ablation).
_CONDS = rw.build_conditions(set(), "as_released~")
SCORING_KEEP = [("scoring_normalizer", scoring_normalizer)] + [
    (c.name, c.ref_fn) for c in _CONDS
    if isinstance(c.ref_fn, UrduNormalizer) and c.ref_fn.latin_tokens == "keep"]
SCORING_DROP = [(c.name, c.ref_fn) for c in _CONDS
                if isinstance(c.ref_fn, UrduNormalizer) and c.ref_fn.latin_tokens == "drop"]

FAST = settings(max_examples=200, deadline=None,
                suppress_health_check=[HealthCheck.too_slow])


def _is_arabic_letter(c: str) -> bool:
    return "؀" <= c <= "ۿ" and unicodedata.category(c) == "Lo"


# Spec of strip_disfluency_tags, written independently of the module's regex:
# a disfluency tag is "#" followed by a maximal run of non-whitespace characters.
TAG_RE = re.compile(r"#\S+")


def _outside_tags(x: str) -> str:
    """The part of x that strip_disfluency_tags keeps (tags -> one space)."""
    return TAG_RE.sub(" ", x)


def _has_letter_outside_tags(x: str) -> bool:
    return any(c in LETTERS for c in _outside_tags(x))


# Non-space run for generated tags: anything in the curated/Arabic alphabet
# that is not whitespace (incl. "#", digits, marks, zero-width, Latin).
tag_body = st.text(
    (st.characters(min_codepoint=0x0600, max_codepoint=0x06FF) | st.sampled_from(ALPHABET))
    .filter(lambda c: not c.isspace()),
    min_size=1, max_size=8)
tag_token = st.sampled_from(["#um", "#uh", "#آہ", "#اوں", "#ہمم", "##", "#a#b"]) | \
    tag_body.map(lambda b: "#" + b)


# --------------------------------------------------------------------------- #
# 1. Idempotence
# --------------------------------------------------------------------------- #

@FAST
@given(n=configs(strip_diacritics=st.just(True)), x=urdu_text)
def test_idempotent_all_flag_combinations_with_strip_diacritics(n, x):
    """Holds for every flag combination when strip_diacritics=True and the only
    combining marks in the input are the ones stripped (see xfails below)."""
    y = n(x)
    assert n(y) == y


@FAST
@given(n=configs(), x=urdu_text)
@example(n=UrduNormalizer(strip_diacritics=False), x="إٓ")
@example(n=scoring_normalizer, x="بٗ​ٖ")
@example(n=scoring_normalizer, x="e​́")
@pytest.mark.xfail(strict=True, reason=(
    "BUG normalize_urdu.py:177-190: NFC runs only at step 1, but later steps can "
    "leave non-NFC text, so a second pass changes it. "
    "(a) map_confusables, strip_diacritics=False: 'إٓ' (U+0625 U+0653) -> 'آ' "
    "decomposed (U+0627 U+0653) -> 2nd pass 'آ' (U+0622). "
    "(b) zero-width removal after NFC, scoring_normalizer: 'ب\\u0657\\u200b\\u0656' "
    "-> marks out of canonical order -> 2nd pass reorders them; "
    "'e\\u200b\\u0301' -> 'e\\u0301' -> 2nd pass 'é'."))
def test_idempotent_every_configuration_every_input(n, x):
    y = n(x)
    assert n(y) == y


@pytest.mark.xfail(strict=True, reason=(
    "BUG normalize_urdu.py:191-193: lowercasing after NFC can create a "
    "composable pair: scoring_normalizer('J\\u030c') = 'j\\u030c', "
    "scoring_normalizer('j\\u030c') = 'ǰ' (U+01F0)."))
def test_idempotent_after_lowercasing_latin_with_combining_mark():
    y = scoring_normalizer("J̌")
    assert scoring_normalizer(y) == y


@settings(max_examples=150, deadline=None)
@given(x=wide_text)
def test_scoring_presets_idempotent_on_arabic_block_without_zero_width(x):
    x = "".join(c for c in x if c not in ZERO_WIDTH)
    for _, n in SCORING_KEEP + SCORING_DROP:
        if n.strip_diacritics:
            y = n(x)
            assert n(y) == y


# --------------------------------------------------------------------------- #
# Output invariants
# --------------------------------------------------------------------------- #

@FAST
@given(n=configs(), x=wide_text)
def test_output_has_no_zero_width_chars(n, x):
    assert not any(c in ZERO_WIDTH for c in n(x))


@FAST
@given(n=configs(), x=wide_text)
def test_collapsed_output_has_clean_single_spaces(n, x):
    n.collapse_whitespace = True
    y = n(x)
    assert y == y.strip()
    assert "  " not in y
    assert all(c == " " or not c.isspace() for c in y)


@FAST
@given(n=configs(), x=wide_text)
def test_no_diacritics_when_stripped(n, x):
    n.strip_diacritics = True
    assert not any(c in DIACRITICS for c in n(x))


@FAST
@given(n=configs(), x=wide_text)
def test_no_punctuation_when_removed(n, x):
    n.remove_punct = True
    assert not any(c in nu._PUNCT for c in n(x))


@FAST
@given(n=configs(), x=wide_text)
def test_no_ascii_uppercase_when_lower_latin(n, x):
    n.lower_latin = True
    assert not any("A" <= c <= "Z" for c in n(x))


@FAST
@given(n=configs(), x=wide_text)
def test_no_latin_letters_when_dropped(n, x):
    n.latin_tokens = "drop"
    assert not any(c.isascii() and c.isalpha() for c in n(x))


@FAST
@given(n=configs(), x=urdu_text)
def test_eastern_digits_gone_when_normalized(n, x):
    n.normalize_digits = True
    assert not any(c in nu._DIGIT_MAP for c in n(x))


@FAST
@given(n=configs(), x=urdu_text)
def test_digits_to_words_leaves_no_digits(n, x):
    n.digits_to_words = True
    y = n(x)
    assert not any(c in "0123456789" for c in y)
    assert not any(c in nu._DIGIT_MAP for c in y)


@FAST
@given(n=configs(), x=urdu_text)
def test_confusables_absent_when_mapped(n, x):
    n.map_confusables = True
    y = n(x)
    assert not any(c in nu._CHAR_MAP for c in y)


@FAST
@given(n=configs(strip_diacritics=st.just(True)), x=urdu_text)
@example(n=UrduNormalizer(), x="هٔ")
@example(n=UrduNormalizer(), x="ىٔ")
@pytest.mark.xfail(strict=True, reason=(
    "BUG normalize_urdu.py:184-190: the yeh+hamza canonicalisation runs before "
    "the confusable map and there is no NFC afterwards, so an Arabic confusable "
    "followed by hamza loses the hamza while its Urdu counterpart keeps it: "
    "n('ه\\u0654') = 'ہ' but n('ہ\\u0654') = 'ۂ'; n('ى\\u0654') = 'ی' but "
    "n('ی\\u0654') = 'ئ'."))
def test_confusable_spelling_does_not_change_output(n, x):
    n.map_confusables = True
    assert n(x) == n(x.translate(nu._CHAR_TABLE))


@FAST
@given(x=urdu_text, zw=st.lists(st.sampled_from(ZERO_WIDTH), max_size=3))
def test_zero_width_between_letters_is_ignored(x, zw):
    letters = [c for c in x if c in LETTERS] or ["ب"]
    plain = "".join(letters)
    with_zw = "".join(c + "".join(zw) for c in letters)
    assert scoring_normalizer(with_zw) == scoring_normalizer(plain)


@FAST
@given(words=st.lists(urdu_word, min_size=1, max_size=6),
       seps=st.lists(st.text(st.sampled_from(WHITESPACE), min_size=1, max_size=3),
                     min_size=7, max_size=7))
def test_whitespace_variation_is_ignored(words, seps):
    messy = seps[0] + "".join(w + s for w, s in zip(words, seps[1:] + seps))
    assert scoring_normalizer(messy) == scoring_normalizer(" ".join(words))


@FAST
@given(words=st.lists(urdu_word, min_size=1, max_size=6),
       marks=st.lists(st.sampled_from(PUNCT), min_size=1, max_size=6))
def test_trailing_punctuation_is_ignored(words, marks):
    punctuated = " ".join(w + m for w, m in zip(words, marks * 6))
    assert scoring_normalizer(punctuated) == scoring_normalizer(" ".join(words))


@FAST
@given(x=urdu_text)
def test_flag_off_steps_are_noops(x):
    """With every optional step off, only NFC + zero-width removal apply."""
    n = UrduNormalizer(strip_disfluency_tags=False,
                       map_confusables=False, strip_diacritics=False,
                       normalize_digits=False, remove_punct=False,
                       lower_latin=False, collapse_whitespace=False)
    expected = nu._ZW_RE.sub("", unicodedata.normalize("NFC", x)).replace(
        nu._DECOMPOSED_YEH_HAMZA, "ئ")
    assert n(x) == expected


# --------------------------------------------------------------------------- #
# 3. Urdu letters never vanish
# --------------------------------------------------------------------------- #

@st.composite
def text_with_urdu_letter(draw):
    return draw(urdu_text) + draw(st.sampled_from(LETTERS)) + draw(urdu_text)


@st.composite
def text_with_urdu_letter_outside_tags(draw):
    """Urdu letter guaranteed outside every `#\\S+` token: a whitespace char
    before it ends any tag the prefix may have opened. Tags (generated and
    real) are mixed in so the tag case is exercised, not just avoided."""
    pre = draw(st.lists(urdu_text | tag_token, max_size=3)).copy()
    post = draw(st.lists(urdu_text | tag_token, max_size=3)).copy()
    ws = draw(st.sampled_from(WHITESPACE))
    letter = draw(st.sampled_from(LETTERS))
    return " ".join(pre) + ws + letter + draw(urdu_text) + " " + " ".join(post)


@FAST
@given(x=text_with_urdu_letter())
@example(x="#آ ب")          # letter after a tag survives
@example(x="ب#آ")           # tag glued after a word: only the tag goes
def test_urdu_letter_never_normalizes_to_empty_keep(x):
    """Intended invariant: under every keep-Latin scoring preset, an Urdu letter
    outside any `#\\S+` disfluency tag survives normalization. Letters inside a
    tag are removed by design when strip_disfluency_tags is on (N-conditions),
    so that case is excluded explicitly by assume() -- see
    test_urdu_letters_only_inside_tags_normalize_to_empty for it."""
    assume(_has_letter_outside_tags(x))
    for name, n in SCORING_KEEP:
        y = n(x)
        assert y, name
        assert any(_is_arabic_letter(c) for c in y), name


@FAST
@given(x=text_with_urdu_letter_outside_tags())
def test_urdu_letter_outside_tags_never_normalizes_to_empty_keep(x):
    assert _has_letter_outside_tags(x)          # by construction
    for name, n in SCORING_KEEP:
        y = n(x)
        assert y, name
        assert any(_is_arabic_letter(c) for c in y), name


@FAST
@given(x=text_with_urdu_letter())
def test_urdu_letter_never_normalizes_to_empty_without_tag_stripping(x):
    """Without strip_disfluency_tags the original, unrestricted property holds."""
    for name, n in SCORING_KEEP:
        n = dataclasses.replace(n, strip_disfluency_tags=False)
        y = n(x)
        assert y, name
        assert any(_is_arabic_letter(c) for c in y), name


@pytest.mark.parametrize("x", ["#آ", "#آہ", "  #ہمم\t#اوں ", "#um #آہ۔"])
def test_urdu_letters_only_inside_tags_normalize_to_empty(x):
    for name, n in SCORING_KEEP + SCORING_DROP:
        if n.strip_disfluency_tags:
            assert n(x) == "", name
        else:
            assert n(x) != "", name


@FAST
@given(urdu=st.lists(urdu_word, min_size=1, max_size=5),
       latin=st.lists(latin_word, max_size=5), data=st.data())
def test_latin_drop_keeps_urdu_tokens(urdu, latin, data):
    toks = data.draw(st.permutations(urdu + latin))
    x = " ".join(toks)
    keep_only_urdu = " ".join(t for t in toks if t in urdu)
    for name, n in SCORING_DROP:
        y = n(x)
        assert y == n(keep_only_urdu), name
        assert y, name


@FAST
@given(x=text_with_urdu_letter())
@example(x="آپok")
@pytest.mark.xfail(strict=True, reason=(
    "By design latin_tokens='drop' drops whole whitespace tokens containing a "
    "Latin letter, so Urdu letters glued to Latin letters vanish: "
    "N8_latin_drop('آپok') == ''. Not a crash bug, but the 'Urdu letters "
    "survive drop' property is false for mixed-script tokens."))
def test_urdu_letter_survives_latin_drop_any_text(x):
    assume(_has_letter_outside_tags(x))       # tag case is removed by design, not this bug
    for name, n in SCORING_DROP:
        assert any(_is_arabic_letter(c) for c in n(x)), name


def test_latin_drop_mixed_token_edge_cases():
    n = dict(SCORING_DROP)["N8_latin_drop"]
    assert n("آپok") == ""                      # glued: whole token dropped
    assert n("آپ ok") == "آپ"
    assert n("آپ.ok") == "آپ"                   # punctuation splits the token first


# --------------------------------------------------------------------------- #
# strip_disfluency_tags
# --------------------------------------------------------------------------- #

# Inputs that contain tags: free text, tag tokens and tags glued to text.
text_with_tags = st.lists(wide_text | tag_token, max_size=6).map("".join) | \
    st.lists(wide_text | tag_token, max_size=6).map(" ".join)


def _tag_on(n):
    return dataclasses.replace(n, strip_disfluency_tags=True)


@FAST
@given(n=configs(), x=text_with_tags)
def test_no_tag_left_when_stripping(n, x):
    """(a) No "#" followed by a non-space character survives, under every flag
    combination (remove_punct=False keeps bare "#" but never a tag)."""
    y = _tag_on(n)(x)
    assert not TAG_RE.search(y)


@FAST
@given(n=configs(), x=wide_text, tag=tag_token, data=st.data())
def test_inserting_tag_at_token_boundary_does_not_change_output(n, x, tag, data):
    """(b) A whitespace-delimited tag inserted at a token boundary is invisible.
    Needs collapse_whitespace: the tag is replaced by a space, so without
    collapsing the output keeps the extra whitespace by design."""
    n = dataclasses.replace(n, strip_disfluency_tags=True, collapse_whitespace=True)
    bounds = [i for i in range(len(x) + 1)
              if i in (0, len(x)) or x[i - 1].isspace() or x[i].isspace()]
    i = data.draw(st.sampled_from(bounds))
    x2 = x[:i] + " " + tag + " " + x[i:]
    assert n(x2) == n(x)


@FAST
@given(words=st.lists(urdu_word | latin_word, min_size=1, max_size=6),
       tags=st.lists(tag_token, min_size=1, max_size=4), data=st.data())
def test_tags_between_real_words_are_ignored_by_n_conditions(words, tags, data):
    toks = list(words)
    for t in tags:
        toks.insert(data.draw(st.integers(0, len(toks))), t)
    for c in _CONDS:
        if isinstance(c.ref_fn, UrduNormalizer):
            assert c.ref_fn(" ".join(toks)) == c.ref_fn(" ".join(words)), c.name


@pytest.mark.parametrize("x, expected", [
    ("#um آپ کیسے ہیں", "آپ کیسے ہیں"),
    ("آپ #آہ کیسے #uh ہیں", "آپ کیسے ہیں"),
    ("ہاں #ہمم۔ ٹھیک ہے", "ہاں ٹھیک ہے"),      # punctuation glued to the tag goes with it
    ("ہاں # ٹھیک", "ہاں ٹھیک"),               # bare "#" is not a tag; removed as punct
    ("ہاں#um ٹھیک", "ہاں ٹھیک"),              # tag glued after a word: only the tag goes
    ("#um", ""),
])
def test_strip_disfluency_tags_examples(x, expected):
    n = dict((c.name, c.ref_fn) for c in _CONDS)["N7_numwords"]
    assert n(x) == expected


@FAST
@given(n=configs(), x=wide_text)
def test_strip_disfluency_tags_noop_without_hash(n, x):
    """(c) On inputs with no "#" the flag changes nothing."""
    x = x.replace("#", "")
    on = dataclasses.replace(n, strip_disfluency_tags=True)
    off = dataclasses.replace(n, strip_disfluency_tags=False)
    assert on(x) == off(x)


@FAST
@given(n=configs(strip_diacritics=st.just(True)), x=st.lists(urdu_text | tag_token,
                                                            max_size=5).map(" ".join))
def test_idempotent_with_tag_stripping(n, x):
    """(d) Idempotence with the flag on, in the domain where it held before
    (strip_diacritics=True, curated alphabet), now with tags mixed in."""
    n = _tag_on(n)
    y = n(x)
    assert n(y) == y


@settings(max_examples=150, deadline=None)
@given(x=text_with_tags)
def test_scoring_presets_idempotent_with_tags(x):
    x = "".join(c for c in x if c not in ZERO_WIDTH)
    for name, n in SCORING_KEEP + SCORING_DROP:
        if n.strip_diacritics:
            y = n(x)
            assert n(y) == y, name


# --------------------------------------------------------------------------- #
# Numbers
# --------------------------------------------------------------------------- #

def test_urdu_number_words_injective_0_to_999999():
    words = [urdu_number_words(i) for i in range(1_000_000)]
    assert len(set(words)) == len(words)


@settings(max_examples=300, deadline=None)
@given(a=st.integers(0, 10**12), b=st.integers(0, 10**12))
def test_urdu_number_words_injective_large(a, b):
    assume(a != b)
    assert urdu_number_words(a) != urdu_number_words(b)


@settings(max_examples=300, deadline=None)
@given(k=st.integers(0, 10**12))
def test_urdu_number_words_are_urdu_tokens_only(k):
    w = urdu_number_words(k)
    assert w == w.strip() and "  " not in w
    assert all(_is_arabic_letter(c) or c == " " for c in w)
    assert scoring_normalizer(w) == w        # number words are already normalized


def test_urdu_number_words_edges():
    assert urdu_number_words(0) == "صفر"
    assert urdu_number_words(100) == "سو"
    assert urdu_number_words(101) == "ایک سو ایک"
    assert urdu_number_words(1000) == "ایک ہزار"
    assert urdu_number_words(100_000) == "ایک لاکھ"
    assert urdu_number_words(10**7) == "ایک کروڑ"
    assert urdu_number_words(10**9 - 1).split()[-1] == "ننانوے"
    assert urdu_number_words(10**9) == "ایک " + " ".join(["صفر"] * 9)
    with pytest.raises(ValueError):
        urdu_number_words(-1)


@FAST
@given(x=st.text(st.sampled_from(LETTERS + "0123456789 ,.-"), max_size=40))
def test_digits_to_urdu_words_removes_ascii_digits(x):
    assert not any(c in "0123456789" for c in digits_to_urdu_words(x))


@FAST
@given(x=st.text(st.characters(categories=["Nd"]) | st.sampled_from(LETTERS + " ,."),
                 max_size=30))
def test_digits_to_urdu_words_removes_all_unicode_digits(x):
    assert not any(unicodedata.category(c) == "Nd" for c in digits_to_urdu_words(x))


@pytest.mark.xfail(strict=True, raises=ValueError, reason=(
    "BUG normalize_urdu.py:112: int(whole) raises ValueError ('Exceeds the limit "
    "(4300 digits) for integer string conversion') for a digit run longer than "
    "sys.get_int_max_str_digits(), so UrduNormalizer(digits_to_words=True) "
    "crashes on '1' * 5000 instead of reading it digit by digit."))
def test_digits_to_words_very_long_digit_run_does_not_crash():
    y = UrduNormalizer(digits_to_words=True)("1" * 5000)
    assert y.split() == ["ایک"] * 5000


@FAST
@given(k=st.integers(0, 10**9 - 1))
def test_digits_to_urdu_words_matches_number_words(k):
    assert digits_to_urdu_words(str(k)) == urdu_number_words(k)
    assert digits_to_urdu_words(f"{k:,}") == urdu_number_words(k)


@pytest.mark.parametrize("src, expected", [
    ("25", "پچیس"),
    ("1,000", "ایک ہزار"),
    ("2.5", "دو اعشاریہ پانچ"),
    ("5واں", "پانچواں"),                 # attached ordinal suffix stays attached
    ("21ویں", "اکیسویں"),
    ("کل3بجے", "کل تین بجے"),            # spaced from neighbouring letters
    ("۲۵", "پچیس"),                       # re's \d matches any Unicode digit
    ("२५", "پچیس"),                       # ... including Devanagari
])
def test_digits_to_urdu_words_examples(src, expected):
    assert digits_to_urdu_words(src) == expected


def test_digits_to_words_handles_eastern_digits_via_normalizer():
    n = UrduNormalizer(digits_to_words=True)
    assert n("۲۵ روپے") == n("25 روپے") == n("٢٥ روپے") == "پچیس روپے"


def test_digits_to_urdu_words_drops_leading_zeros():
    # Observation (not asserted as a bug): leading zeros are not spoken, so
    # "007" and "7" normalize identically; phone numbers lose their leading 0.
    assert digits_to_urdu_words("007") == digits_to_urdu_words("7") == "سات"


# --------------------------------------------------------------------------- #
# Code-switch detection
# --------------------------------------------------------------------------- #

@FAST
@given(x=urdu_text)
def test_code_switch_method_consistent_with_detectors(x):
    m = code_switch_method(x)
    assert m in {"latin", "loanword", "both", "none"}
    assert (m in {"latin", "both"}) == is_code_switched(x)
    assert (m in {"loanword", "both"}) == bool(find_loanwords(x))


@FAST
@given(x=urdu_text)
def test_find_loanwords_returns_known_normalized_entries(x):
    for hit in find_loanwords(x):
        assert hit in nu._LOAN_TOKENS or hit in nu._LOAN_BIGRAMS


@FAST
@given(words=st.lists(urdu_word, max_size=4),
       loan=st.sampled_from(sorted(nu.URDU_SCRIPT_LOANWORDS)),
       data=st.data())
def test_loanword_detected_anywhere_in_urdu_sentence(words, loan, data):
    pos = data.draw(st.integers(0, len(words)))
    sent = " ".join(words[:pos] + [loan] + words[pos:])
    assert nu._LOAN_NORM(loan) in find_loanwords(sent)
    assert code_switch_method(sent) in {"loanword", "both"}


@FAST
@given(phrase=st.sampled_from(sorted(nu.URDU_SCRIPT_LOAN_PHRASES)))
def test_loan_phrase_detected_as_bigram(phrase):
    assert nu._LOAN_NORM(phrase) in find_loanwords("میں " + phrase + " پر ہوں")


@pytest.mark.parametrize("text, method", [
    ("آج میٹنگ ہے", "loanword"),
    ("آج میٹنگ۔", "loanword"),             # punctuation stripped before matching
    ("اج افس جانا ہے", "loanword"),        # آ/ا variant matched via hamza merge
    ("meeting کب ہے", "latin"),
    ("meeting اور میٹنگ", "both"),
    ("آپ کیسے ہیں", "none"),
    ("بس کرو", "none"),                    # native word excluded from list
    ("a ہے", "none"),                       # one Latin char < min_latin_chars
    ("", "none"),
])
def test_code_switch_method_examples(text, method):
    assert code_switch_method(text) == method


def test_normalizer_edge_cases():
    assert scoring_normalizer("") == ""
    assert scoring_normalizer(" \t\n​‌ ") == ""
    assert scoring_normalizer("۔،؟") == ""
    assert scoring_normalizer("گئی") == scoring_normalizer("گیٔی") == "گئی"
    assert scoring_normalizer("آپ") == "آپ"                       # madda kept by default
    assert UrduNormalizer(merge_hamza_madda=True)("آپ") == "اپ"
    assert scoring_normalizer("Hello, دنیا!") == "hello دنیا"
    with pytest.raises(ValueError):
        UrduNormalizer(latin_tokens="remove")
