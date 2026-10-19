
import pytest

from app.ingestion.chunker import chunk_document
from app.models.document import DocumentPage
from app.models.chunk import DocumentChunk


def test_chunk_document_with_overlap():
    page = DocumentPage(
        source="sample.pdf",
        page_number=1,
        text="A B C D E F G",
    )

    chunks = chunk_document(
        [page],
        chunk_size=4,
        overlap=1,
    )

    assert len(chunks) == 2
    assert chunks[0].text == "A B C D"
    assert chunks[1].text == "D E F G"


def test_chunk_metadata():
    page = DocumentPage(
        source="python_guide.pdf",
        page_number=3,
        text="Python supports functions and classes",
    )

    chunks = chunk_document(
        [page],
        chunk_size=3,
        overlap=1,
    )

    assert all(isinstance(c, DocumentChunk) for c in chunks)
    assert all(c.source == "python_guide.pdf" for c in chunks)
    assert all(c.page_number == 3 for c in chunks)
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


def test_empty_page():
    page = DocumentPage(
        source="empty.pdf",
        page_number=1,
        text="",
    )

    assert chunk_document([page]) == []


def test_invalid_chunk_size():
    page = DocumentPage(
        source="sample.pdf",
        page_number=1,
        text="Hello world",
    )

    with pytest.raises(ValueError):
        chunk_document([page], chunk_size=0)


def test_invalid_overlap():
    page = DocumentPage(
        source="sample.pdf",
        page_number=1,
        text="Hello world",
    )

    with pytest.raises(ValueError):
        chunk_document([page], chunk_size=5, overlap=5)
