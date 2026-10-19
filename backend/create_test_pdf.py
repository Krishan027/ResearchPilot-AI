
import pymupdf


def create_test_pdf():
    with pymupdf.open() as pdf:
        page1 = pdf.new_page()
        page1.insert_textbox(
            (72, 72, 520, 700),
            """ResearchPilot AI: Introduction

Retrieval Augmented Generation (RAG) is a technique that
combines information retrieval with language generation.

First, a system searches a knowledge source for relevant
passages. Then, a language model uses those passages to
generate an answer grounded in the retrieved evidence.

RAG can help reduce unsupported answers and lets a system
use information from external documents.
""",
            fontsize=12,
        )

        page2 = pdf.new_page()
        page2.insert_textbox(
            (72, 72, 520, 700),
            """Python and Semantic Search

Python is a popular programming language used in AI,
data analysis, automation, and web development.

Semantic search represents text as numerical vectors
called embeddings. It compares these vectors to identify
passages that are similar in meaning to a question.

Cosine similarity is one method for comparing vectors.
A higher score generally indicates greater similarity,
but it does not guarantee that a passage answers a question.
""",
            fontsize=12,
        )

        pdf.save("test_document.pdf")

    print("Created test_document.pdf successfully.")


if __name__ == "__main__":
    create_test_pdf()
