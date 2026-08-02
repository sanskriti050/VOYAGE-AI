/**
 * RecommendationEngine — shows personalized destination suggestions
 * based on trip type, budget, and semantic similarity.
 */

const SCORE_COLOR = (score) => {
  if (score >= 0.5) return "#22c55e";
  if (score >= 0.3) return "#f59e0b";
  return "#94a3b8";
};

const TRIP_TYPE_EMOJIS = {
  Solo: "🧍", Couple: "👫", Family: "👨‍👩‍👧",
  Friends: "👯", Honeymoon: "💍",
};

function RecommendationEngine({ recommendations = [], tripType = "Friends", basedOn = {} }) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="rec-container">
      <div className="rec-header">
        <h4>
          {TRIP_TYPE_EMOJIS[tripType] || "✨"} You Might Also Love
        </h4>
        <p>
          Personalised picks for {tripType} trips similar to{" "}
          <strong>{basedOn.destination || "your destination"}</strong>
        </p>
      </div>

      <div className="rec-grid">
        {recommendations.map((rec, i) => {
          const scoreColor = SCORE_COLOR(rec.score);
          const scorePct = Math.round(rec.score * 100);
          return (
            <div key={i} className="rec-card">
              <div className="rec-card-top">
                <div>
                  <span className="rec-dest">{rec.destination}</span>
                  <span className="rec-country">{rec.country}</span>
                </div>
                <div
                  className="rec-score-badge"
                  style={{ background: `${scoreColor}18`, color: scoreColor, borderColor: `${scoreColor}40` }}
                >
                  {scorePct}%
                </div>
              </div>

              <div className="rec-score-bar-track">
                <div
                  className="rec-score-bar-fill"
                  style={{ width: `${Math.min(scorePct * 1.5, 100)}%`, background: scoreColor }}
                />
              </div>

              <p className="rec-why">{rec.why}</p>

              <div className="rec-tags">
                {rec.tags.slice(0, 4).map((tag, ti) => (
                  <span key={ti} className="rec-tag">{tag}</span>
                ))}
              </div>

              <div className="rec-meta">
                <span>🗓️ {rec.best_months}</span>
                <span>💰 {rec.budget_level}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default RecommendationEngine;
