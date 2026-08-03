# 🌍 VoyageAI — AI-Powered Travel Planner

VoyageAI is a full-stack AI travel planner that generates complete personalised trip plans using Groq (LLaMA) and Google Gemini AI. Enter your source city, destination, budget, and trip type — get a full day-wise itinerary, hotel picks, food guide, budget breakdown, packing list, and emergency contacts instantly.

Live Demo: [voyage-ai-2.onrender.com](https://voyage-ai-2.onrender.com)

---

## ✨ Features

### 🗺️ Trip Planning
- 📅 **Day-wise Itinerary** — Morning, Afternoon, Evening plans for every day
- 🏆 **Trip Score Card** — AI rates your trip on Adventure, Romance, Food, Value & more
- 💰 **Budget Assessment** — Tells if budget is sufficient with min & comfortable estimates
- 💱 **Auto Currency Detection** — Detects destination currency, shows INR equivalent for international trips
- 🚗 **Smart Travel Mode** — Disables modes not available for your route (e.g. no flight for Delhi→Agra)
- 🏨 **Hotel Recommendations** — Tailored to trip type (Solo / Couple / Family / Friends / Honeymoon)
- 🍛 **Food Guide** — Must-try local dishes and restaurant picks
- 📸 **Places to Visit** — Top attractions with entry fees
- 🎒 **Interactive Packing List** — Tap to check off items
- 🆘 **Emergency Contacts** — Local police, ambulance, embassy
- 🖨️ **Print / Save as PDF** — Full plan printable
- 🕒 **Recent Trips** — Last 5 plans saved locally

### 🤖 AI-Powered Smart Features

- 🔍 **Semantic Destination Search** — Natural language search using TF-IDF vectorization with cosine similarity over a curated travel knowledge base. Understands mood, weather, and season queries like "rainy misty peaceful", "cold snowy romantic", "sunny beach party"

- 📊 **Budget Optimizer** — Smart budget allocation by category (travel / hotels / food / transport / activities) with health score (0–100), per-person breakdown, and saving tips — personalised by trip type

- 🗺️ **Route Optimizer** — Multi-city route planner using Nearest Neighbor + 2-opt local search to minimize total travel distance. Detects international routes and restricts impossible modes (no bike/train for Delhi→London)

- ✨ **Personalized Recommendations** — Similar destination suggestions scored on trip-type affinity, budget match, and semantic similarity

- 🧠 **Grounded AI Generation** — Trip plans are grounded using semantic retrieval over a curated travel knowledge base (TF-IDF vectorization + cosine similarity). Relevant destination facts — best season, budget level, key highlights — are injected into the AI prompt to reduce hallucination and improve accuracy

- 💬 **AI Travel Assistant Chatbot** — Context-aware floating chatbot powered by Groq (LLaMA 3.3 70B). Answers real-time questions: "Where should I eat?", "Find ATM", "It started raining", "Shift today's plan"

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite 8 |
| Backend | FastAPI (Python) |
| Primary AI | Groq API — LLaMA 3.3 70B (fast, generous free tier) |
| Fallback AI | Google Gemini API (`gemini-2.5-flash`) |
| Semantic Search | TF-IDF vectorization + cosine similarity (no external vector DB) |
| Route Optimization | Nearest Neighbor TSP + 2-opt local search (Haversine distances) |
| Styling | Pure CSS |
| Deployment | Render (backend) + GitHub Pages (frontend) |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/VoyageAI.git
cd VoyageAI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

Create `.env` file:
```bash
cp .env.example .env
```

Add your API keys in `backend/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

- Groq free key: https://console.groq.com/keys
- Gemini free key: https://aistudio.google.com/apikey

Start the backend:
```bash
python -m uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Open in browser
```
http://localhost:5173
```

---

## 📁 Project Structure

```
VoyageAI/
├── backend/
│   ├── main.py                   # FastAPI server — all endpoints + AI integration
│   ├── rag_knowledge.py          # Curated travel knowledge base with TF-IDF semantic search
│   ├── budget_optimizer.py       # Smart budget allocation engine
│   ├── route_optimizer.py        # Multi-city route optimizer (Nearest Neighbor + 2-opt)
│   ├── recommendation_engine.py  # Personalized destination recommendations
│   ├── requirements.txt
│   ├── render.yaml               # Render deployment config
│   ├── .env                      # Your API keys (not committed)
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TripPlanner.jsx       # Main form + smart travel mode logic
│   │   │   ├── ResultCard.jsx        # 12-tab results display
│   │   │   ├── SemanticSearch.jsx    # Natural language destination search
│   │   │   ├── BudgetOptimizer.jsx   # Budget allocation visualizer
│   │   │   ├── RouteOptimizer.jsx    # Multi-city route planner UI
│   │   │   ├── RecommendationEngine.jsx  # Similar destinations
│   │   │   ├── TravelChatbot.jsx     # Floating AI travel assistant
│   │   │   ├── Navbar.jsx
│   │   │   ├── Hero.jsx
│   │   │   ├── Features.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── TripPlanner.css       # All component styles
│   │   ├── services/
│   │   │   └── api.js               # All backend API calls
│   │   └── App.jsx
│   └── vite.config.js
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/generate-trip` | Generate full AI trip plan (Groq + Gemini fallback) |
| POST | `/search-destinations` | Semantic destination search (TF-IDF + cosine similarity) |
| POST | `/optimize-budget` | Smart budget allocation by trip type |
| POST | `/optimize-route` | Multi-city route optimization (Nearest Neighbor + 2-opt) |
| POST | `/recommendations` | Personalized destination suggestions |
| POST | `/chat` | AI travel assistant (Groq LLaMA 3.3 70B) |

---

## 🌐 Environment Variables

**Backend (`backend/.env`):**
```
GROQ_API_KEY=your_groq_api_key       # Primary AI — LLaMA 3.3 70B
GEMINI_API_KEY=your_gemini_api_key   # Fallback AI
```

**Frontend (for production deployment):**
```
VITE_API_URL=https://your-render-backend-url.onrender.com
```

---

<<<<<<< HEAD
=======


>>>>>>> fad0280841d52c35252afad4e88260a1cf319a2c
Built with ❤️ using React, FastAPI, Groq (LLaMA) and Google Gemini AI
