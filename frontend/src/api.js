
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export async function getOllamaHealth() {
  const response = await fetch(`${API_BASE_URL}/health/ollama`);
  return parseResponse(response);
}

// Parse API responses and handle errors.
async function parseResponse(response) {
  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("The server returned an invalid response.");
  }

  if (!response.ok) {
    const detail = data?.detail;

    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(", ")
      : typeof detail === "string"
        ? detail
        : "Something went wrong.";

    throw new Error(message);
  }

  return data;
}

// Upload a PDF document.
export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  return parseResponse(response);
}

// Ask a question about an uploaded document.
export async function askQuestion(documentId, question) {
  const response = await fetch(
    `${API_BASE_URL}/api/documents/${encodeURIComponent(
      documentId
    )}/answer`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        top_k: 3,
        min_score: 0.1,
      }),
    }
  );

  return parseResponse(response);
}

// Get the list of uploaded documents.
export async function getUploadedDocuments() {
  const response = await fetch(
    `${API_BASE_URL}/api/documents`
  );

  return parseResponse(response);
}

// Get saved research sessions.
// Optional query filters sessions by title.
export async function getResearchHistory(query = "") {
  const params = new URLSearchParams();

  if (query.trim()) {
    params.set("q", query.trim());
  }

  const queryString = params.toString();
  const url = `${API_BASE_URL}/api/history${
    queryString ? `?${queryString}` : ""
  }`;

  const response = await fetch(url);

  return parseResponse(response);
}

// Get a single saved research session and its messages.
export async function getResearchSession(sessionId) {
  const response = await fetch(
    `${API_BASE_URL}/api/history/${encodeURIComponent(
      sessionId
    )}`
  );

  return parseResponse(response);
}

// Save or update a research session in SQLite.
export async function saveResearchSession(session) {
  const payload = {
    id: session.id,
    title: session.title || "New research",
    document_id:
      session.documentId || session.document_id || "",
    file_name:
      session.fileName || session.file_name || "",
    created_at:
      session.createdAt ||
      session.created_at ||
      new Date().toISOString(),
    messages: (session.messages || [])
      .filter(
        (message) =>
          message.role === "user" ||
          message.role === "assistant"
      )
      .map((message) => ({
        id: message.id,
        role: message.role,
        text: message.text,
        citations: message.citations || [],
        confidence: message.confidence ?? null,
        created_at:
          message.createdAt ||
          message.created_at ||
          null,
      })),
  };

  const response = await fetch(
    `${API_BASE_URL}/api/history`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  return parseResponse(response);
}

// Delete a saved research session.
export async function deleteResearchSession(sessionId) {
  const response = await fetch(
    `${API_BASE_URL}/api/history/${encodeURIComponent(
      sessionId
    )}`,
    {
      method: "DELETE",
    }
  );

  return parseResponse(response);
}

// Migrate sessions from the old localStorage history to SQLite.
export async function migrateLegacyHistory(sessions) {
  const existingData = await getResearchHistory();
  const existingIds = new Set(
    (existingData.sessions || []).map((item) => item.id)
  );

  let migrated = 0;
  let skipped = 0;
  const errors = [];

  for (const session of sessions || []) {
    if (!session?.id || existingIds.has(session.id)) {
      skipped++;
      continue;
    }

    try {
      await saveResearchSession(session);
      existingIds.add(session.id);
      migrated++;
    } catch (error) {
      errors.push({
        sessionId: session.id,
        message: error.message,
      });
    }
  }

  return {
    migrated,
    skipped,
    errors,
  };
}
