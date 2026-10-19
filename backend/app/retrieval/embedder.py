
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class TextEmbedder:
    def __init__(self):
        # Import the heavyweight ML runtime only when embeddings are requested.
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(MODEL_NAME)

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Text cannot be empty")

        vector = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return vector.tolist()


if __name__ == "__main__":
    embedder = TextEmbedder()

    text = "ResearchPilot AI uses retrieval augmented generation."
    vector = embedder.embed_text(text)

    print("Input:", text)
    print("Vector dimensions:", len(vector))
    print("First 5 values:", vector[:5])
