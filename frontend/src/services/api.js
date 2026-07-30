// Deployed Render backend. Calling it directly avoids a missing /api rewrite (404).
const API_URL = "https://voyage-ai-2.onrender.com";

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
