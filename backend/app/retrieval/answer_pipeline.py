
from app.llm.answer_generator import AnswerGenerator
from app.models.chunk import DocumentChunk
from app.retrieval.pipeline import search_pdf
from app.schemas.answer import AnswerResponse


# Reuse the generator and its Ollama service across requests.
answer_generator = AnswerGenerator()


def answer_pdf_question(
    pdf_path: str,
    question: str,
    top_k: int = 3,
    min_score: float = 0.10,
) -> AnswerResponse:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    results = search_pdf(
        pdf_path=pdf_path,
        query=question,
        top_k=top_k,
    )

    
    print("\n--- ResearchPilot Retrieval Debug ---")
    print(f"Question: {question}")
    print(f"Retrieved chunks: {len(results)}")

    for result in results:
        print(
            f"Score: {result['score']:.4f} | "
            f"Page: {result['page_number']} | "
            f"Text: {result['text'][:200]!r}"
        )

    print("--- End Retrieval Debug ---\n")


    chunks = [
        DocumentChunk(
            chunk_id=result["chunk_id"],
            source=result["source"],
            page_number=result["page_number"],
            chunk_index=index,
            text=result["text"],
            score=result["score"],
        )
        for index, result in enumerate(results)
        if result["score"] >= min_score
    ]

    if not chunks:
        return AnswerResponse(
            question=question,
            answer=(
                "I couldn't find sufficiently relevant evidence "
                "in this document to answer your question."
            ),
            citations=[],
            confidence=0.0,
        )

    return answer_generator.generate(
        question=question,
        chunks=chunks,
    )
