import { useState, useRef } from "react";

/* ─── helpers ──────────────────────────────────────────── */

function extractSection(text, heading) {
  const regex = new RegExp(`## ${heading}[\\s\\S]*?(?=## |$)`, "i");
  const match = text.match(regex);
  if (!match) return "";
  return match[0].replace(/^## .+\n/, "").trim();
}

function parseDays(itineraryText) {
  const dayBlocks = itineraryText.split(/### Day \d+/);
  const dayTitles = [...itineraryText.matchAll(/### Day (\d+)[:\s]*(.*)/g)];
  return dayTitles.map((match, i) => {
    const block     = dayBlocks[i + 1] || "";
    const morning   = block.match(/\*\*Morning:\*\*\s*([\s\S]*?)(?=\*\*Afternoon|\*\*Evening|$)/i)?.[1]?.trim() || "";
    const afternoon = block.match(/\*\*Afternoon:\*\*\s*([\s\S]*?)(?=\*\*Evening|$)/i)?.[1]?.trim() || "";
    const evening   = block.match(/\*\*Evening:\*\*\s*([\s\S]*?)$/i)?.[1]?.trim() || "";
    return { dayNum: match[1], title: match[2].trim(), morning, afternoon, evening };
  });
}

function parseBullets(text) {
  return text.split("\n")
    .filter((l) => l.trim().startsWith("-"))
    .map((line) => {
      const clean = line.replace(/^-\s*/, "");
      const m = clean.match(/\*\*(.+?)\*\*\s*[-–]?\s*(.*)/);
      return m ? { name: m[1], desc: m[2] } : { name: clean, desc: "" };
    });
}

function parseBudgetAssessment(text) {
  return {
    status:       text.match(/\*\*Status:\*\*\s*(.+)/i)?.[1]?.trim() || "",
    minimum:      text.match(/\*\*Minimum Recommended Budget:\*\*\s*(.+)/i)?.[1]?.trim() || "",
    comfortable:  text.match(/\*\*Comfortable Budget:\*\*\s*(.+)/i)?.[1]?.trim() || "",
    exchangeRate: text.match(/\*\*Exchange Rate:\*\*\s*(.+)/i)?.[1]?.trim() || "",
    assessment:   text.match(/\*\*Assessment:\*\*\s*([\s\S]*?)(?=\*\*|$)/i)?.[1]?.trim() || "",
  };
}

function parseTripScore(text) {
  const dims = ["Adventure", "Romance", "Food & Culture", "Value for Money", "Family Friendliness", "Overall"];
  return dims.map((dim) => {
    const regex = new RegExp(`\\*\\*${dim}:\\*\\*\\s*(\\d+)\\/10\\s*[—–-]?\\s*(.*)`, "i");
    const m = text.match(regex);
    return { dim, score: m ? parseInt(m[1]) : null, reason: m ? m[2].trim() : "" };
  }).filter((d) => d.score !== null);
}

function parsePackingList(text) {
  const categories = [];
  const catRegex = /\*\*(.+?):\*\*\n([\s\S]*?)(?=\*\*|$)/g;
  let m;
  while ((m = catRegex.exec(text)) !== null) {
    const items = m[2].split("\n").filter((l) => l.trim().startsWith("-"))
      .map((l) => l.replace(/^-\s*/, "").trim()).filter(Boolean);
    if (items.length) categories.push({ name: m[1].trim(), items });
  }
  return categories;
}

/* ─── Sub-components ───────────────────────────────────── */

function BudgetBanner({ assessment }) {
  if (!assessment.status) return null;
  const s = assessment.status.toUpperCase();
  const cfg = s.includes("VERY LOW")
    ? { bg: "#fef2f2", border: "#fca5a5", icon: "🚨", color: "#991b1b", label: "Budget Too Low" }
    : s.includes("LOW")
    ? { bg: "#fffbeb", border: "#fcd34d", icon: "⚠️", color: "#92400e", label: "Budget a Bit Low" }
    : { bg: "#f0fdf4", border: "#86efac", icon: "✅", color: "#166534", label: "Budget Looks Good!" };

  return (
    <div className="budget-banner" style={{ background: cfg.bg, borderColor: cfg.border }}>
      <div className="budget-banner-title" style={{ color: cfg.color }}>{cfg.icon} {cfg.label}</div>
      <div className="budget-banner-body" style={{ color: cfg.color }}>
        {assessment.assessment && <p>{assessment.assessment}</p>}
        <div className="budget-suggestions">
          {assessment.minimum     && <span className="budget-suggest-tag suggest-min">🔻 Minimum: {assessment.minimum}</span>}
          {assessment.comfortable && <span className="budget-suggest-tag suggest-comfortable">✅ Comfortable: {assessment.comfortable}</span>}
          {assessment.exchangeRate && <span className="budget-suggest-tag suggest-rate">💱 {assessment.exchangeRate}</span>}
        </div>
      </div>
    </div>
  );
}

const SCORE_COLORS = {
  "Adventure":          { color: "#f59e0b", bg: "#fef9c3" },
  "Romance":            { color: "#ec4899", bg: "#fce7f3" },
  "Food & Culture":     { color: "#f97316", bg: "#ffedd5" },
  "Value for Money":    { color: "#10b981", bg: "#d1fae5" },
  "Family Friendliness":{ color: "#3b82f6", bg: "#dbeafe" },
  "Overall":            { color: "#7c3aed", bg: "#ede9fe" },
};

function TripScoreCard({ scores }) {
  if (!scores.length) return null;
  const overall = scores.find((s) => s.dim === "Overall");
  const dims    = scores.filter((s) => s.dim !== "Overall");

  return (
    <div className="score-card">
      <div className="score-card-header">
        <div>
          <h3>🏆 Trip Score</h3>
          <p>AI-rated experience for this trip</p>
        </div>
        {overall && (
          <div className="overall-score" style={{ background: SCORE_COLORS["Overall"].bg, color: SCORE_COLORS["Overall"].color }}>
            <span className="overall-num">{overall.score}</span>
            <span className="overall-denom">/10</span>
            <div className="overall-label">Overall</div>
          </div>
        )}
      </div>
      <div className="score-dims">
        {dims.map((d) => {
          const c = SCORE_COLORS[d.dim] || { color: "#6366f1", bg: "#ede9fe" };
          return (
            <div className="score-dim" key={d.dim}>
              <div className="score-dim-top">
                <span className="score-dim-name">{d.dim}</span>
                <span className="score-dim-val" style={{ color: c.color }}>{d.score}/10</span>
              </div>
              <div className="score-bar-bg">
                <div
                  className="score-bar-fill"
                  style={{
                    width: `${d.score * 10}%`,
                    background: c.color,
                    transition: "width 1s ease",
                  }}
                />
              </div>
              {d.reason && <p className="score-dim-reason">{d.reason}</p>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── Main ResultCard ──────────────────────────────────── */

function ResultCard({ result }) {
  const [activeTab, setActiveTab] = useState("itinerary");
  const [checkedItems, setCheckedItems] = useState({});
  const printRef = useRef(null);

  if (!result) return null;

  const plan = result.ai_plan || "";
  const sym  = result.currency_symbol || "₹";

  const assessmentText  = extractSection(plan, "BUDGET ASSESSMENT");
  const scoreText       = extractSection(plan, "TRIP SCORE");
  const itineraryText   = extractSection(plan, "DAY-WISE ITINERARY");
  const hotelsText      = extractSection(plan, "BEST HOTELS");
  const foodText        = extractSection(plan, "MUST-TRY FOOD");
  const placesText      = extractSection(plan, "PLACES TO VISIT");
  const budgetText      = extractSection(plan, "BUDGET BREAKDOWN");
  const packingText     = extractSection(plan, "PACKING LIST");
  const emergencyText   = extractSection(plan, "EMERGENCY CONTACTS");
  const tipsText        = extractSection(plan, "TRAVEL TIPS");

  const assessment    = parseBudgetAssessment(assessmentText);
  const scores        = parseTripScore(scoreText);
  const days          = parseDays(itineraryText);
  const hotels        = parseBullets(hotelsText);
  const foods         = parseBullets(foodText);
  const places        = parseBullets(placesText);
  const budgetLines   = parseBullets(budgetText);
  const packingCats   = parsePackingList(packingText);
  const emergencyItems= parseBullets(emergencyText);
  const tips          = tipsText.split("\n").filter((l) => l.trim());

  const TRIP_TYPE_EMOJIS = {
    Solo: "🧍", Couple: "👫", Family: "👨‍👩‍👧", Friends: "👯", Honeymoon: "💍",
  };

  const tabs = [
    { id: "itinerary", label: "📅 Itinerary"  },
    { id: "score",     label: "🏆 Score"      },
    { id: "hotels",    label: "🏨 Hotels"     },
    { id: "food",      label: "🍛 Food"       },
    { id: "places",    label: "📸 Places"     },
    { id: "budget",    label: "💰 Budget"     },
    { id: "packing",   label: "🎒 Packing"    },
    { id: "emergency", label: "🆘 Emergency"  },
    { id: "tips",      label: "💡 Tips"       },
  ];

  const toggleCheck = (key) => setCheckedItems((prev) => ({ ...prev, [key]: !prev[key] }));

  const handlePrint = () => window.print();

  const handleShare = () => {
    const text = `✈️ Trip Plan: ${result.source_city} → ${result.destination}\n📅 ${result.days} Days | 👥 ${result.members} People | ${TRIP_TYPE_EMOJIS[result.trip_type] || "🎯"} ${result.trip_type} | ${sym}${Number(result.budget).toLocaleString()}\n🚀 Planned with VoyageAI`;
    navigator.clipboard.writeText(text).then(() => alert("Trip summary copied! Share it with your travel buddies 🎉"));
  };

  return (
    <div className="result-card" ref={printRef}>

      {/* ── HEADER ── */}
      <div className="result-header">
        <div className="result-header-top">
          <div>
            <div className="result-route">
              <span className="route-tag">{result.source_city || "Home"}</span>
              <span className="route-divider">✈ ─────→</span>
              <span className="route-tag route-dest">{result.destination}</span>
            </div>
            <h1>🌍 {result.destination} Trip Plan</h1>
          </div>
          <div className="header-actions no-print">
            <button className="action-btn" onClick={handlePrint}>🖨️ Print / PDF</button>
            <button className="action-btn" onClick={handleShare}>📋 Share</button>
          </div>
        </div>
        <div className="trip-meta">
          <span>📅 {result.days} Days</span>
          <span>👥 {result.members} {result.members === 1 ? "Person" : "People"}</span>
          <span>{TRIP_TYPE_EMOJIS[result.trip_type] || "🎯"} {result.trip_type}</span>
          <span>🚗 {result.travel_mode}</span>
          <span>💰 {sym}{Number(result.budget).toLocaleString()}</span>
        </div>
      </div>

      {/* ── BUDGET BANNER ── */}
      <div className="banner-wrapper">
        <BudgetBanner assessment={assessment} />
      </div>

      {/* ── TABS ── */}
      <div className="result-tabs no-print">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── CONTENT ── */}
      <div className="tab-content">

        {/* ITINERARY */}
        {activeTab === "itinerary" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">📅 Day-wise Itinerary</h3>
              <span className="section-meta">{result.days} days · {result.trip_type} trip</span>
            </div>
            {days.length > 0 ? days.map((day) => (
              <div className="day-card" key={day.dayNum}>
                <div className="day-header">
                  <span className="day-badge">Day {day.dayNum}</span>
                  {day.title && <span className="day-title">{day.title}</span>}
                </div>
                {day.morning   && <div className="time-slot"><span className="time-label morning-label">🌅 Morning</span><p>{day.morning}</p></div>}
                {day.afternoon && <div className="time-slot"><span className="time-label afternoon-label">☀️ Afternoon</span><p>{day.afternoon}</p></div>}
                {day.evening   && <div className="time-slot"><span className="time-label evening-label">🌙 Evening</span><p>{day.evening}</p></div>}
              </div>
            )) : <div className="raw-text">{itineraryText || plan}</div>}
          </div>
        )}

        {/* SCORE */}
        {activeTab === "score" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">🏆 Trip Score Card</h3>
              <span className="section-meta">AI-rated for your {result.trip_type} trip</span>
            </div>
            {scores.length > 0
              ? <TripScoreCard scores={scores} />
              : <div className="raw-text">{scoreText}</div>}
          </div>
        )}

        {/* HOTELS */}
        {activeTab === "hotels" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">🏨 Recommended Hotels</h3>
              <span className="section-meta">best for {result.trip_type} in {result.destination}</span>
            </div>
            <div className="cards-grid">
              {hotels.length > 0 ? hotels.map((h, i) => (
                <div className="info-card hotel-card" key={i}>
                  <div className="card-icon">🏨</div>
                  <h4>{h.name}</h4>
                  {h.desc && <p>{h.desc}</p>}
                </div>
              )) : <div className="raw-text">{hotelsText}</div>}
            </div>
          </div>
        )}

        {/* FOOD */}
        {activeTab === "food" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">🍛 Must-Try Food</h3>
              <span className="section-meta">local flavours of {result.destination}</span>
            </div>
            <div className="cards-grid">
              {foods.length > 0 ? foods.map((f, i) => (
                <div className="info-card food-card" key={i}>
                  <div className="card-icon">🍛</div>
                  <h4>{f.name}</h4>
                  {f.desc && <p>{f.desc}</p>}
                </div>
              )) : <div className="raw-text">{foodText}</div>}
            </div>
          </div>
        )}

        {/* PLACES */}
        {activeTab === "places" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">📸 Places to Visit</h3>
              <span className="section-meta">top picks for {result.trip_type}</span>
            </div>
            <div className="cards-grid">
              {places.length > 0 ? places.map((p, i) => (
                <div className="info-card place-card" key={i}>
                  <div className="card-icon">📸</div>
                  <h4>{p.name}</h4>
                  {p.desc && <p>{p.desc}</p>}
                </div>
              )) : <div className="raw-text">{placesText}</div>}
            </div>
          </div>
        )}

        {/* BUDGET */}
        {activeTab === "budget" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">💰 Budget Breakdown</h3>
              <span className="section-meta">{result.members} people · {result.days} days</span>
            </div>
            <div className="budget-list">
              {budgetLines.length > 0 ? budgetLines.map((item, i) => (
                <div className={`budget-row ${item.name.toLowerCase().includes("total") ? "budget-total" : ""}`} key={i}>
                  <span className="budget-label">{item.name}</span>
                  <span className="budget-value">{item.desc}</span>
                </div>
              )) : <div className="raw-text">{budgetText}</div>}
            </div>
          </div>
        )}

        {/* PACKING — interactive checkboxes */}
        {activeTab === "packing" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">🎒 Packing List</h3>
              <span className="section-meta">tap items to mark packed ✓</span>
            </div>
            {packingCats.length > 0 ? (
              <div className="packing-grid">
                {packingCats.map((cat, ci) => (
                  <div className="packing-card" key={ci}>
                    <h4 className="packing-cat-title">{cat.name}</h4>
                    <ul className="packing-items">
                      {cat.items.map((item, ii) => {
                        const key = `${ci}-${ii}`;
                        const checked = !!checkedItems[key];
                        return (
                          <li
                            key={ii}
                            className={`pack-item ${checked ? "packed" : ""}`}
                            onClick={() => toggleCheck(key)}
                          >
                            <span className="pack-check">{checked ? "✅" : "☐"}</span>
                            <span className="pack-text">{item}</span>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ))}
              </div>
            ) : <div className="raw-text">{packingText}</div>}
          </div>
        )}

        {/* EMERGENCY */}
        {activeTab === "emergency" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">🆘 Emergency Contacts</h3>
              <span className="section-meta">{result.destination}</span>
            </div>
            <div className="emergency-list">
              {emergencyItems.length > 0 ? emergencyItems.map((item, i) => (
                <div className="emergency-row" key={i}>
                  <span className="emergency-label">{item.name}</span>
                  <span className="emergency-value">{item.desc}</span>
                </div>
              )) : <div className="raw-text">{emergencyText}</div>}
            </div>
            <div className="emergency-note">
              ⚠️ Save these numbers offline before you travel. Keep a printed copy in your bag.
            </div>
          </div>
        )}

        {/* TIPS */}
        {activeTab === "tips" && (
          <div className="section-content">
            <div className="section-header-row">
              <h3 className="section-title">💡 Travel Tips</h3>
              <span className="section-meta">{result.source_city} → {result.destination}</span>
            </div>
            <ul className="tips-list">
              {tips.map((tip, i) => (
                <li key={i}>{tip.replace(/^[-*•]\s*/, "")}</li>
              ))}
            </ul>
          </div>
        )}

      </div>

      {/* ── PRINT-ONLY full view ── */}
      <div className="print-only">
        {[
          ["📅 Day-wise Itinerary", itineraryText],
          ["🏆 Trip Score", scoreText],
          ["🏨 Hotels", hotelsText],
          ["🍛 Food", foodText],
          ["📸 Places", placesText],
          ["💰 Budget", budgetText],
          ["🎒 Packing List", packingText],
          ["🆘 Emergency Contacts", emergencyText],
          ["💡 Travel Tips", tipsText],
        ].map(([title, content]) => (
          <div className="print-section" key={title}>
            <h2>{title}</h2>
            <div className="raw-text">{content}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ResultCard;
