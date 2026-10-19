
import { useEffect, useRef, useState } from "react";
import {
  askQuestion,
  uploadPdf,
  getUploadedDocuments,
  getResearchHistory,
  getResearchSession,
  saveResearchSession,
  deleteResearchSession,
  migrateLegacyHistory,
  getOllamaHealth,
} from "./api";
import "./App.css";

function createId() {
  return (
    globalThis.crypto?.randomUUID?.() ??
    `id-${Date.now()}-${Math.random().toString(36).slice(2)}`
  );
}

function createSession() {
  const now = new Date().toISOString();

  return {
    id: createId(),
    title: "New research",
    documentId: "",
    fileName: "",
    createdAt: now,
    updatedAt: now,
    messages: [],
  };
}

function App() {
  const [history, setHistory] = useState([]);
  const [historyQuery, setHistoryQuery] = useState("");
  const [historySearching, setHistorySearching] = useState(false);
  const [session, setSession] = useState(createSession);
  const [question, setQuestion] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [checkingDocument, setCheckingDocument] = useState(false);
  const [documentAvailable, setDocumentAvailable] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [historyLoading, setHistoryLoading] = useState(true);
  const [migrating, setMigrating] = useState(false);
  const [migrationMessage, setMigrationMessage] = useState("");
  const [savingHistory, setSavingHistory] = useState(false);
  const [modelStatus, setModelStatus] = useState({
    label: "Checking local model...",
    healthy: false,
  });
  const historySaveQueue = useRef(Promise.resolve());
  const pendingHistorySaves = useRef(0);
  const historyQueryRef = useRef(historyQuery);
  const skipHistorySaveForSession = useRef(null);
  historyQueryRef.current = historyQuery;

  const { id: sessionId, documentId, fileName, messages } = session;

  // Load research history from SQLite.
  async function refreshHistory(query = "") {
    const result = await getResearchHistory(query);
    setHistory(result.sessions || []);
  }

  // Search saved conversations by title.
  async function handleSearchHistory(event) {
    event.preventDefault();
    setHistorySearching(true);

    try {
      await refreshHistory(historyQuery);
    } catch (error) {
      setUploadError(`Unable to search research history: ${error.message}`);
    } finally {
      setHistorySearching(false);
    }
  }

  async function clearHistorySearch() {
    setHistoryQuery("");
    setHistorySearching(true);

    try {
      await refreshHistory("");
    } catch (error) {
      setUploadError(`Unable to load research history: ${error.message}`);
    } finally {
      setHistorySearching(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      try {
        const result = await getResearchHistory();

        if (!cancelled) {
          setHistory(result.sessions || []);
        }
      } catch (error) {
        console.error("Unable to load research history:", error);

        if (!cancelled) {
          setUploadError(
            `Unable to load research history: ${error.message}`
          );
        }
      } finally {
        if (!cancelled) {
          setHistoryLoading(false);
        }
      }
    }

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    getOllamaHealth()
      .then((result) => {
        if (!cancelled) {
          setModelStatus({ label: `${result.model} · Local`, healthy: true });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setModelStatus({ label: "Local model unavailable", healthy: false });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Save completed conversations to SQLite.
  useEffect(() => {
    if (asking || (session.messages.length === 0 && !session.documentId)) return;
    if (skipHistorySaveForSession.current === session.id) {
      skipHistorySaveForSession.current = null;
      return;
    }

    const firstQuestion = session.messages.find(
      (message) => message.role === "user"
    )?.text;

    const updatedSession = {
      ...session,
      title: firstQuestion
        ? firstQuestion.slice(0, 45)
        : session.fileName || "New research",
      updatedAt: new Date().toISOString(),
      messages: session.messages.filter((message) => !message.loading),
    };

    let cancelled = false;

    pendingHistorySaves.current += 1;
    setSavingHistory(true);

    const save = historySaveQueue.current
      .catch(() => {})
      .then(() => saveResearchSession(updatedSession));
    historySaveQueue.current = save;

    save
      .then(async () => {
        const query = historyQueryRef.current;
        const result = await getResearchHistory(query);

        if (!cancelled && query === historyQueryRef.current) {
          setHistory(result.sessions || []);
        }
      })
      .catch((error) => {
        console.error("Unable to save research session:", error);

        if (!cancelled) {
          setUploadError(`Unable to save research history: ${error.message}`);
        }
      })
      .finally(() => {
        pendingHistorySaves.current -= 1;
        setSavingHistory(pendingHistorySaves.current > 0);
      });

    return () => {
      cancelled = true;
    };
  }, [session, asking]);

  const latestCitations =
    [...messages]
      .reverse()
      .find(
        (message) =>
          message.role === "assistant" &&
          message.citations?.length > 0
      )?.citations || [];

  function updateSession(updates) {
    setSession((previous) => ({
      ...previous,
      ...updates,
      updatedAt: new Date().toISOString(),
    }));
  }

  async function checkDocumentAvailability(documentIdToCheck) {
    if (!documentIdToCheck) {
      setDocumentAvailable(false);
      return false;
    }

    setDocumentAvailable(false);

    try {
      const result = await getUploadedDocuments();

      const available = (result.documents || []).some(
        (document) => document.document_id === documentIdToCheck
      );

      setDocumentAvailable(available);

      if (!available) {
        setUploadError(
          "This PDF is no longer available. Upload it again to continue."
        );
      }

      return available;
    } catch (error) {
      console.error("Unable to check document availability:", error);
      setDocumentAvailable(false);
      setUploadError(
        "Could not verify the saved PDF. Check that the backend is running."
      );
      return false;
    }
  }

  function startNewResearch() {
    if (uploading || asking || checkingDocument || migrating) return;

    setSession(createSession());
    setQuestion("");
    setUploadError("");
    setDocumentAvailable(false);
    setMigrationMessage("");
  }

  // Restore a complete conversation from SQLite.
  async function openSession(savedSession) {
    if (uploading || asking || checkingDocument || migrating) return;

    setCheckingDocument(true);
    setUploadError("");
    setQuestion("");
    setDocumentAvailable(false);

    try {
      const restored = await getResearchSession(savedSession.id);

      const restoredSession = {
        ...restored,
        documentId: restored.document_id || "",
        fileName: restored.file_name || "",
        createdAt: restored.created_at,
        updatedAt: restored.updated_at,
        messages: (restored.messages || []).map((message) => ({
          ...message,
          loading: false,
        })),
      };

      skipHistorySaveForSession.current = restoredSession.messages.length
        ? restoredSession.id
        : null;
      setSession(restoredSession);

      if (restoredSession.documentId) {
        await checkDocumentAvailability(restoredSession.documentId);
      }
    } catch (error) {
      setUploadError(`Unable to open research: ${error.message}`);
    } finally {
      setCheckingDocument(false);
    }
  }

  // Delete a saved conversation from SQLite.
  async function handleDeleteSession(event, id) {
    event.stopPropagation();

    if (uploading || asking || checkingDocument || migrating) return;

    try {
      await historySaveQueue.current.catch(() => {});
      await deleteResearchSession(id);
      await refreshHistory(historyQueryRef.current);

      if (sessionId === id) {
        setSession(createSession());
        setQuestion("");
        setUploadError("");
        setDocumentAvailable(false);
      }
    } catch (error) {
      setUploadError(`Unable to delete history: ${error.message}`);
    }
  }

  // Import old browser history without deleting the local backup.
  async function handleMigrateHistory() {
    if (migrating || uploading || asking || checkingDocument) return;

    setMigrating(true);
    setMigrationMessage("");
    setUploadError("");

    try {
      const stored = localStorage.getItem("researchpilot_conversations");
      const legacySessions = stored ? JSON.parse(stored) : [];

      if (!Array.isArray(legacySessions) || legacySessions.length === 0) {
        setMigrationMessage("No old browser conversations were found.");
        return;
      }

      const result = await migrateLegacyHistory(legacySessions);
      await refreshHistory();

      setMigrationMessage(
        `Migration complete: ${result.migrated} migrated, ` +
          `${result.skipped} skipped, ${result.errors.length} failed.`
      );

      if (result.errors.length > 0) {
        console.error("History migration errors:", result.errors);
      }
    } catch (error) {
      setMigrationMessage(`Migration failed: ${error.message}`);
    } finally {
      setMigrating(false);
    }
  }

  async function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadError("");

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setUploadError("Please select a PDF file.");
      event.target.value = "";
      return;
    }

    if (file.size === 0) {
      setUploadError("The selected PDF is empty.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadError("The PDF must be 10 MB or smaller.");
      event.target.value = "";
      return;
    }

    setUploading(true);
    setQuestion("");
    setDocumentAvailable(false);

    updateSession({
      documentId: "",
      fileName: file.name,
      messages: [],
    });

    try {
      const result = await uploadPdf(file);

      updateSession({
        documentId: result.document_id,
        fileName: file.name,
        messages: [],
      });

      setDocumentAvailable(true);
      setUploadError("");
    } catch (error) {
      updateSession({
        documentId: "",
        fileName: "",
      });

      setUploadError(error.message || "Unable to upload PDF.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const questionText = question.trim();

    if (
      !questionText ||
      !documentId ||
      !documentAvailable ||
      checkingDocument ||
      asking
    ) {
      return;
    }

    setQuestion("");
    setUploadError("");
    setAsking(true);

    const userMessage = {
      id: createId(),
      role: "user",
      text: questionText,
      created_at: new Date().toISOString(),
    };

    const loadingId = createId();

    const loadingMessage = {
      id: loadingId,
      role: "assistant",
      text: "Researching your document...",
      loading: true,
      created_at: new Date().toISOString(),
    };

    setSession((previous) => ({
      ...previous,
      messages: [...previous.messages, userMessage, loadingMessage],
      updatedAt: new Date().toISOString(),
    }));

    try {
      const result = await askQuestion(documentId, questionText);

      setSession((previous) => ({
        ...previous,
        messages: previous.messages.map((message) =>
          message.id === loadingId
            ? {
                id: loadingId,
                role: "assistant",
                text: result.answer,
                citations: result.citations || [],
                confidence: result.confidence ?? null,
                created_at: new Date().toISOString(),
              }
            : message
        ),
        updatedAt: new Date().toISOString(),
      }));
    } catch (error) {
      setSession((previous) => ({
        ...previous,
        messages: previous.messages.map((message) =>
          message.id === loadingId
            ? {
                id: loadingId,
                role: "assistant",
                text: `Unable to answer: ${error.message}`,
                created_at: new Date().toISOString(),
              }
            : message
        ),
      }));
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">R</div>
          <div>
            <h2>ResearchPilot</h2>
            <span>AI Research Workspace</span>
          </div>
        </div>

        <button
          className="new-research-button"
          type="button"
          onClick={startNewResearch}
          disabled={uploading || asking || checkingDocument || migrating}
        >
          <span>＋</span> New research
        </button>

        <div className="sidebar-section">
          <span className="section-label">WORKSPACE</span>
          <div className="sidebar-item active">
            <span>◈</span> PDF Research
          </div>
        </div>

        <div className="history-section">
          <div className="history-heading">
            <span className="section-label">RECENT RESEARCH</span>
            <div className="history-heading-meta">
              {savingHistory && <span className="history-save-status" role="status">Saving...</span>}
              <span className="history-count">{history.length}</span>
            </div>
          </div>

          <form
            className="history-search-form"
            onSubmit={handleSearchHistory}
          >
            <input
              className="history-search-input"
              type="search"
              value={historyQuery}
              onChange={(event) => setHistoryQuery(event.target.value)}
              placeholder="Search by title..."
              aria-label="Search saved research by title"
              disabled={historySearching}
            />
            <button className="history-search-submit" type="submit" disabled={historySearching}>
              {historySearching ? "..." : "Search"}
            </button>
            {historyQuery && (
              <button
                className="history-search-clear"
                type="button"
                onClick={clearHistorySearch}
                disabled={historySearching}
                aria-label="Clear history search"
                title="Clear search"
              >
                ×
              </button>
            )}
          </form>

          {historyLoading ? (
            <p className="history-empty">Loading research history...</p>
          ) : history.length === 0 ? (
            <p className="history-empty">
              {historyQuery.trim()
                ? "No saved conversations match your search."
                : "Your saved conversations will appear here."}
            </p>
          ) : (
            <div className="history-list">
              {history.map((item) => (
                <div
                  className={`history-item ${
                    item.id === sessionId ? "selected" : ""
                  }`}
                  key={item.id}
                >
                  <button
                    type="button"
                    className="history-open"
                    onClick={() => openSession(item)}
                    disabled={
                      uploading || asking || checkingDocument || migrating
                    }
                    title={item.title}
                  >
                    <span className="history-file">▤</span>
                    <span className="history-title">
                      {item.title || "New research"}
                    </span>
                  </button>

                  <button
                    type="button"
                    className="history-delete"
                    onClick={(event) => handleDeleteSession(event, item.id)}
                    disabled={
                      uploading || asking || checkingDocument || migrating
                    }
                    aria-label={`Delete ${item.title || "research session"}`}
                    title="Delete conversation"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="history-tools">
          <button
            type="button"
            onClick={handleMigrateHistory}
            disabled={migrating || uploading || asking || checkingDocument}
              className="history-import-button"
          >
            {migrating ? "Migrating..." : "Import old history"}
          </button>

          {migrationMessage && (
            <p
              role="status"
              className="history-import-message"
            >
              {migrationMessage}
            </p>
          )}
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>Local AI engine</strong>
            <span>Powered by Ollama</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace /</span>
            <strong> PDF Research</strong>
          </div>

          <div className={`model-badge ${modelStatus.healthy ? "" : "model-unavailable"}`}>
            <span className="status-dot" />
            {modelStatus.label}
          </div>
        </header>

        <div className="workspace">
          <section className="research-panel">
            <div className="welcome-heading">
              <span className="eyebrow">
                YOUR PERSONAL RESEARCH ASSISTANT
              </span>
              <h1>Turn documents into insights.</h1>
              <p>
                Upload a PDF, ask questions, and explore answers grounded
                in your document.
              </p>
            </div>

            <label className="upload-box">
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                disabled={uploading || asking || checkingDocument}
              />

              <span className="upload-icon">↑</span>
              <strong>
                {uploading ? "Uploading your document..." : "Upload a PDF"}
              </strong>
              <span className="upload-description">
                Choose a PDF from your computer (max 10 MB)
              </span>

              {fileName && (
                <span className="selected-file">📄 {fileName}</span>
              )}

              {documentAvailable && documentId && (
                <span className="upload-success">✓ PDF is available</span>
              )}

              {uploading && (
                <span className="upload-description">
                  Please wait while your document uploads.
                </span>
              )}

              {uploadError && (
                <span className="upload-error" role="alert">
                  {uploadError}
                </span>
              )}
            </label>

            {documentId && (
              <p className="document-id">Document ID: {documentId}</p>
            )}

            {checkingDocument && (
              <p className="upload-description">
                Checking document availability...
              </p>
            )}

            {documentId && !documentAvailable && !checkingDocument && (
              <p className="upload-error" role="alert">
                Upload this PDF again to continue asking questions.
              </p>
            )}

            <div className="chat-section">
              <div className="chat-heading">
                <div>
                  <h2>Research conversation</h2>
                  <p>Ask questions about your uploaded document.</p>
                </div>
                <span className="chat-count">
                  {messages.filter((message) => message.role === "user").length}{" "}
                  questions
                </span>
              </div>

              <div className="messages">
                {messages.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">✳</div>
                    <h3>What would you like to discover?</h3>
                    <p>
                      {documentAvailable
                        ? "Your PDF is ready. Ask your first question below."
                        : "Upload a PDF to begin your research."}
                    </p>

                    {documentAvailable && (
                      <div className="suggestion-list">
                        {[
                          "Summarize this document",
                          "What are the key findings?",
                          "Explain the main concepts",
                        ].map((suggestion) => (
                          <button
                            type="button"
                            className="suggestion"
                            key={suggestion}
                            onClick={() => setQuestion(suggestion)}
                          >
                            {suggestion} <span>↗</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <div
                      className={`message ${message.role}`}
                      key={message.id || `${message.role}-${index}`}
                    >
                      <div className="message-avatar">
                        {message.role === "user" ? "Y" : "R"}
                      </div>

                      <div className="message-content">
                        <strong>
                          {message.role === "user" ? "You" : "ResearchPilot"}
                        </strong>

                        <p>{message.text}</p>

                        {message.loading && (
                          <span className="loading-indicator">
                            <span />
                            <span />
                            <span />
                          </span>
                        )}

                        {message.confidence != null && (
                          <span className="confidence">
                            Confidence:{" "}
                            {typeof message.confidence === "number"
                              ? `${Math.round(
                                  message.confidence <= 1
                                    ? message.confidence * 100
                                    : message.confidence
                                )}%`
                              : message.confidence}
                          </span>
                        )}

                        {message.citations?.length > 0 && (
                          <div className="message-citations">
                            <strong>Sources used</strong>
                            {message.citations.map((citation, citationIndex) => (
                              <div
                                className="citation-item"
                                key={`${citation.chunk_id ?? "chunk"}-${citationIndex}`}
                              >
                                <span>
                                  [{citationIndex + 1}]{" "}
                                  {citation.source ||
                                    fileName ||
                                    "Uploaded document"}
                                  {" · Page "}
                                  {citation.page_number ?? "N/A"}
                                </span>
                                {citation.text && <p>{citation.text}</p>}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>

              <form className="question-form" onSubmit={handleSubmit}>
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder={
                    documentAvailable
                      ? "Ask anything about your PDF..."
                      : "Upload a PDF to start asking questions..."
                  }
                  rows={2}
                  disabled={
                    !documentId ||
                    !documentAvailable ||
                    checkingDocument ||
                    asking
                  }
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey &&
                      !event.nativeEvent.isComposing
                    ) {
                      event.preventDefault();
                      event.currentTarget.form?.requestSubmit();
                    }
                  }}
                />

                <div className="question-form-footer">
                  <span>Enter to send · Shift + Enter for a new line</span>
                  <button
                    type="submit"
                    disabled={
                      !question.trim() ||
                      !documentId ||
                      !documentAvailable ||
                      checkingDocument ||
                      asking
                    }
                  >
                    {asking ? "Researching..." : "Ask question ↗"}
                  </button>
                </div>
              </form>
            </div>
          </section>

          <aside className="sources-panel">
            <div className="sources-heading">
              <div>
                <span className="eyebrow">REFERENCE</span>
                <h2>Sources & citations</h2>
              </div>
              <span className="source-count">{latestCitations.length}</span>
            </div>

            {!documentId ? (
              <div className="sources-empty">
                <span className="sources-icon">▤</span>
                <strong>No document loaded</strong>
                <p>
                  Reopen a saved conversation or upload a PDF to continue.
                </p>
              </div>
            ) : latestCitations.length === 0 ? (
              <div className="sources-empty">
                <span className="sources-icon">⌕</span>
                <strong>No citations yet</strong>
                <p>Sources will appear here after you ask a question.</p>
              </div>
            ) : (
              <div className="source-list">
                {latestCitations.map((citation, index) => (
                  <article
                    className="source-card"
                    key={`${citation.chunk_id ?? "source"}-${index}`}
                  >
                    <div className="source-card-top">
                      <span className="source-number">[{index + 1}]</span>
                      <span className="page-badge">
                        Page {citation.page_number ?? "N/A"}
                      </span>
                    </div>
                    <strong>
                      {citation.source || fileName || "Uploaded PDF"}
                    </strong>
                    {citation.text ? (
                      <p>{citation.text}</p>
                    ) : (
                      <p>Referenced in the generated answer.</p>
                    )}
                  </article>
                ))}
              </div>
            )}

            <div className="privacy-note">
              <span>🔒</span>
              <p>
                <strong>Private by design</strong>
                <br />
                Research history is stored in your backend SQLite database.
                Uploaded PDFs remain in backend storage.
              </p>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}

export default App;
