import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Features from "./components/Features";
import TripPlanner from "./components/TripPlanner";
import Footer from "./components/Footer";

function App() {
  return (
    <div className="app">
      <Navbar />
      <Hero />
      <Features />
      <TripPlanner />
      <Footer />
    </div>
  );
}

export default App;
