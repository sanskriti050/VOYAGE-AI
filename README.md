# 🌍 VoyageAI — AI-Powered Travel Planner

VoyageAI is a full-stack AI travel planner that generates complete personalised trip plans using Google Gemini AI. Enter your source city, destination, budget, and trip type — get a full day-wise itinerary, hotel picks, food guide, budget breakdown, packing list, and emergency contacts instantly.

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
- 🔍 **Semantic Destination Search** — Natural language search ("romantic beach honeymoon", "budget friends adventure") using BM25-style embeddings
- 📊 **Budget Optimizer** — Smart budget allocation by category (travel/hotels/food/transport/activities) with health score, per-person breakdown, and saving tips
- 🗺️ **Route Optimizer** — Multi-city route planner using nearest-neighbor + 2-opt algorithm to minimize travel distance
- ✨ **Personalized Recommendations** — Similar destination suggestions based on trip type, budget, and semantic similarity
- 🧠 **RAG (Retrieval-Augmented Generation)** — In-memory knowledge base of 25+ destinations augments Gemini prompts for more accurate trip plans
- 💬 **AI Travel Assistant Chatbot** — Context-aware floating chatbot for real-time travel help ("Where should I eat?", "Find ATM", "It started raining")

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite 8 |
| Backend | FastAPI (Python) |
| AI | Google Gemini API (`gemini-2.5-flash-lite`) |
| Search | BM25-style TF-IDF cosine similarity (no external vector DB) |
| Route Optimization | Nearest-neighbor TSP + 2-opt improvement |
| Styling | Pure CSS |
| Deployment | Render (backend) + Vercel (frontend) |

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

Add your Gemini API key in `backend/.env`:
```
GEMINI_API_KEY=your_key_here
```
Get a free key at: https://aistudio.google.com/apikey

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
│   ├── main.py                   # FastAPI server — all endpoints + Gemini integration
│   ├── rag_knowledge.py          # RAG knowledge base with BM25 semantic search
│   ├── budget_optimizer.py       # Smart budget allocation engine
│   ├── route_optimizer.py        # Multi-city route optimizer (TSP + 2-opt)
│   ├── recommendation_engine.py  # Personalized destination recommendations
│   ├── requirements.txt
│   ├── render.yaml               # Render deployment config
│   ├── .env                      # Your API key (not committed)
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
| POST | `/generate-trip` | Generate full AI trip plan |
| POST | `/search-destinations` | Semantic destination search |
| POST | `/optimize-budget` | Smart budget allocation |
| POST | `/optimize-route` | Multi-city route optimization |
| POST | `/recommendations` | Personalized destination suggestions |
| POST | `/chat` | AI travel assistant chat |

---

## 🌐 Environment Variables

**Backend (`backend/.env`):**
```
GEMINI_API_KEY=your_gemini_api_key
```

**Frontend (for production deployment):**
```
VITE_API_URL=https://your-render-backend-url.onrender.com
```

---

## ⚠️ Important Notes

- Never commit your `.env` file — it contains your secret API key
- The `.gitignore` already excludes it
- Get a free Gemini API key at https://aistudio.google.com/apikey
- All new backend modules use Python standard library only — no extra pip installs needed

---

Built with ❤️ using React, FastAPI and Google Gemini AI
