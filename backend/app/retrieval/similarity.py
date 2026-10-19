
from app.retrieval.embedder import TextEmbedder


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same dimensions")

    if not vector_a:
        raise ValueError("Vectors cannot be empty")

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    norm_a = sum(a * a for a in vector_a) ** 0.5
    norm_b = sum(b * b for b in vector_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        raise ValueError("Zero vectors are not supported")

    return dot_product / (norm_a * norm_b)


if __name__ == "__main__":
    embedder = TextEmbedder()

    query = "How can I learn Python programming?"
    candidates = [
        "Python is a programming language.",
        "The weather is sunny today.",
        "Ways to study and improve Python coding skills.",
    ]

    query_vector = embedder.embed_text(query)

    scores = []

    for text in candidates:
        candidate_vector = embedder.embed_text(text)
        score = cosine_similarity(query_vector, candidate_vector)
        scores.append((text, score))

    scores.sort(key=lambda item: item[1], reverse=True)

    for text, score in scores:
        print(f"{score:.4f} | {text}")
