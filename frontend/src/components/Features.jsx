function Features() {
  const features = [
    {
      icon: "🗓️",
      title: "Day-wise Itinerary",
      desc: "Get a detailed plan for each day — morning, afternoon, and evening activities tailored to your destination.",
    },
    {
      icon: "🏨",
      title: "Hotel Recommendations",
      desc: "Curated hotel suggestions that fit your budget, from budget stays to premium properties.",
    },
    {
      icon: "🍛",
      title: "Local Food Guide",
      desc: "Discover must-try local dishes and top restaurants at your travel destination.",
    },
    {
      icon: "📸",
      title: "Top Places to Visit",
      desc: "Never miss a highlight — AI finds the best spots, monuments, nature trails, and hidden gems.",
    },
    {
      icon: "💰",
      title: "Budget Breakdown",
      desc: "Smart cost estimation across hotels, food, transport, and activities so you never overspend.",
    },
    {
      icon: "💡",
      title: "Travel Tips",
      desc: "Expert tips on the best time to visit, local customs, what to pack, and how to get around.",
    },
  ];

  return (
    <section className="features-section">
      <h2 className="features-title">Everything You Need for the Perfect Trip</h2>
      <p className="features-subtitle">VoyageAI handles all the planning so you can focus on enjoying.</p>
      <div className="features-grid">
        {features.map((f, i) => (
          <div className="feature-card" key={i}>
            <div className="feature-icon">{f.icon}</div>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Features;
