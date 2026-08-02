// LOCAL DEV  → http://localhost:8000  (run: uvicorn main:app --reload --port 8000)
// PRODUCTION → https://voyage-ai-2.onrender.com  (deployed Render backend)
//
// Change this ONE line to switch between local and prod:
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function generateTrip(tripData) {
  const response = await fetch(`${API_URL}/generate-trip`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(tripData),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }
  return response.json();
}

export async function searchDestinations(query, topK = 5) {
  const response = await fetch(`${API_URL}/search-destinations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!response.ok) throw new Error(`Search error: ${response.status}`);
  return response.json();
}

export async function optimizeBudget(payload) {
  const response = await fetch(`${API_URL}/optimize-budget`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`Budget optimizer error: ${response.status}`);
  return response.json();
}

export async function optimizeRoute(cities, travelMode = "Flight", startCity = "") {
  const response = await fetch(`${API_URL}/optimize-route`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cities, travel_mode: travelMode, start_city: startCity }),
  });
  if (!response.ok) throw new Error(`Route optimizer error: ${response.status}`);
  return response.json();
}

export async function getRecommendations(payload) {
  const response = await fetch(`${API_URL}/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`Recommendations error: ${response.status}`);
  return response.json();
}

// ── AI Travel Assistant Chat ─────────────────────────────────────
export async function sendChatMessage(message, history = [], tripContext = null) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history, trip_context: tripContext }),
  });
  if (!response.ok) throw new Error(`Chat error: ${response.status}`);
  return response.json();
}
