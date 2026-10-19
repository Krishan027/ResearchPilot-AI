
import time

import requests

from app.core.config import settings


class OllamaService:
    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    def health_check(self) -> dict:
        """Check Ollama connectivity and model availability."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

        except (requests.RequestException, ValueError):
            return {
                "status": "unavailable",
                "model": self.model,
            }

        models = [
            item.get("name", "")
            for item in data.get("models", [])
        ]

        model_available = any(
            name == self.model
            or name.startswith(f"{self.model}:")
            for name in models
        )

        return {
            "status": (
                "healthy" if model_available else "model_missing"
            ),
            "model": self.model,
        }

    def generate_answer(self, prompt: str) -> str:
        """Generate an answer using the configured Ollama model."""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        start_time = time.perf_counter()

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=180,
            )
            response.raise_for_status()
            data = response.json()

        except requests.Timeout as exc:
            raise RuntimeError(
                "Ollama took too long to respond. Try again."
            ) from exc

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Check that Ollama is running."
            ) from exc

        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Ollama returned an HTTP error: "
                f"{exc.response.status_code}"
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                "An error occurred while communicating with Ollama."
            ) from exc

        except ValueError as exc:
            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from exc

        answer = data.get("response", "").strip()

        
        elapsed = time.perf_counter() - start_time

        eval_count = data.get("eval_count", 0)
        eval_duration = data.get("eval_duration", 0)

        tokens_per_second = 0.0
        if isinstance(eval_count, (int, float)) and isinstance(
            eval_duration, (int, float)
        ) and eval_duration > 0:
            tokens_per_second = eval_count / (eval_duration / 1_000_000_000)

        print(f"Total Ollama request time: {elapsed:.2f} seconds")
        print(f"Generated tokens: {eval_count}")
        print(f"Generation speed: {tokens_per_second:.2f} tokens/second")


        if not answer:
            raise RuntimeError("Ollama returned an empty response.")

        return answer
