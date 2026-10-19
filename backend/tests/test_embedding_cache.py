
from unittest.mock import Mock

from app.retrieval import retriever


def test_chunk_embedding_is_cached(monkeypatch):
    retriever.get_chunk_embedding.cache_clear()
    retriever.get_embedder.cache_clear()

    fake_embedder = Mock()
    fake_embedder.embed_text.return_value = [0.1, 0.2, 0.3]

    monkeypatch.setattr(
        retriever,
        "get_embedder",
        lambda: fake_embedder,
    )

    first = retriever.get_chunk_embedding("sample document chunk")
    second = retriever.get_chunk_embedding("sample document chunk")

    assert first == second == (0.1, 0.2, 0.3)
    fake_embedder.embed_text.assert_called_once_with(
        "sample document chunk"
    )

    retriever.get_chunk_embedding.cache_clear()


def test_different_chunks_get_separate_embeddings(monkeypatch):
    retriever.get_chunk_embedding.cache_clear()

    fake_embedder = Mock()
    fake_embedder.embed_text.side_effect = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    monkeypatch.setattr(
        retriever,
        "get_embedder",
        lambda: fake_embedder,
    )

    first = retriever.get_chunk_embedding("chunk one")
    second = retriever.get_chunk_embedding("chunk two")

    assert first != second
    assert fake_embedder.embed_text.call_count == 2

    retriever.get_chunk_embedding.cache_clear()


def test_clear_document_cache():
    from app.retrieval import pipeline

    pipeline.clear_document_cache()

    assert pipeline._load_document_chunks.cache_info().currsize == 0

    cache = getattr(pipeline.retriever, "_chunk_embedding_cache", None)
    if cache is not None:
        assert len(cache) == 0
