import pytest
import pymupdf

from app.ingestion.parser import extract_text_from_pdf
from app.models.document import DocumentPage


def test_extract_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    # Create a two-page test PDF.
    with pymupdf.open() as pdf:
        page1 = pdf.new_page()
        page1.insert_text((72, 72), "ResearchPilot AI")

        page2 = pdf.new_page()
        page2.insert_text(
            (72, 72),
            "Retrieval Augmented Generation",
        )

        pdf.save(pdf_path)

    # Extract text using our parser.
    result = extract_text_from_pdf(str(pdf_path))

    # Verify the returned type and number of pages.
    assert isinstance(result, list)
    assert len(result) == 2

    # Verify page 1.
    assert isinstance(result[0], DocumentPage)
    assert result[0].source == "sample.pdf"
    assert result[0].page_number == 1
    assert "ResearchPilot AI" in result[0].text

    # Verify page 2.
    assert isinstance(result[1], DocumentPage)
    assert result[1].source == "sample.pdf"
    assert result[1].page_number == 2
    assert "Retrieval Augmented Generation" in result[1].text


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("does_not_exist.pdf")


def test_invalid_extension(tmp_path):
    invalid_file = tmp_path / "document.txt"
    invalid_file.write_text(
        "This is not a PDF.",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        extract_text_from_pdf(str(invalid_file))