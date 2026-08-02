/**
 * BudgetOptimizer — shows smart budget allocation breakdown.
 * Receives budget_optimization object from the trip result.
 */

const CATEGORY_ICONS = {
  travel: "✈️",
  hotels: "🏨",
  food: "🍛",
  local_transport: "🚕",
  activities: "🎯",
  miscellaneous: "🛍️",
};

const CATEGORY_COLORS = {
  travel: "#3b82f6",
  hotels: "#7c3aed",
  food: "#f59e0b",
  local_transport: "#10b981",
  activities: "#ef4444",
  miscellaneous: "#6b7280",
};

const HEALTH_CONFIG = {
  Excellent: { bg: "#f0fdf4", border: "#86efac", text: "#166534", icon: "🌟" },
  Good:      { bg: "#eff6ff", border: "#93c5fd", text: "#1e40af", icon: "✅" },
  Tight:     { bg: "#fffbeb", border: "#fcd34d", text: "#92400e", icon: "⚠️" },
  "Very Tight": { bg: "#fef2f2", border: "#fca5a5", text: "#991b1b", icon: "🚨" },
};

function BudgetOptimizer({ data }) {
  if (!data) return null;

  const {
    allocation = {},
    per_person_per_day = {},
    total_budget,
    currency_symbol: sym = "₹",
    members,
    days,
    budget_health_label,
    budget_health_score,
    budget_per_person,
    budget_per_person_per_day,
    saving_suggestions = [],
    optimization_tips = [],
  } = data;

  const health = HEALTH_CONFIG[budget_health_label] || HEALTH_CONFIG["Tight"];
  const categories = Object.keys(allocation);
  const maxAmt = Math.max(...Object.values(allocation));
  const isRupee = sym === "\u20b9" || sym === "Rs" || sym === "INR" || sym === "&#8377;";

  // Smart formatter
  const fmt = (n) => {
    const rupeeSym = "\u20b9"; // ₹
    if (isRupee) {
      if (n >= 100000) return `${rupeeSym}${(n / 100000).toFixed(1)}L`;
      if (n >= 1000)   return `${rupeeSym}${(n / 1000).toFixed(1)}K`;
      return `${rupeeSym}${Math.round(n).toLocaleString("en-IN")}`;
    }
    if (n >= 1000) return `${sym}${(n / 1000).toFixed(1)}K`;
    return `${sym}${Math.round(n).toLocaleString()}`;
  };

  return (
    <div className="budget-opt-container">
      {/* Health Badge */}
      <div
        className="budget-health-badge"
        style={{ background: health.bg, borderColor: health.border, color: health.text }}
      >
        <span className="health-icon">{health.icon}</span>
        <div>
          <strong>Budget Health: {budget_health_label}</strong>
          <p>
            {fmt(budget_per_person)} per person · {fmt(budget_per_person_per_day)}/day/person
          </p>
        </div>
        <div className="health-score-circle" style={{ color: health.text, borderColor: health.border }}>
          <span>{budget_health_score}</span>
          <small>/100</small>
        </div>
      </div>

      {/* Allocation Bars */}
      <div className="budget-opt-bars">
        <h5>💰 Smart Allocation ({members} people · {days} days)</h5>
        {categories.map((cat) => {
          const amt = allocation[cat] || 0;
          const ppd = per_person_per_day[cat] || 0;
          const pct = maxAmt > 0 ? (amt / maxAmt) * 100 : 0;
          const color = CATEGORY_COLORS[cat] || "#6b7280";
          const icon = CATEGORY_ICONS[cat] || "📦";
          return (
            <div key={cat} className="opt-bar-row">
              <div className="opt-bar-label">
                <span>{icon} {cat.replace("_", " ")}</span>
                <span className="opt-bar-amount">{fmt(amt)}</span>
              </div>
              <div className="opt-bar-track">
                <div
                  className="opt-bar-fill"
                  style={{ width: `${pct}%`, background: color }}
                />
              </div>
              <span className="opt-bar-ppd">{fmt(ppd)}/day per person</span>
            </div>
          );
        })}
      </div>

      {/* Optimization Tips */}
      {optimization_tips.length > 0 && (
        <div className="opt-tips">
          {optimization_tips.map((tip, i) => (
            <div key={i} className="opt-tip-row">{tip}</div>
          ))}
        </div>
      )}

      {/* Saving Suggestions */}
      {saving_suggestions.length > 0 && (
        <div className="opt-savings">
          <h5>🪄 Money-Saving Tips</h5>
          <div className="opt-savings-grid">
            {saving_suggestions.map((s, i) => (
              <div key={i} className="opt-saving-card">
                <span className="saving-cat">{s.category}</span>
                <p>{s.tip}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default BudgetOptimizer;
