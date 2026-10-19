
from fastapi import APIRouter, HTTPException

from app.retrieval.answer_pipeline import answer_pdf_question
from app.schemas.answer import AnswerResponse, QuestionRequest


router = APIRouter(prefix="/api", tags=["Research"])


@router.post("/answer", response_model=AnswerResponse)
def answer_question(request: QuestionRequest):
    try:
        return answer_pdf_question(
            pdf_path=request.pdf_path,
            question=request.question,
            top_k=request.top_k,
            min_score=request.min_score,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc