
const STORAGE_KEY = "researchpilot_conversations";
const MAX_SESSIONS = 30;

function readHistory() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);

    if (!stored) return [];

    const parsed = JSON.parse(stored);

    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.error("Unable to read research history:", error);
    return [];
  }
}

export function getHistory() {
  return readHistory();
}

export function saveSession(session) {
  const history = readHistory();

  const updatedSession = {
    ...session,
    updatedAt: new Date().toISOString(),
  };

  const remainingSessions = history.filter(
    (item) => item.id !== updatedSession.id
  );

  const updatedHistory = [
    updatedSession,
    ...remainingSessions,
  ].slice(0, MAX_SESSIONS);

  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(updatedHistory)
    );

    return updatedSession;
  } catch (error) {
    console.error("Unable to save research history:", error);
    throw new Error(
      "Could not save history. Browser storage may be full.",
      { cause: error }
    );
  }
}

export function deleteSession(sessionId) {
  const updatedHistory = readHistory().filter(
    (session) => session.id !== sessionId
  );

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(updatedHistory)
  );

  return updatedHistory;
}

export function clearHistory() {
  localStorage.removeItem(STORAGE_KEY);
}
