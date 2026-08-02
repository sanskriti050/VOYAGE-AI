import { useState } from "react";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Features from "./components/Features";
import TripPlanner from "./components/TripPlanner";
import Footer from "./components/Footer";
import TravelChatbot from "./components/TravelChatbot";

function App() {
  // tripContext is set when a trip plan is generated — passed to chatbot
  const [tripContext, setTripContext] = useState(null);

  return (
    <div className="app">
      <Navbar />
      <Hero />
      <Features />
      <TripPlanner onTripGenerated={setTripContext} />
      <Footer />
      {/* Floating AI chatbot — always visible, context-aware when trip is planned */}
      <TravelChatbot tripContext={tripContext} />
    </div>
  );
}

export default App;
