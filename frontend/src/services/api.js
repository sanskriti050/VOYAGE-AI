// Uses Vite proxy — requests to /api/* are forwarded to http://127.0.0.1:8000/*
const API_URL = "/api";

export async function generateTrip(tripData) {
  const response = await fetch(`${API_URL}/generate-trip`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(tripData),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }

  return response.json();
}
