# ResearchPilot AI

**A local LLM-powered PDF research assistant built with RAG, FastAPI, React, and Ollama.**

ResearchPilot AI lets users upload PDF documents, ask questions about their content, and receive answers grounded in retrieved passages with page references and citations. It combines semantic search with a locally running language model to support document-based research.

## Features

- **PDF question answering** — ask questions about uploaded documents.
- **Retrieval-Augmented Generation (RAG)** — retrieve relevant text passages to ground answers in document evidence.
- **Semantic search** — use sentence-transformer embeddings to find passages related to a question.
- **Source citations** — show document page references and cited evidence.
- **Local LLM inference** — generate answers with Ollama and the `qwen2.5:3b` model.
- **Research history** — save, review, search, restore, and delete previous research sessions.
- **REST API** — access backend functionality through FastAPI endpoints.
- **Automated tests** — validate important backend functionality with pytest.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| LLM inference | Ollama, Qwen 2.5 3B |
| Embeddings | Sentence Transformers, `all-MiniLM-L6-v2` |
| Retrieval | Semantic similarity and document chunking |
| Data storage | SQLite |
| Testing | pytest |

## Architecture

1. **Upload:** The user uploads a PDF through the React interface.
2. **Extract:** The FastAPI backend extracts text and divides it into chunks.
3. **Retrieve:** The embedding model and semantic retrieval pipeline find passages relevant to the question.
4. **Generate:** Ollama generates an answer using the retrieved context.
5. **Cite:** The response includes source references to help the user inspect the supporting document evidence.
6. **Save:** Research sessions and document metadata are stored locally.

```text
React + Vite
     |
     v
FastAPI REST API
     |
     v
PDF Text Extraction -> Chunking -> Embeddings
                                  |
                                  v
                           Semantic Retrieval
                                  |
                                  v
                          Ollama LLM (Qwen)
                                  |
                                  v
                       Answer + Source Citations
                                  |
                                  v
                         SQLite Research History
```

## Requirements

- Python 3.10 or newer
- Node.js 20.19+ or 22.12+
- [Ollama](https://ollama.com/)
- Git

The first backend run may download the `sentence-transformers/all-MiniLM-L6-v2` embedding model if it is not already cached.

**PDF limitation:** The current pipeline works with text-based PDFs. Scanned image-only PDFs require OCR, which is not currently included.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Krishan027/ResearchPilot-AI.git
cd ResearchPilot-AI
```

### 2. Configure the backend

Open a terminal in the project root and run:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
ollama pull qwen2.5:3b
python -m uvicorn app.main:app --reload
```

If `.env` already exists, do not overwrite it. Configure `RESEARCHPILOT_OLLAMA_BASE_URL` and `RESEARCHPILOT_OLLAMA_MODEL` in `backend/.env` as needed.

The backend runs at `http://127.0.0.1:8000`.

Interactive API documentation: `http://127.0.0.1:8000/docs`

### 3. Configure the frontend

Open a **second terminal** in the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

If your API uses a different address, configure `VITE_API_BASE_URL` in `frontend/.env.local` as supported by the frontend.

## Using the Application

1. Start Ollama and ensure the configured model is available.
2. Start the FastAPI backend and React frontend.
3. Upload a PDF (maximum 10 MB).
4. Ask a question about the document.
5. Review the generated answer, citations, and confidence estimate.
6. Use research history to revisit saved sessions.

## API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/documents/upload` | Validate and store a PDF |
| GET | `/api/documents` | List stored PDFs |
| POST | `/api/documents/{document_id}/answer` | Answer a question about an uploaded document |
| GET / POST | `/api/history` | List or save research sessions |
| GET / DELETE | `/api/history/{session_id}` | Retrieve or delete a saved session |
| GET | `/health` | Check API health |
| GET | `/health/ollama` | Check Ollama connectivity |

## Running Tests

From the project root:

```powershell
cd backend
python -m pytest
```

Tests cover areas including PDF parsing, chunking, retrieval, answer generation, citation validation, API behavior, configuration, and research history.

## Project Structure

```text
ResearchPilot-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── ingestion/
│   │   ├── llm/
│   │   ├── models/
│   │   ├── retrieval/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Privacy and Security

- The application is designed for local use.
- Uploaded documents and research history are stored on the local machine.
- Local files and database contents are not encrypted by the application.
- Keep secrets in local environment files; do not commit `.env` files.
- Keep the API bound to localhost unless you implement authentication and appropriate network protections before exposing it to other users.

## Current Limitations and Future Improvements

Potential improvements include:

- OCR support for scanned PDFs
- Better retrieval evaluation and configurable relevance thresholds
- More robust document-level access controls
- Deployment guidance and authentication for multi-user environments
- Additional frontend and end-to-end tests

## Author

**Krishan027**

- GitHub: [@Krishan027](https://github.com/Krishan027)
- Project: [ResearchPilot AI](https://github.com/Krishan027/ResearchPilot-AI)
