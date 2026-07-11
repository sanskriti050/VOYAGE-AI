import { useState } from "react";

function TripForm() {
  const [formData, setFormData] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const res = await fetch("https://voyage-ai-cp93.onrender.com/generate-trip", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        destination: formData,
        days: 3,
        budget: 15000,
      }),
    });

    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="trip-section">

      <h2>🧠 Plan Your Trip with AI</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="e.g. Goa / Manali / Kashmir"
          value={formData}
          onChange={(e) => setFormData(e.target.value)}
        />

        <button type="submit">
          {loading ? "Generating..." : "Generate Trip"}
        </button>
      </form>

      {/* RESULT SHOW */}
      {result && (
        <div style={{ marginTop: "30px", textAlign: "left" }}>
          <h3>📍 AI Result:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

    </div>
  );
}

export default TripForm;