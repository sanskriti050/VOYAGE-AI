import { useState } from "react";
import { searchDestinations } from "../services/api";

/**
 * SemanticSearch — searches destinations using embedding-based similarity.
 * Shown in the planner above the form as a discovery tool.
 */
function SemanticSearch({ onSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(false);
    try {
      const data = await searchDestinations(query.trim(), 5);
      setResults(data.results || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
      setSearched(true);
    }
  };

  const scoreBar = (score) => {
    const pct = Math.round(score * 100);
    const color =
      pct >= 60 ? "#22c55e" : pct >= 35 ? "#f59e0b" : "#94a3b8";
    return (
      <div className="sem-score-bar">
        <div
          className="sem-score-fill"
          style={{ width: `${Math.min(pct * 2, 100)}%`, background: color }}
        />
        <span className="sem-score-label">{pct}% match</span>
      </div>
    );
  };

  return (
    <div className="semantic-search-box">
      <div className="sem-search-header">
        <span className="sem-search-icon">🔍</span>
        <div>
          <h4>Smart Destination Search</h4>
          <p>Describe your dream trip in natural language</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="sem-search-form">
        <input
          type="text"
          className="sem-search-input"
          placeholder='e.g. "romantic beach honeymoon" or "budget mountain adventure friends"'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="sem-search-btn" disabled={loading}>
          {loading ? <span className="sem-spinner" /> : "Search"}
        </button>
      </form>

      {searched && results.length === 0 && (
        <p className="sem-no-results">No matching destinations found. Try different keywords.</p>
      )}

      {results.length > 0 && (
        <div className="sem-results">
          {results.map((r, i) => (
            <div className="sem-result-card" key={i}>
              <div className="sem-result-top">
                <div>
                  <span className="sem-dest-name">{r.destination}</span>
                  <span className="sem-country">{r.country}</span>
                </div>
                <span className="sem-budget-badge">{r.budget_level}</span>
              </div>
              {scoreBar(r.similarity_score)}
              <div className="sem-tags">
                {r.tags.slice(0, 5).map((tag, ti) => (
                  <span key={ti} className="sem-tag">{tag}</span>
                ))}
              </div>
              <p className="sem-best-time">🗓️ Best time: {r.best_months}</p>
              <button
                className="sem-pick-btn"
                onClick={() => onSelect && onSelect(r.destination)}
              >
                Plan this trip →
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SemanticSearch;
