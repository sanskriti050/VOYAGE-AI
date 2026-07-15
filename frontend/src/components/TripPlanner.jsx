import { useState, useEffect, useMemo } from "react";
import "./TripPlanner.css";
import ResultCard from "./ResultCard";

/* ── Travel facts ── */
const TRAVEL_FACTS = [
  "🌍 There are 195 countries in the world — how many have you visited?",
  "✈️ The world's longest non-stop flight is 19 hours from Singapore to New York.",
  "🗺️ France is the most visited country in the world with 90 million tourists a year.",
  "🏔️ India has 9 of the 14 tallest mountain peaks in the world.",
  "🌊 The Maldives is the world's lowest-lying country — just 1.5m above sea level.",
  "🍜 Japan has more Michelin-starred restaurants than any other country.",
  "🏝️ Indonesia has over 17,000 islands — the most of any country.",
  "🚂 India's railway network is the 4th largest in the world.",
  "🌸 Japan's cherry blossom season lasts only about 2 weeks each year.",
  "🐘 Thailand's national symbol is the elephant — revered for centuries.",
  "💡 The Eiffel Tower grows 15cm taller in summer due to heat expansion.",
  "🏰 There are more than 25,000 castles in Europe.",
  "🌴 Bali has more temples than houses — over 20,000 temples on the island.",
  "🎭 Venice has no cars — it runs entirely on boats and walking.",
  "⛩️ There are over 80,000 Shinto shrines in Japan.",
];

function LoadingScreen() {
  const [factIdx, setFactIdx] = useState(0);
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const ft = setInterval(() => setFactIdx((i) => (i + 1) % TRAVEL_FACTS.length), 3000);
    const pt = setInterval(() => setProgress((p) => Math.min(p + 2, 92)), 600);
    return () => { clearInterval(ft); clearInterval(pt); };
  }, []);
  return (
    <div className="loading-screen">
      <div className="loading-globe">🌍</div>
      <h3>Building your perfect trip plan...</h3>
      <div className="loading-bar-wrap">
        <div className="loading-bar-fill" style={{ width: `${progress}%` }} />
      </div>
      <p className="loading-fact">{TRAVEL_FACTS[factIdx]}</p>
      <p className="loading-sub">Powered by Google Gemini AI</p>
    </div>
  );
}

/* ── Recent trips ── */
function RecentTrips({ onLoad }) {
  const trips = JSON.parse(localStorage.getItem("voyageai_recent") || "[]");
  if (!trips.length) return null;
  return (
    <div className="recent-trips">
      <h4>🕒 Recent Plans</h4>
      <div className="recent-list">
        {trips.map((t, i) => (
          <button key={i} className="recent-chip" onClick={() => onLoad(t)}>
            {t.source_city} → {t.destination}
            <span>{t.days}d · {t.members}p</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function saveToRecent(tripData) {
  const existing = JSON.parse(localStorage.getItem("voyageai_recent") || "[]");
  const updated = [tripData, ...existing.filter(
    (t) => !(t.source_city === tripData.source_city && t.destination === tripData.destination)
  )].slice(0, 5);
  localStorage.setItem("voyageai_recent", JSON.stringify(updated));
}

/* ── Smart travel mode logic ── */
const INDIA_KW = [
  "india","goa","manali","kashmir","rajasthan","mumbai","delhi","bangalore",
  "bengaluru","chennai","kolkata","kerala","himachal","uttarakhand","jaipur",
  "agra","varanasi","ladakh","sikkim","meghalaya","assam","ooty","coorg",
  "munnar","shimla","mussoorie","rishikesh","haridwar","amritsar","pune",
  "hyderabad","ahmedabad","leh","spiti","andaman","lakshadweep","darjeeling",
  "gangtok","kochi","trivandrum","mysore","udaipur","jodhpur","pushkar",
  "hampi","alleppey","kodaikanal","mount abu","nainital","jim corbett","rann",
  "kutch","diu","daman","pondicherry","coimbatore","madurai","vizag",
  "visakhapatnam","bhubaneswar","puri","patna","lucknow","kanpur","nagpur",
  "surat","indore","bhopal","raipur","ranchi","guwahati","imphal","aizawl",
  "kohima","itanagar","shillong","agartala","panaji","dehradun","chandigarh",
  "jammu","srinagar","prayagraj","allahabad","vrindavan","mathura","dwarka",
  "somnath","tirupati","shirdi","bodh gaya","ajmer","ranthambore","kaziranga",
  "lonavala","mahabaleshwar","aurangabad","wayanad","varkala","kovalam",
  "rameshwaram","kanyakumari","mahabalipuram","thanjavur",
];

// Islands/remote that need flight even within India
const INDIA_FLIGHT_ONLY = ["andaman","lakshadweep","port blair","kavaratti"];

// Very close city pairs in India where flight doesn't operate
// Format: sorted pair → modes NOT available
const CLOSE_INDIA_PAIRS = [
  { cities: ["lucknow","prayagraj"],  noFlight: true, noBike: false },
  { cities: ["lucknow","kanpur"],     noFlight: true, noBike: false },
  { cities: ["delhi","agra"],         noFlight: true, noBike: false },
  { cities: ["delhi","jaipur"],       noFlight: true, noBike: false },
  { cities: ["mumbai","pune"],        noFlight: true, noBike: false },
  { cities: ["mumbai","lonavala"],    noFlight: true, noBike: false },
  { cities: ["mumbai","nashik"],      noFlight: true, noBike: false },
  { cities: ["bangalore","mysore"],   noFlight: true, noBike: false },
  { cities: ["bangalore","mysuru"],   noFlight: true, noBike: false },
  { cities: ["bangalore","ooty"],     noFlight: true, noBike: false },
  { cities: ["chennai","pondicherry"],noFlight: true, noBike: false },
  { cities: ["chennai","mahabalipuram"], noFlight: true, noBike: false },
  { cities: ["kolkata","darjeeling"], noFlight: true, noBike: false },
  { cities: ["delhi","chandigarh"],   noFlight: true, noBike: false },
  { cities: ["delhi","shimla"],       noFlight: true, noBike: false },
  { cities: ["delhi","mussoorie"],    noFlight: true, noBike: false },
  { cities: ["delhi","haridwar"],     noFlight: true, noBike: false },
  { cities: ["delhi","rishikesh"],    noFlight: true, noBike: false },
  { cities: ["delhi","dehradun"],     noFlight: true, noBike: false },
  { cities: ["delhi","mathura"],      noFlight: true, noBike: false },
  { cities: ["delhi","vrindavan"],    noFlight: true, noBike: false },
  { cities: ["agra","varanasi"],      noFlight: false,noBike: false },
  { cities: ["prayagraj","varanasi"], noFlight: true, noBike: false },
  { cities: ["indore","bhopal"],      noFlight: true, noBike: false },
  { cities: ["jaipur","ajmer"],       noFlight: true, noBike: false },
  { cities: ["jaipur","pushkar"],     noFlight: true, noBike: false },
  { cities: ["jaipur","udaipur"],     noFlight: false,noBike: false },
  { cities: ["udaipur","jodhpur"],    noFlight: false,noBike: false },
  { cities: ["hyderabad","warangal"], noFlight: true, noBike: false },
  { cities: ["kochi","alleppey"],     noFlight: true, noBike: false },
  { cities: ["kochi","varkala"],      noFlight: true, noBike: false },
  { cities: ["kochi","kovalam"],      noFlight: true, noBike: false },
  { cities: ["kochi","trivandrum"],   noFlight: false,noBike: false },
];

/**
 * Returns object: { Flight, Train, Car, Bus, Bike }
 * Each value: { available: bool, reason: string }
 */
function getAvailableModes(source, destination) {
  const s = source.toLowerCase().trim();
  const d = destination.toLowerCase().trim();

  if (!s || !d) {
    return {
      Flight: { available: true,  reason: "" },
      Train:  { available: true,  reason: "" },
      Car:    { available: true,  reason: "" },
      Bus:    { available: true,  reason: "" },
      Bike:   { available: true,  reason: "" },
    };
  }

  const srcIndia  = INDIA_KW.some((k) => s.includes(k));
  const destIndia = INDIA_KW.some((k) => d.includes(k));

  // ── International trip ──────────────────────────────────────────
  if (!destIndia || !srcIndia) {
    return {
      Flight: { available: true,  reason: "" },
      Train:  { available: false, reason: "Train not available for international travel" },
      Car:    { available: false, reason: "Car / self-drive not feasible for international travel" },
      Bus:    { available: false, reason: "Bus not available for international travel" },
      Bike:   { available: false, reason: "Bike not available for international travel" },
    };
  }

  // ── Both India — island destination ────────────────────────────
  const destIsIsland = INDIA_FLIGHT_ONLY.some((k) => d.includes(k));
  if (destIsIsland) {
    return {
      Flight: { available: true,  reason: "" },
      Train:  { available: false, reason: "No train connectivity to this island destination" },
      Car:    { available: false, reason: "Car not available to island destination — need flight" },
      Bus:    { available: false, reason: "Bus not available to island destination — need flight" },
      Bike:   { available: false, reason: "Bike not available to island destination — need flight" },
    };
  }

  // ── Both India — check close pairs ─────────────────────────────
  const pair = CLOSE_INDIA_PAIRS.find((p) => {
    const [c0, c1] = p.cities;
    const fwd = (s.includes(c0) || c0.includes(s)) && (d.includes(c1) || c1.includes(d));
    const rev = (s.includes(c1) || c1.includes(s)) && (d.includes(c0) || c0.includes(d));
    return fwd || rev;
  });

  const noFlight = pair?.noFlight ?? false;
  const noBike   = pair?.noBike   ?? false;

  return {
    Flight: { available: !noFlight, reason: noFlight ? "No direct flights between these nearby cities" : "" },
    Train:  { available: true,      reason: "" },
    Car:    { available: true,      reason: "" },
    Bus:    { available: true,      reason: "" },
    Bike:   { available: !noBike,   reason: noBike ? "Bike not practical for this route" : "" },
  };
}

// ── Backend URL ──────────────────────────────────────────────────
const BACKEND_URL = "https://voyage-ai-2.onrender.com";

function TripPlanner() {
  const [trip, setTrip] = useState({
    source_city: "",
    destination: "",
    days: "",
    members: "",
    travel_mode: "Flight",
    trip_type: "Friends",
    budget: "",
  });

  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);
  const [waking,  setWaking]  = useState(false);

  // Wake up Render backend on mount (free tier sleeps after inactivity)
  useEffect(() => {
    setWaking(true);
    fetch(`${BACKEND_URL}/`)
      .catch(() => {})
      .finally(() => setWaking(false));
  }, []);

  // Compute available modes whenever source/dest changes
  const modes = useMemo(
    () => getAvailableModes(trip.source_city, trip.destination),
    [trip.source_city, trip.destination]
  );

  // Auto-switch selected mode if current becomes unavailable
  useEffect(() => {
    if (trip.travel_mode && !modes[trip.travel_mode]?.available) {
      const first = Object.entries(modes).find(([, v]) => v.available)?.[0];
      if (first) setTrip((prev) => ({ ...prev, travel_mode: first }));
    }
  }, [modes]);

  const handleChange = (e) => setTrip({ ...trip, [e.target.name]: e.target.value });
  const loadRecent   = (t) => setTrip({ ...t, days: String(t.days), members: String(t.members), budget: String(t.budget) });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      source_city: trip.source_city,
      destination: trip.destination,
      days:        Number(trip.days),
      members:     Number(trip.members),
      travel_mode: trip.travel_mode,
      trip_type:   trip.trip_type,
      budget:      Number(trip.budget),
    };

    try {
      const response = await fetch(`${BACKEND_URL}/generate-trip`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        const detail  = errData.detail || "";
        if (detail.includes("UNAUTHENTICATED") || detail.includes("API key"))  throw new Error("API_KEY_INVALID");
        if (detail.includes("quota exhausted")  || detail.includes("RESOURCE_EXHAUSTED")) throw new Error("QUOTA_EXHAUSTED");
        if (detail.includes("503") || detail.includes("UNAVAILABLE") || detail.includes("high demand")) throw new Error("SERVER_BUSY");
        throw new Error(`SERVER_${response.status}: ${detail.slice(0, 150)}`);
      }

      const data = await response.json();
      setResult(data);
      saveToRecent(payload);
      setTimeout(() => document.getElementById("trip-result")?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);

    } catch (err) {
      console.error(err);
      if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError") || err.message.includes("fetch")) {
        setError("Cannot connect to backend. The server may be waking up — please wait 30 seconds and try again.");
      } else if (err.message === "API_KEY_INVALID") {
        setError("Invalid Gemini API key. Get one free at https://aistudio.google.com/apikey");
      } else if (err.message === "QUOTA_EXHAUSTED") {
        setError("Gemini API quota exhausted. Wait a few minutes and try again.");
      } else if (err.message === "SERVER_BUSY") {
        setError("Gemini servers are busy right now (high demand). Please wait 30 seconds and try again — this is temporary.");
      } else {
        setError(`Something went wrong: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const TRIP_TYPES = [
    { value: "Solo",      label: "🧍 Solo"     },
    { value: "Couple",    label: "👫 Couple"   },
    { value: "Family",    label: "👨‍👩‍👧 Family" },
    { value: "Friends",   label: "👯 Friends"  },
    { value: "Honeymoon", label: "💍 Honeymoon"},
  ];

  const TRAVEL_MODES = [
    { value: "Flight", label: "✈️ Flight"          },
    { value: "Train",  label: "🚂 Train"            },
    { value: "Car",    label: "🚗 Car / Self Drive"  },
    { value: "Bus",    label: "🚌 Bus"              },
    { value: "Bike",   label: "🏍️ Bike"            },
  ];

  return (
    <section className="planner-section" id="planner">
      <div className="planner-container">
        <h2>✨ AI Travel Planner</h2>
        <p className="subtitle">Fill in your details and get a complete personalised trip plan instantly</p>

        {waking && (
          <div className="waking-banner">
            ⏳ Waking up the server... first load may take 30–60 seconds on free hosting.
          </div>
        )}

        <RecentTrips onLoad={loadRecent} />

        <form onSubmit={handleSubmit}>

          {/* Source & Destination */}
          <div className="form-group">
            <label>🏠 Travelling From</label>
            <input
              type="text" name="source_city"
              placeholder="e.g. Delhi, Mumbai, Lucknow"
              value={trip.source_city} onChange={handleChange} required
            />
          </div>

          <div className="form-group">
            <label>📍 Destination</label>
            <input
              type="text" name="destination"
              placeholder="e.g. Goa, Paris, Tokyo, Andaman"
              value={trip.destination} onChange={handleChange} required
            />
          </div>

          {/* Route preview */}
          {trip.source_city && trip.destination && (
            <div className="route-display full-width">
              <span className="route-from">{trip.source_city}</span>
              <span className="route-arrow">✈ ──────→</span>
              <span className="route-to">{trip.destination}</span>
            </div>
          )}

          {/* Days & Members */}
          <div className="form-group">
            <label>📅 Number of Days</label>
            <input
              type="number" name="days" placeholder="e.g. 5"
              min="1" max="30" value={trip.days} onChange={handleChange} required
            />
          </div>

          <div className="form-group">
            <label>👥 Number of Members</label>
            <input
              type="number" name="members" placeholder="e.g. 2"
              min="1" max="50" value={trip.members} onChange={handleChange} required
            />
          </div>

          {/* Trip Type */}
          <div className="form-group full-width">
            <label>🎯 Trip Type</label>
            <div className="trip-type-grid">
              {TRIP_TYPES.map((t) => (
                <button
                  key={t.value} type="button"
                  className={`trip-type-btn ${trip.trip_type === t.value ? "selected" : ""}`}
                  onClick={() => setTrip({ ...trip, trip_type: t.value })}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* ── Smart Travel Mode ── */}
          <div className="form-group full-width">
            <label>🚗 Mode of Travel</label>
            <div className="travel-mode-grid">
              {TRAVEL_MODES.map((m) => {
                const info      = modes[m.value] || { available: true, reason: "" };
                const isActive  = trip.travel_mode === m.value;
                const disabled  = !info.available;
                return (
                  <div
                    key={m.value}
                    className={`travel-mode-btn ${isActive ? "selected" : ""} ${disabled ? "disabled" : ""}`}
                    onClick={() => !disabled && setTrip({ ...trip, travel_mode: m.value })}
                    title={disabled ? info.reason : ""}
                  >
                    <span className="mode-label">{m.label}</span>
                    {disabled && (
                      <span className="mode-unavail">Not available</span>
                    )}
                  </div>
                );
              })}
            </div>
            {/* show reason for disabled modes */}
            {Object.entries(modes).some(([k, v]) => !v.available) && (
              <div className="mode-hint">
                {Object.entries(modes)
                  .filter(([, v]) => !v.available)
                  .map(([k, v]) => (
                    <span key={k}>⚠️ {v.reason}</span>
                  ))}
              </div>
            )}
          </div>

          {/* Budget */}
          <div className="form-group full-width">
            <label>
              💰 Total Budget
              <span className="label-hint"> (₹ for India · foreign currency for abroad)</span>
            </label>
            <input
              type="number" name="budget"
              placeholder="e.g. 25000 for India · 1500 for Paris ($)"
              min="1" value={trip.budget} onChange={handleChange} required
            />
          </div>

          <button type="submit" className="generate-btn" disabled={loading}>
            {loading ? (
              <span className="loading-text">
                <span className="spinner" /> Generating your personalised trip plan...
              </span>
            ) : "🚀 Generate AI Trip Plan"}
          </button>
        </form>

        {error && <div className="error-box">⚠️ {error}</div>}
        {loading && <LoadingScreen />}

        <div id="trip-result">
          {!loading && result && <ResultCard result={result} />}
        </div>
      </div>
    </section>
  );
}

export default TripPlanner;
