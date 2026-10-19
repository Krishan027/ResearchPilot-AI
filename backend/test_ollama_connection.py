
from app.llm.ollama_service import OllamaService


def main():
    service = OllamaService()

    print("Testing Ollama connection...")

    answer = service.generate_answer(
        "Reply with exactly this text: "
        "ResearchPilot AI Ollama connection successful."
    )

    print("Ollama response:", answer)
    print("Ollama test completed successfully.")


if __name__ == "__main__":
    main()
