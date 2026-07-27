function Hero() {
  const scrollToPlanner = () => document.getElementById("planner")?.scrollIntoView({ behavior: "smooth" });

  return (
    <section className="hero-content" id="home">
      <div className="hero-copy">
        <div className="hero-badge"><span className="badge-dot" /> AI travel concierge</div>
        <p className="hero-eyebrow">TRAVEL, THOUGHTFULLY PLANNED</p>
        <h1>Turn your next escape into a <span className="hero-highlight">beautifully planned journey.</span></h1>
        <p className="hero-description">A calm, intelligent place to shape every part of your trip—from where to stay to what to experience—around your time, taste and budget.</p>
        <div className="hero-actions">
          <button className="hero-btn" onClick={scrollToPlanner}>Start planning <span>→</span></button>
          <span className="hero-note">Personalised in moments</span>
        </div>
        <div className="hero-stats">
          <div className="stat"><strong>01</strong><span>Tell us where you want to go</span></div>
          <div className="stat"><strong>02</strong><span>Set your travel style & budget</span></div>
          <div className="stat"><strong>03</strong><span>Receive your day-by-day plan</span></div>
        </div>
      </div>
      <div className="hero-visual" aria-label="Mountain destination landscape">
        <img src="/travel-escape.svg" alt="Aesthetic travel postcard collage" />
        <div className="visual-shade" />
        <div className="trip-preview">
          <span className="preview-label">NEXT ESCAPE</span>
          <strong>Slow days in the Alps</strong>
          <p>6 days · nature & culture</p>
          <div className="preview-avatars"><i>J</i><i>M</i><span>+2 travellers</span></div>
        </div>
      </div>
    </section>
  );
}

export default Hero;
