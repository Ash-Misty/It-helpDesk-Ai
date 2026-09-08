const API_BASE_URL = "http://localhost:8000/api";

export async function postQuery(message) {
  const response = await fetch(`${API_BASE_URL}/queries`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to send query.");
  }

  return response.json();
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("Health check failed.");
  }
  return response.json();
}

export async function classifyQuery(message) {
  const response = await fetch(`${API_BASE_URL}/classify`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to classify query.");
  }

  return response.json();
}

export async function createTicket(data) {
  const response = await fetch(`${API_BASE_URL}/tickets`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to create ticket.");
  }

  return response.json();
}

export async function analyzeTicket(ticketId) {
  const response = await fetch(`${API_BASE_URL}/agent/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ticket_id: ticketId }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to analyze ticket.");
  }

  return response.json();
}

export async function initializeState(ticketId) {
  const response = await fetch(`${API_BASE_URL}/state/${ticketId}/initialize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to initialize state.");
  }

  return response.json();
}

export async function getState(ticketId) {
  const response = await fetch(`${API_BASE_URL}/state/${ticketId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to get state.");
  }

  return response.json();
}

export async function addAnswer(ticketId, question, answer) {
  const response = await fetch(`${API_BASE_URL}/state/${ticketId}/answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, answer }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to add answer.");
  }

  return response.json();
}

export async function completeStep(ticketId) {
  const response = await fetch(`${API_BASE_URL}/state/${ticketId}/complete-step`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to complete step.");
  }

  return response.json();
}

export async function executeAgent(ticketId) {
  const response = await fetch(`${API_BASE_URL}/agent/execute`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ticket_id: ticketId }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to execute agent.");
  }

  return response.json();
}
