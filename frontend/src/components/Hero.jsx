function Hero() {
  const scrollToPlanner = () => {
    const el = document.getElementById("planner");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="hero-content">
      <div className="hero-badge">🤖 Powered by Google Gemini AI</div>
      <h1>
        Your AI-Powered
        <br />
        <span className="hero-highlight">Travel Planner</span>
      </h1>

      <p>
        Enter your destination, days, budget & group size — get a complete
        day-by-day itinerary, hotel picks, local food guide, and budget breakdown.
        All in seconds.
      </p>

      <button className="hero-btn" onClick={scrollToPlanner}>
        🚀 Plan My Trip Now
      </button>

      <div className="hero-stats">
        <div className="stat">
          <span className="stat-num">📍</span>
          <span>Any Destination</span>
        </div>
        <div className="stat">
          <span className="stat-num">📅</span>
          <span>Custom Days</span>
        </div>
        <div className="stat">
          <span className="stat-num">💰</span>
          <span>Budget-Friendly</span>
        </div>
        <div className="stat">
          <span className="stat-num">⚡</span>
          <span>Instant Results</span>
        </div>
      </div>
    </section>
  );
}

export default Hero;
