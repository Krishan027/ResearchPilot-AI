
from functools import lru_cache
from pathlib import Path

from app.ingestion.chunker import chunk_document
from app.ingestion.parser import extract_text_from_pdf
from app.retrieval.retriever import SemanticRetriever


# Reuse the retriever and its embedding cache across searches.
retriever = SemanticRetriever()


@lru_cache(maxsize=8)
def _load_document_chunks(
    pdf_path: str,
    modified_time_ns: int,
    file_size: int,
):
    """Cache parsed and chunked PDFs."""
    pages = extract_text_from_pdf(pdf_path)
    return chunk_document(pages)


def search_pdf(
    pdf_path: str,
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """Search a PDF and return its most relevant passages."""

    path = Path(pdf_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    stat = path.stat()

    chunks = _load_document_chunks(
        str(path),
        stat.st_mtime_ns,
        stat.st_size,
    )

    if not chunks:
        raise ValueError(
            "No searchable text was found in this PDF. "
            "It may contain scanned pages that need OCR."
        )

    return retriever.retrieve(
        query=query,
        chunks=chunks,
        top_k=top_k,
    )


def clear_document_cache() -> None:
    """Clear cached PDF chunks and document embeddings."""
    _load_document_chunks.cache_clear()

    # Clear the retriever's per-instance chunk embedding cache.
    retriever_cache = getattr(retriever, "_chunk_embedding_cache", None)
    if retriever_cache is not None:
        retriever_cache.clear()
