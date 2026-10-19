
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.answer import router as answer_router
from app.api.documents import router as documents_router
from app.api.history import router as history_router
from app.core.config import settings
from app.core.database import initialize_database
from app.llm.ollama_service import OllamaService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application resources during startup."""
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(answer_router)
app.include_router(documents_router)
app.include_router(history_router)


@app.get("/", tags=["General"])
def root():
    return {
        "project": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.get("/health/ollama", tags=["Health"])
def ollama_health():
    result = OllamaService().health_check()

    if result["status"] != "healthy":
        raise HTTPException(status_code=503, detail=result)

    return result
