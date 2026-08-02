import { useState } from "react";
import { optimizeRoute } from "../services/api";

const MODE_ICONS = {
  Flight: "✈️", Train: "🚂", Car: "🚗", Bus: "🚌", Bike: "🏍️",
};

function RouteOptimizer({
  defaultStart = "",
  defaultDestination = "",
  defaultMode = "Flight",
  isInternational = false,
  currencySymbol = "₹",
}) {
  // Pre-fill: source city as first, destination as second, two empty slots after
  const buildInitialCities = () => {
    const list = [];
    if (defaultStart) list.push(defaultStart);
    if (defaultDestination) list.push(defaultDestination);
    // Add empty slots up to at least 3 total
    while (list.length < 3) list.push("");
    return list;
  };

  const [cities, setCities] = useState(buildInitialCities);
  const [mode, setMode] = useState(defaultMode);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addCity = () => setCities((prev) => [...prev, ""]);
  const removeCity = (i) => {
    if (cities.length <= 2) return;
    setCities((prev) => prev.filter((_, idx) => idx !== i));
  };
  const updateCity = (i, val) => {
    setCities((prev) => {
      const c = [...prev];
      c[i] = val;
      return c;
    });
  };

  const handleOptimize = async (e) => {
    e.preventDefault();
    const filtered = cities.map((c) => c.trim()).filter(Boolean);
    if (filtered.length < 2) {
      setError("Please enter at least 2 cities to optimize the route.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await optimizeRoute(filtered, mode, filtered[0]);
      setResult({ ...data, travel_mode: mode });
    } catch (err) {
      setError(err.message || "Route optimization failed. Please check city names and try again.");
    } finally {
      setLoading(false);
    }
  };

  // Format cost — INR for domestic, foreign currency for international
  const fmtCost = (inrAmt) => {
    const rupeeSym = "\u20b9"; // ₹
    if (!isInternational) {
      return `${rupeeSym}${inrAmt?.toLocaleString("en-IN")}`;
    }
    return `~${currencySymbol}${Math.round(inrAmt / 83)}`;
  };

  const MODES = ["Flight", "Train", "Car", "Bus", "Bike"];
  const isOptimal = result && result.distance_saved_km === 0;
  const isSaved   = result && result.distance_saved_km > 0;

  return (
    <div className="route-opt-container">
      <div className="route-opt-header">
        <h4>🗺️ Multi-City Route Optimizer</h4>
        <p>Add all cities you want to visit — we'll find the shortest travel order</p>
      </div>

      <form onSubmit={handleOptimize} className="route-form">
        <div className="route-cities-list">
          {cities.map((city, i) => (
            <div key={i} className="route-city-row">
              <div className="route-city-badge" data-type={i === 0 ? "start" : "stop"}>
                {i === 0 ? "🏠" : i === cities.length - 1 ? "🏁" : `${i}`}
              </div>
              <input
                type="text"
                className="route-city-input"
                placeholder={
                  i === 0
                    ? "Starting city (e.g. Delhi)"
                    : i === 1
                    ? "Next city (e.g. Jaipur)"
                    : `Stop ${i + 1} (e.g. Agra)`
                }
                value={city}
                onChange={(e) => updateCity(i, e.target.value)}
              />
              {cities.length > 2 && (
                <button
                  type="button"
                  className="route-remove-btn"
                  onClick={() => removeCity(i)}
                  title="Remove this city"
                  aria-label="Remove city"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>

        <button type="button" className="route-add-btn" onClick={addCity}>
          + Add another city
        </button>

        <div className="route-mode-row">
          <label>Travel by:</label>
          <div className="route-mode-pills">
            {MODES.map((m) => (
              <button
                key={m}
                type="button"
                className={`route-mode-pill ${mode === m ? "active" : ""}`}
                onClick={() => setMode(m)}
              >
                {MODE_ICONS[m]} {m}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" className="route-optimize-btn" disabled={loading}>
          {loading
            ? <><span className="sem-spinner" /> Optimizing route…</>
            : "⚡ Find Optimal Route"}
        </button>
      </form>

      {error && <div className="route-error">⚠️ {error}</div>}

      {result && !result.error && (
        <div className="route-result">

          {/* ── Optimal / Saved Banner ── */}
          {isOptimal && (
            <div className="route-already-optimal">
              ✅ Your original route is already optimal! No changes needed.
            </div>
          )}
          {isSaved && (
            <div className="route-saved-banner">
              🎉 Optimized! Saved <strong>{result.distance_saved_km?.toLocaleString()} km</strong>
              {" "}({result.savings_percentage}% shorter journey)
            </div>
          )}

          {/* ── Before vs After ── */}
          <div className="route-comparison">
            <div className="route-col">
              <div className="route-col-label original-label">📍 Your Order</div>
              <div className="route-path">
                {result.original_route.map((c, i) => (
                  <span key={i} className="rpath-item">
                    <span className="rpath-city">{c}</span>
                    {i < result.original_route.length - 1 && (
                      <span className="rpath-arrow">→</span>
                    )}
                  </span>
                ))}
              </div>
              <p className="route-dist-info">
                {result.original_distance_km?.toLocaleString()} km total
              </p>
            </div>

            {!isOptimal && (
              <div className="route-col">
                <div className="route-col-label optimized-label">✨ Best Order</div>
                <div className="route-path">
                  {result.optimized_route.map((c, i) => (
                    <span key={i} className="rpath-item">
                      <span className="rpath-city optimized">{c}</span>
                      {i < result.optimized_route.length - 1 && (
                        <span className="rpath-arrow">→</span>
                      )}
                    </span>
                  ))}
                </div>
                <p className="route-dist-info optimized-info">
                  {result.total_distance_km?.toLocaleString()} km total
                  <span className="saving-chip">
                    −{result.distance_saved_km?.toLocaleString()} km
                  </span>
                </p>
              </div>
            )}
          </div>

          {/* ── Journey Legs ── */}
          <div className="route-legs">
            <div className="route-legs-title">
              🛤️ Journey Breakdown · {MODE_ICONS[mode]} {mode}
            </div>
            {result.legs.map((leg, i) => (
              <div key={i} className="route-leg-card">
                <div className="leg-step">{i + 1}</div>
                <div className="leg-body">
                  <div className="leg-cities">
                    <span className="leg-from">{leg.from}</span>
                    <span className="leg-connector">
                      {MODE_ICONS[mode]} ────→
                    </span>
                    <span className="leg-to">{leg.to}</span>
                  </div>
                  <div className="leg-stats">
                    <span className="leg-stat">
                      📏 <strong>{leg.distance_km?.toLocaleString()} km</strong>
                    </span>
                    <span className="leg-stat">
                      ⏱️ <strong>{leg.estimated_time}</strong>
                    </span>
                    <span className="leg-stat">
                      💰 <strong>{fmtCost(leg.estimated_cost_inr)}</strong> est.
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* ── Summary Cards ── */}
          <div className="route-summary">
            <div className="route-sum-card">
              <span className="sum-icon">📏</span>
              <div>
                <span className="sum-label">Total Distance</span>
                <strong>{result.total_distance_km?.toLocaleString()} km</strong>
              </div>
            </div>
            <div className="route-sum-card">
              <span className="sum-icon">💰</span>
              <div>
                <span className="sum-label">Est. Travel Cost</span>
                <strong>{fmtCost(result.total_estimated_cost_inr)}</strong>
              </div>
            </div>
            <div className="route-sum-card">
              <span className="sum-icon">🚌</span>
              <div>
                <span className="sum-label">Travel Mode</span>
                <strong>{MODE_ICONS[mode]} {mode}</strong>
              </div>
            </div>
            {isSaved && (
              <div className="route-sum-card saved-card">
                <span className="sum-icon">🎯</span>
                <div>
                  <span className="sum-label">Distance Saved</span>
                  <strong>{result.distance_saved_km?.toLocaleString()} km ({result.savings_percentage}%)</strong>
                </div>
              </div>
            )}
          </div>

          {result.unresolved_cities?.length > 0 && (
            <div className="route-unresolved">
              ⚠️ Couldn't find location data for: <strong>{result.unresolved_cities.join(", ")}</strong>.
              Try using the full city name.
            </div>
          )}
        </div>
      )}

      {result?.error && (
        <div className="route-error">⚠️ {result.error}</div>
      )}
    </div>
  );
}

export default RouteOptimizer;
