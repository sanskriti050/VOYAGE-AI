# 🌍 VoyageAI — AI-Powered Travel Planner

VoyageAI is a full-stack AI travel planner that generates complete personalised trip plans using Google Gemini AI. Enter your source city, destination, budget, and trip type — get a full day-wise itinerary, hotel recommendations, food guide, budget breakdown, packing list, and emergency contacts instantly.

---

## ✨ Features

- 🗓️ **Day-wise Itinerary** — Morning, Afternoon, Evening plans for every day
- 🏆 **Trip Score Card** — AI rates your trip on Adventure, Romance, Food, Value & more
- 💰 **Budget Assessment** — Tells if your budget is sufficient, with min & comfortable estimates
- 💱 **Currency Conversion** — Auto-detects destination currency, shows INR equivalent for international trips
- 🚗 **Smart Travel Mode** — Disables modes not available for your route (e.g. no flight for Lucknow→Prayagraj)
- 🏨 **Hotel Recommendations** — Tailored to your trip type (Solo/Couple/Family/Friends/Honeymoon)
- 🍛 **Local Food Guide** — Authentic dishes and restaurants
- 🎒 **Interactive Packing List** — Tap to check off items
- 🆘 **Emergency Contacts** — Local police, ambulance, embassy
- 🖨️ **Print / Save as PDF** — Full trip plan printable
- 🕒 **Recent Trips** — Last 5 plans saved locally

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| AI | Google Gemini API (`google-genai`) |
| Styling | Pure CSS |

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
pip install fastapi uvicorn google-genai python-dotenv
```

Create your `.env` file:
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
python -m uvicorn main:app --reload
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
│   ├── main.py          # FastAPI server + Gemini integration
│   ├── .env             # Your API key (not committed)
│   └── .env.example     # Template for API key
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TripPlanner.jsx   # Main form with smart travel mode
│   │   │   ├── ResultCard.jsx    # Tabbed results display
│   │   │   ├── Navbar.jsx
│   │   │   ├── Hero.jsx
│   │   │   ├── Features.jsx
│   │   │   └── Footer.jsx
│   │   └── App.jsx
│   └── vite.config.js
└── README.md
```

---

## ⚠️ Important

- Never commit your `.env` file — it contains your secret API key
- The `.gitignore` already excludes it
- Get your own free Gemini API key at https://aistudio.google.com/apikey

---

Built with ❤️ using React, FastAPI and Google Gemini AI
