
from unittest.mock import Mock

from app.models.chunk import DocumentChunk
from app.retrieval.retriever import SemanticRetriever


def test_retriever_reuses_chunk_embeddings():
    retriever = SemanticRetriever()

    fake_embedder = Mock()
    fake_embedder.embed_text.side_effect = [
        [1.0, 0.0],  # First query
        [0.9, 0.1],  # Document chunk
        [0.0, 1.0],  # Second query
    ]
    retriever.embedder = fake_embedder

    chunks = [
        DocumentChunk(
            chunk_id="chunk-1",
            source="sample.pdf",
            page_number=1,
            chunk_index=0,
            text="ResearchPilot AI uses retrieval augmented generation.",
            score=0.0,
        )
    ]

    retriever.retrieve("What is ResearchPilot?", chunks)
    retriever.retrieve("How does ResearchPilot work?", chunks)

    # Two query embeddings plus one cached chunk embedding.
    assert fake_embedder.embed_text.call_count == 3
