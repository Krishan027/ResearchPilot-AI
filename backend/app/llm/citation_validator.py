
import re


def find_invalid_citations(answer: str, citation_count: int) -> list[str]:
    """Return numeric citation markers that do not reference supplied evidence."""
    markers = re.findall(r"\[(\d+)\]", answer)

    invalid = []
    for marker in markers:
        number = int(marker)
        if number < 1 or number > citation_count:
            invalid.append(f"[{marker}]")

    return sorted(
        set(invalid),
        key=lambda marker: int(marker[1:-1]),
    )


def validate_citations(answer: str, citation_count: int) -> bool:
    """Return True when every numeric citation marker is valid."""
    return not find_invalid_citations(answer, citation_count)
