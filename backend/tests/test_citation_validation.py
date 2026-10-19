
from app.llm.citation_validator import (
    find_invalid_citations,
    validate_citations,
)


def test_valid_citations():
    assert validate_citations("This is supported [1] and [2].", 2)


def test_invalid_citation_above_range():
    assert not validate_citations("This cites [3].", 2)


def test_zero_citation_is_invalid():
    assert not validate_citations("This cites [0].", 2)


def test_no_citations_is_valid():
    assert validate_citations("No citation markers here.", 2)


def test_find_invalid_citations():
    answer = "Claims [1], [4], [0], and [4]."
    assert find_invalid_citations(answer, 2) == ["[0]", "[4]"]


def test_duplicate_invalid_citations_are_returned_once():
    answer = "Claim A [9]. Claim B [9]."
    assert find_invalid_citations(answer, citation_count=2) == ["[9]"]


def test_valid_citations_with_no_evidence_are_invalid():
    answer = "The document says [1]."
    assert find_invalid_citations(answer, citation_count=0) == ["[1]"]


def test_multiple_invalid_citations_are_sorted_numerically():
    answer = "Claim [10]. Another claim [3]. First claim [2]."
    assert find_invalid_citations(answer, citation_count=1) == [
        "[2]",
        "[3]",
        "[10]",
    ]


def test_valid_citations_are_not_flagged():
    answer = "First fact [1]. Second fact [2]."
    assert find_invalid_citations(answer, citation_count=2) == []


def test_ordinary_bracketed_text_is_not_a_citation():
    answer = "The document labels this section [important]."
    assert find_invalid_citations(answer, citation_count=2) == []
