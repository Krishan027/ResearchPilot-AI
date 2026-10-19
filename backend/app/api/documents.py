
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.retrieval.answer_pipeline import answer_pdf_question
from app.schemas.answer import (
    AnswerResponse,
    UploadedDocumentQuestionRequest,
)


router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_uploaded_pdf_path(document_id: str) -> Path:
    """Resolve a document ID to a safe uploaded PDF path."""

    if (
        not document_id.endswith(".pdf")
        or Path(document_id).name != document_id
        or "/" in document_id
        or "\\" in document_id
    ):
        raise ValueError("Invalid document ID.")

    path = UPLOAD_DIR / document_id

    if not path.is_file():
        raise FileNotFoundError(
            f"Uploaded document not found: {document_id}"
        )

    return path


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and validate a PDF."""

    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    document_id = f"{uuid4().hex}.pdf"
    destination = UPLOAD_DIR / document_id
    size = 0

    try:
        with destination.open("wb") as output:
            while True:
                data = await file.read(1024 * 1024)

                if not data:
                    break

                size += len(data)

                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF must be 10 MB or smaller.",
                    )

                output.write(data)

        if size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        # Check the file signature, not only the extension.
        with destination.open("rb") as uploaded:
            if not uploaded.read(5).startswith(b"%PDF-"):
                raise HTTPException(
                    status_code=400,
                    detail="The uploaded file is not a valid PDF.",
                )

        return {
            "message": "PDF uploaded successfully.",
            "document_id": document_id,
            "size_bytes": size,
        }

    except Exception:
        destination.unlink(missing_ok=True)
        raise

    finally:
        await file.close()


@router.get("")
def list_uploaded_documents():
    """List PDFs currently stored on the backend."""

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    documents = []

    for path in sorted(
        UPLOAD_DIR.glob("*.pdf"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    ):
        if not path.is_file():
            continue

        stat = path.stat()

        documents.append(
            {
                "document_id": path.name,
                "size_bytes": stat.st_size,
                "uploaded_at": stat.st_mtime,
            }
        )

    return {"documents": documents}


@router.post(
    "/{document_id}/answer",
    response_model=AnswerResponse,
)
def answer_uploaded_document(
    document_id: str,
    request: UploadedDocumentQuestionRequest,
):
    """Answer a question using an uploaded PDF."""

    try:
        pdf_path = get_uploaded_pdf_path(document_id)

        return answer_pdf_question(
            pdf_path=str(pdf_path),
            question=request.question,
            top_k=request.top_k,
            min_score=request.min_score,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
