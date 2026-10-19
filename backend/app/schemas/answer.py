
from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    page_number: int = Field(ge=1)
    chunk_id: str
    text: str = ""


class AnswerResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class QuestionRequest(BaseModel):
    pdf_path: str
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)
    min_score: float = Field(default=0.10, ge=0.0, le=1.0)



class UploadedDocumentQuestionRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)
    min_score: float = Field(default=0.10, ge=0.0, le=1.0)

