
from uuid import uuid4

from app.models.chunk import DocumentChunk
from app.models.document import DocumentPage


def chunk_document(
    pages: list[DocumentPage],
    chunk_size: int = 200,
    overlap: int = 40,
) -> list[DocumentChunk]:
    """Split document pages into overlapping word-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size"
        )

    chunks: list[DocumentChunk] = []

    for page in pages:
        words = page.text.split()
        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            text = " ".join(words[start:end])

            chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid4()),
                    source=page.source,
                    page_number=page.page_number,
                    chunk_index=len(chunks),
                    text=text,
                )
            )

            if end == len(words):
                break

            start = end - overlap

    return chunks
