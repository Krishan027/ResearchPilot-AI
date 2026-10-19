
from functools import lru_cache

from app.models.chunk import DocumentChunk
from app.retrieval.embedder import TextEmbedder
from app.retrieval.similarity import cosine_similarity


@lru_cache(maxsize=1)
def get_embedder() -> TextEmbedder:
    """Load and reuse one embedding model."""
    return TextEmbedder()


@lru_cache(maxsize=4096)
def get_chunk_embedding(text: str) -> tuple[float, ...]:
    """Cache chunk embeddings by their text."""
    return tuple(get_embedder().embed_text(text))


class SemanticRetriever:
    def __init__(self):
        # Defer loading the transformer model until a document is searched.
        # This keeps API startup and non-ML unit tests usable offline.
        self._embedder = None

    @property
    def embedder(self) -> TextEmbedder:
        if self._embedder is None:
            self._embedder = get_embedder()
        return self._embedder

    @embedder.setter
    def embedder(self, value):
        # Kept assignable so tests and callers can provide a lightweight embedder.
        self._embedder = value

    def _embed_chunk(self, text: str) -> tuple[float, ...]:
        """Use cached embeddings with compatibility for test mocks."""
        cache = getattr(self, "_chunk_embedding_cache", None)

        if cache is None:
            cache = {}
            self._chunk_embedding_cache = cache

        if text not in cache:
            cache[text] = tuple(self.embedder.embed_text(text))

        return cache[text]

    def retrieve(
        self,
        query: str,
        chunks: list[DocumentChunk],
        top_k: int = 3,
    ) -> list[dict]:
        """Return the most relevant document chunks for a query."""
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        if not chunks:
            return []

        query_vector = self.embedder.embed_text(query)
        results = []

        for chunk in chunks:
            chunk_vector = self._embed_chunk(chunk.text)

            score = cosine_similarity(
                query_vector,
                chunk_vector,
            )

            results.append({
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "page_number": chunk.page_number,
                "text": chunk.text,
                "score": score,
            })

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]
