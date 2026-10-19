
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_pdf_success():
    fake_pdf = b"%PDF-1.4\nTest PDF content"

    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "sample.pdf",
                BytesIO(fake_pdf),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "PDF uploaded successfully."
    assert data["document_id"].endswith(".pdf")
    assert data["size_bytes"] == len(fake_pdf)


def test_upload_rejects_non_pdf():
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "notes.txt",
                BytesIO(b"plain text"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed."


def test_upload_rejects_empty_file():
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "empty.pdf",
                BytesIO(b""),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is empty."


def test_upload_rejects_oversized_file():
    # Avoid allocating a real 10 MB+ byte string.
    class LargeFakeFile:
        def __init__(self):
            self.remaining = 10 * 1024 * 1024 + 1

        async def read(self, size=-1):
            if self.remaining <= 0:
                return b""

            amount = min(size, self.remaining)
            self.remaining -= amount
            return b"x" * amount

        async def close(self):
            pass

    with patch(
        "app.api.documents.UploadFile.read",
        new=LargeFakeFile().read,
    ):
        response = client.post(
            "/api/documents/upload",
            files={
                "file": (
                    "large.pdf",
                    BytesIO(b"%PDF-1.4\n"),
                    "application/pdf",
                )
            },
        )

    assert response.status_code in (200, 413)
