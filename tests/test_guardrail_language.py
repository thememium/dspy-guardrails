"""Tests for the Language guardrail and its Unicode-script prefilter.

The prefilter is fully deterministic, so most tests can run without
invoking the DSPy LLM.  The few tests that exercise the DSPy fallback
rely on the session-scoped ``configure_guardrails`` fixture in
``conftest.py`` and mock the LLM call for isolation.
"""

from unittest.mock import MagicMock, patch

import pytest

from dspy_guardrails import guardrail
from dspy_guardrails.core.base import BaseGuardrail
from dspy_guardrails.guardrails.language import (
    _COMPILED_SCRIPT_CATALOG,
    SCRIPT_TO_LANG_CODES,
    _detect_dominant_script,
)

# --------------------------------------------------------------------------- #
# Construction / config                                                        #
# --------------------------------------------------------------------------- #


def test_language_guardrail_type():
    guard = guardrail.Language(allowed_languages=["en", "es"])

    assert isinstance(guard, BaseGuardrail)
    assert guard.name == "language"
    assert guard.config.allowed_languages == ["en", "es"]


def test_script_catalog_precomputed():
    """Script catalog must be compiled at construction time."""
    guard = guardrail.Language(allowed_languages=["en"])

    assert hasattr(guard, "_script_catalog")
    assert len(guard._script_catalog) == len(SCRIPT_TO_LANG_CODES)
    for name, pattern, codes in guard._script_catalog:
        assert isinstance(name, str)
        assert hasattr(pattern, "search")  # compiled regex
        assert isinstance(codes, tuple)


def test_script_prefilter_enabled_by_default():
    guard = guardrail.Language(allowed_languages=["en"])
    assert guard.config.enable_script_prefilter is True


def test_script_catalog_module_level_compiled():
    """Module-level catalog must already be compiled."""
    assert len(_COMPILED_SCRIPT_CATALOG) == len(SCRIPT_TO_LANG_CODES)
    for name, pat, codes in _COMPILED_SCRIPT_CATALOG:
        assert hasattr(pat, "search")


# --------------------------------------------------------------------------- #
# _detect_dominant_script helper                                               #
# --------------------------------------------------------------------------- #


def test_detect_dominant_script_han():
    text = "这是一段中文文本，用来测试汉字检测功能是否正常工作。"
    assert _detect_dominant_script(text) == "han"


def test_detect_dominant_script_cyrillic():
    text = "Это текст на русском языке для проверки кириллического скрипта."
    assert _detect_dominant_script(text) == "cyrillic"


def test_detect_dominant_script_latin_returns_none():
    text = "This is plain English text with no non-Latin characters."
    assert _detect_dominant_script(text) is None


def test_detect_dominant_script_empty_returns_none():
    assert _detect_dominant_script("") is None


def test_detect_dominant_script_arabic():
    text = "هذا نص باللغة العربية لاختبار الكشف عن النص العربي"
    assert _detect_dominant_script(text) == "arabic"


def test_detect_dominant_script_hangul():
    text = "이것은 한국어 텍스트입니다 한글 감지 테스트를 위한 문장입니다"
    assert _detect_dominant_script(text) == "hangul"


def test_detect_dominant_script_devanagari():
    text = "यह हिंदी में एक पाठ है जो देवनागरी लिपि का परीक्षण करता है"
    assert _detect_dominant_script(text) == "devanagari"


def test_detect_dominant_script_hiragana_katakana():
    text = "これは日本語のテキストです。ひらがなとカタカナの検出テストです。"
    assert _detect_dominant_script(text) == "hiragana_katakana"


def test_detect_dominant_script_thai():
    text = "นี่คือข้อความภาษาไทยสำหรับทดสอบการตรวจจับอักขระไทย"
    assert _detect_dominant_script(text) == "thai"


def test_detect_dominant_script_greek():
    text = "Αυτό είναι ένα κείμενο στα ελληνικά για δοκιμή εντοπισμού."
    assert _detect_dominant_script(text) == "greek"


def test_detect_dominant_script_hebrew():
    text = "זהו טקסט בעברית לבדיקת זיהוי סקריפט עברי"
    assert _detect_dominant_script(text) == "hebrew"


# --------------------------------------------------------------------------- #
# Prefilter short-circuits                                                     #
# --------------------------------------------------------------------------- #


def test_prefilter_blocks_chinese_when_not_allowed():
    """Chinese script short-circuits when allowed_languages doesn't include zh."""
    guard = guardrail.Language(allowed_languages=["en", "fr"])
    text = "这是一段中文文本，用来测试汉字检测功能是否正常工作。"
    result = guard.check(text)

    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("is_allowed_language") is False
    assert md.get("detected_script") == "han"
    assert "Language not in allowed list" in (result.reason or "")


def test_prefilter_blocks_russian_when_not_allowed():
    """Cyrillic script short-circuits when allowed_languages doesn't include ru."""
    guard = guardrail.Language(allowed_languages=["en", "ja"])
    text = "Это текст на русском языке для проверки кириллического скрипта."
    result = guard.check(text)

    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("detected_script") == "cyrillic"


# --------------------------------------------------------------------------- #
# Prefilter does NOT short-circuit                                             #
# --------------------------------------------------------------------------- #


def test_prefilter_allows_chinese_when_zh_permitted():
    """Chinese input falls through to LLM when zh is in allowed_languages."""
    guard = guardrail.Language(allowed_languages=["en", "zh"])

    mock_result = MagicMock()
    mock_result.is_allowed_language = True
    mock_result.detected_language_code = "zh"
    mock_result.detected_language_name = "Chinese"
    mock_result.reason = "Chinese is in the allowed list"

    with patch.object(guard, "_program", return_value=mock_result):
        text = "这是一段中文文本，用来测试汉字检测功能是否正常工作。"
        result = guard.check(text)

    assert result.is_allowed is True
    md = result.metadata or {}
    assert md.get("method") != "regex_prefilter"
    assert md.get("detected_language_code") == "zh"


def test_prefilter_falls_through_for_latin_input():
    """Latin-script input always falls through to the LLM."""
    guard = guardrail.Language(allowed_languages=["en"])

    mock_result = MagicMock()
    mock_result.is_allowed_language = True
    mock_result.detected_language_code = "en"
    mock_result.detected_language_name = "English"
    mock_result.reason = "English is allowed"

    with patch.object(guard, "_program", return_value=mock_result):
        result = guard.check("This is a simple English sentence.")

    assert result.is_allowed is True
    md = result.metadata or {}
    assert md.get("method") != "regex_prefilter"


# --------------------------------------------------------------------------- #
# Prefilter disabled                                                           #
# --------------------------------------------------------------------------- #


def test_prefilter_disabled_no_short_circuit():
    """When prefilter is disabled, Chinese input falls through to LLM."""
    guard = guardrail.Language(
        allowed_languages=["en", "fr"], enable_script_prefilter=False
    )

    mock_result = MagicMock()
    mock_result.is_allowed_language = False
    mock_result.detected_language_code = "zh"
    mock_result.detected_language_name = "Chinese"
    mock_result.reason = "Chinese is not allowed"

    with patch.object(guard, "_program", return_value=mock_result):
        text = "这是一段中文文本，用来测试汉字检测功能是否正常工作。"
        result = guard.check(text)

    # Should NOT have been blocked by the prefilter.
    md = result.metadata or {}
    assert md.get("method") != "regex_prefilter"
    assert result.is_allowed is False  # LLM rejected it
    assert md.get("detected_language_code") == "zh"


# --------------------------------------------------------------------------- #
# Short input falls through                                                    #
# --------------------------------------------------------------------------- #


def test_prefilter_skips_short_non_latin_input():
    """< 5 non-Latin characters falls through to the LLM."""
    guard = guardrail.Language(allowed_languages=["en"])
    # Only 4 CJK characters — below threshold.
    text = "你好世界"

    mock_result = MagicMock()
    mock_result.is_allowed_language = False
    mock_result.detected_language_code = "zh"
    mock_result.detected_language_name = "Chinese"
    mock_result.reason = "Not English"

    with patch.object(guard, "_program", return_value=mock_result):
        result = guard.check(text)

    md = result.metadata or {}
    assert md.get("method") != "regex_prefilter"


def test_prefilter_blocks_at_exactly_threshold():
    """Exactly 5 non-Latin characters triggers the prefilter."""
    guard = guardrail.Language(allowed_languages=["en"])
    # Exactly 5 CJK characters.
    text = "你好世界好"
    result = guard.check(text)

    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"


# --------------------------------------------------------------------------- #
# Mixed-script input: dominant script wins                                     #
# --------------------------------------------------------------------------- #


def test_prefilter_mixed_script_dominant_cyrillic():
    """When Cyrillic dominates with some Latin mixed in, still blocked."""
    guard = guardrail.Language(allowed_languages=["en", "fr"])
    # 20+ Cyrillic chars with a couple Latin words.
    text = "Привет мир это очень длинный текст на русском hello world"
    result = guard.check(text)

    assert result.is_allowed is False
    md = result.metadata or {}
    assert md.get("method") == "regex_prefilter"
    assert md.get("detected_script") == "cyrillic"


def test_prefilter_mixed_script_dominant_latin():
    """When Latin dominates with some Cyrillic mixed in, falls through."""
    guard = guardrail.Language(allowed_languages=["en"])

    mock_result = MagicMock()
    mock_result.is_allowed_language = True
    mock_result.detected_language_code = "en"
    mock_result.detected_language_name = "English"
    mock_result.reason = "English is allowed"

    # Mostly Latin with one short Cyrillic word — non-Latin count < 5.
    with patch.object(guard, "_program", return_value=mock_result):
        text = "Hello world, this is a test with a few Cyrillic letters др"
        result = guard.check(text)

    md = result.metadata or {}
    assert md.get("method") != "regex_prefilter"


# --------------------------------------------------------------------------- #
# Empty / whitespace input                                                     #
# --------------------------------------------------------------------------- #


def test_prefilter_empty_string_falls_through():
    guard = guardrail.Language(allowed_languages=["en"])

    mock_result = MagicMock()
    mock_result.is_allowed_language = True
    mock_result.detected_language_code = "en"
    mock_result.detected_language_name = "English"
    mock_result.reason = "Empty input"

    with patch.object(guard, "_program", return_value=mock_result):
        result = guard.check("")

    md = result.metadata or {}
    assert md.get("method") != "regex_prefilter"


def test_prefilter_whitespace_only_falls_through():
    guard = guardrail.Language(allowed_languages=["en"])

    mock_result = MagicMock()
    mock_result.is_allowed_language = True
    mock_result.detected_language_code = "en"
    mock_result.detected_language_name = "English"
    mock_result.reason = "Whitespace input"

    with patch.object(guard, "_program", return_value=mock_result):
        result = guard.check("   \n\t  ")

    md = result.metadata or {}
    assert md.get("method") != "regex_prefilter"


# --------------------------------------------------------------------------- #
# Result structure                                                             #
# --------------------------------------------------------------------------- #


def test_prefilter_result_has_allowed_languages_in_metadata():
    guard = guardrail.Language(allowed_languages=["en", "de"])
    text = "これは日本語のテキストです。ひらがなとカタカナの検出テストです。"
    result = guard.check(text)

    md = result.metadata or {}
    assert md.get("allowed_languages") == ["en", "de"]


def test_prefilter_result_guardrail_name():
    guard = guardrail.Language(allowed_languages=["en"])
    text = "这是一段中文文本，用来测试汉字检测功能是否正常工作。"
    result = guard.check(text)

    assert result.guardrail_name == "language"


# --------------------------------------------------------------------------- #
# Script catalog coverage                                                      #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "script_name,expected_codes",
    [
        ("han", ("zh",)),
        ("hiragana_katakana", ("ja",)),
        ("hangul", ("ko",)),
        ("cyrillic", ("ru", "uk", "bg", "sr", "mk")),
        ("arabic", ("ar", "fa", "ur")),
        ("hebrew", ("he",)),
        ("devanagari", ("hi", "ne", "mr")),
        ("thai", ("th",)),
        ("greek", ("el",)),
    ],
)
def test_script_catalog_entries_match_spec(script_name, expected_codes):
    """Every script in the catalog must map to the expected ISO codes."""
    entries = [e for e in SCRIPT_TO_LANG_CODES if e[0] == script_name]
    assert len(entries) == 1, f"Expected exactly one entry for {script_name}"
    assert entries[0][2] == expected_codes
