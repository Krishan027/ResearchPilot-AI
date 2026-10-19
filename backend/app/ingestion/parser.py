
from pathlib import Path

import pymupdf

from app.models.document import DocumentPage


def extract_text_from_pdf(file_path: str) -> list[DocumentPage]:
    """Extract text and metadata from each non-empty PDF page."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("The input file must have a .pdf extension")

    pages: list[DocumentPage] = []

    with pymupdf.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append(
                    DocumentPage(
                        source=path.name,
                        page_number=page_number,
                        text=text,
                    )
                )

    return pages
