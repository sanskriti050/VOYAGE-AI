function Features() {
  const features = [
    { icon: "01", title: "Day-wise itinerary", desc: "A considered plan for every morning, afternoon and evening." },
    { icon: "02", title: "Stay & dining picks", desc: "Thoughtful hotel and local food recommendations for your budget." },
    { icon: "03", title: "Places worth your time", desc: "Highlights, hidden gems and experiences shaped around your pace." },
    { icon: "04", title: "Clear budget view", desc: "A practical breakdown across stays, food, transport and activities." },
  ];

  return (
    <section className="features-section" id="features">
      <div className="section-intro">
        <p className="hero-eyebrow">YOUR TRIP, IN ONE PLACE</p>
        <h2 className="features-title">A travel dashboard that feels personal.</h2>
        <p className="features-subtitle">Every important detail is shaped into one clear, considered itinerary.</p>
      </div>
      <div className="features-grid">
        {features.map((feature) => <article className="feature-card" key={feature.icon}><div className="feature-icon">{feature.icon}</div><h3>{feature.title}</h3><p>{feature.desc}</p><span className="feature-arrow">Explore →</span></article>)}
      </div>
      <div className="inspiration-row">
        <div className="inspiration-copy"><p className="hero-eyebrow">CURATED INSPIRATION</p><h3>Find a place that feels like a story worth living.</h3><p>Choose a mood, set the pace, and let VoyageAI take care of the details.</p></div>
        <article className="destination-card destination-card-large beach-card"><div className="beach-art"><span /><span /><span /></div><div><span>COASTAL RESET</span><strong>Sun, salt & slow mornings</strong></div></article>
        <article className="destination-card city-card"><div className="city-art"><span /><span /><span /></div><div><span>CITY WANDER</span><strong>Beautiful corners, at your pace</strong></div></article>
      </div>
    </section>
  );
}

export default Features;
