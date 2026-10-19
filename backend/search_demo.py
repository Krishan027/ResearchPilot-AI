
from app.retrieval.pipeline import search_pdf


if __name__ == "__main__":
    pdf_path = "test_document.pdf"
    query = input("Enter your research question: ")

    results = search_pdf(
        pdf_path=pdf_path,
        query=query,
        top_k=3,
    )

    print("\n=== ResearchPilot AI: Search Results ===")

    if not results:
        print("No searchable text found in the PDF.")

    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Source: {result['source']}")
        print(f"Page: {result['page_number']}")
        print(f"Similarity: {result['score']:.4f}")
        print(f"Passage: {result['text']}")
