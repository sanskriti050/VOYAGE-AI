import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# Groq client (optional — used as primary AI if GROQ_API_KEY is set)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from rag_knowledge import get_knowledge_base
from budget_optimizer import optimize_budget
from route_optimizer import optimize_route
from recommendation_engine import generate_recommendations

load_dotenv()
api_key      = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

app = FastAPI(title="VoyageAI Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripRequest(BaseModel):
    source_city: str
    destination: str
    days: int
    members: int
    travel_mode: str
    budget: float
    trip_type: str = "Friends"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class BudgetOptimizeRequest(BaseModel):
    total_budget: float
    days: int
    members: int
    trip_type: str = "Friends"
    is_international: bool = False
    currency_symbol: str = "₹"


class RouteOptimizeRequest(BaseModel):
    cities: List[str]
    travel_mode: str = "Flight"
    start_city: str = ""


class RecommendRequest(BaseModel):
    destination: str
    trip_type: str = "Friends"
    days: int = 5
    members: int = 2
    budget: float = 20000
    is_international: bool = False
    exchange_rate: float = 1.0
    past_destinations: Optional[List[str]] = None


class ChatMessage(BaseModel):
    role: str          # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    # Optional trip context — if user already planned a trip
    trip_context: Optional[dict] = None


# ── Exchange rates to INR ─────────────────────────────────────────
EXCHANGE_RATES_TO_INR = {
    "USD": 83.5, "EUR": 90.0, "GBP": 106.0, "JPY": 0.56,
    "AED": 22.7, "THB": 2.4,  "SGD": 62.0,  "MYR": 18.0,
    "AUD": 54.0, "CAD": 61.5, "CHF": 93.0,  "NZD": 50.0,
    "HKD": 10.7, "CNY": 11.5, "KRW": 0.063, "IDR": 0.0053,
    "PHP": 1.5,  "VND": 0.0034,"NPR": 0.625,"BDT": 0.76,
    "LKR": 0.28, "PKR": 0.30, "MXN": 4.8,  "BRL": 16.5,
    "ZAR": 4.5,  "EGP": 1.75, "TRY": 2.6,  "SAR": 22.3,
    "QAR": 22.9, "KWD": 272.0,"BHD": 221.0,"OMR": 217.0,
    "RUB": 0.95, "SEK": 8.0,  "NOK": 8.0,  "DKK": 12.1,
    "PLN": 21.0, "CZK": 3.7,  "HUF": 0.23, "ILS": 23.0,
    "JOD": 118.0,"MAD": 8.4,  "KES": 0.65, "TZS": 0.032,
    "INR": 1.0,
}

# ── Country → (currency_code, symbol) ────────────────────────────
COUNTRY_CURRENCY = {
    "usa": ("USD","$"), "united states": ("USD","$"), "new york": ("USD","$"),
    "los angeles": ("USD","$"), "chicago": ("USD","$"), "las vegas": ("USD","$"),
    "miami": ("USD","$"), "san francisco": ("USD","$"), "washington": ("USD","$"),
    "hawaii": ("USD","$"), "boston": ("USD","$"), "seattle": ("USD","$"),
    "france": ("EUR","€"), "paris": ("EUR","€"), "nice": ("EUR","€"),
    "lyon": ("EUR","€"), "marseille": ("EUR","€"), "bordeaux": ("EUR","€"),
    "germany": ("EUR","€"), "berlin": ("EUR","€"), "munich": ("EUR","€"),
    "frankfurt": ("EUR","€"), "hamburg": ("EUR","€"), "cologne": ("EUR","€"),
    "italy": ("EUR","€"), "rome": ("EUR","€"), "milan": ("EUR","€"),
    "venice": ("EUR","€"), "florence": ("EUR","€"), "naples": ("EUR","€"),
    "spain": ("EUR","€"), "madrid": ("EUR","€"), "barcelona": ("EUR","€"),
    "seville": ("EUR","€"), "ibiza": ("EUR","€"),
    "uk": ("GBP","£"), "london": ("GBP","£"), "edinburgh": ("GBP","£"),
    "manchester": ("GBP","£"), "england": ("GBP","£"), "britain": ("GBP","£"),
    "oxford": ("GBP","£"), "cambridge": ("GBP","£"),
    "japan": ("JPY","¥"), "tokyo": ("JPY","¥"), "osaka": ("JPY","¥"),
    "kyoto": ("JPY","¥"), "hiroshima": ("JPY","¥"), "nara": ("JPY","¥"),
    "dubai": ("AED","AED"), "abu dhabi": ("AED","AED"), "uae": ("AED","AED"),
    "sharjah": ("AED","AED"),
    "thailand": ("THB","฿"), "bangkok": ("THB","฿"), "phuket": ("THB","฿"),
    "chiang mai": ("THB","฿"), "pattaya": ("THB","฿"), "koh samui": ("THB","฿"),
    "singapore": ("SGD","S$"),
    "malaysia": ("MYR","RM"), "kuala lumpur": ("MYR","RM"), "penang": ("MYR","RM"),
    "langkawi": ("MYR","RM"), "kota kinabalu": ("MYR","RM"),
    "australia": ("AUD","A$"), "sydney": ("AUD","A$"), "melbourne": ("AUD","A$"),
    "brisbane": ("AUD","A$"), "perth": ("AUD","A$"), "cairns": ("AUD","A$"),
    "canada": ("CAD","CA$"), "toronto": ("CAD","CA$"), "vancouver": ("CAD","CA$"),
    "montreal": ("CAD","CA$"), "calgary": ("CAD","CA$"),
    "switzerland": ("CHF","CHF"), "zurich": ("CHF","CHF"), "geneva": ("CHF","CHF"),
    "interlaken": ("CHF","CHF"), "bern": ("CHF","CHF"),
    "new zealand": ("NZD","NZ$"), "auckland": ("NZD","NZ$"), "queenstown": ("NZD","NZ$"),
    "hong kong": ("HKD","HK$"),
    "china": ("CNY","¥"), "beijing": ("CNY","¥"), "shanghai": ("CNY","¥"),
    "guangzhou": ("CNY","¥"), "shenzhen": ("CNY","¥"),
    "south korea": ("KRW","₩"), "seoul": ("KRW","₩"), "busan": ("KRW","₩"),
    "indonesia": ("IDR","Rp"), "bali": ("IDR","Rp"), "jakarta": ("IDR","Rp"),
    "yogyakarta": ("IDR","Rp"), "lombok": ("IDR","Rp"),
    "philippines": ("PHP","₱"), "manila": ("PHP","₱"), "cebu": ("PHP","₱"),
    "boracay": ("PHP","₱"), "palawan": ("PHP","₱"),
    "vietnam": ("VND","₫"), "hanoi": ("VND","₫"), "ho chi minh": ("VND","₫"),
    "da nang": ("VND","₫"), "hoi an": ("VND","₫"), "halong bay": ("VND","₫"),
    "nepal": ("NPR","Rs"), "kathmandu": ("NPR","Rs"), "pokhara": ("NPR","Rs"),
    "bangladesh": ("BDT","৳"), "dhaka": ("BDT","৳"),
    "sri lanka": ("LKR","Rs"), "colombo": ("LKR","Rs"), "kandy": ("LKR","Rs"),
    "ella": ("LKR","Rs"), "sigiriya": ("LKR","Rs"),
    "maldives": ("USD","$"),
    "bhutan": ("INR","₹"), "thimphu": ("INR","₹"), "paro": ("INR","₹"),
    "pakistan": ("PKR","Rs"), "lahore": ("PKR","Rs"), "karachi": ("PKR","Rs"),
    "mexico": ("MXN","MX$"), "cancun": ("MXN","MX$"), "mexico city": ("MXN","MX$"),
    "playa del carmen": ("MXN","MX$"),
    "brazil": ("BRL","R$"), "rio de janeiro": ("BRL","R$"), "sao paulo": ("BRL","R$"),
    "south africa": ("ZAR","R"), "cape town": ("ZAR","R"), "johannesburg": ("ZAR","R"),
    "egypt": ("EGP","E£"), "cairo": ("EGP","E£"), "luxor": ("EGP","E£"),
    "turkey": ("TRY","₺"), "istanbul": ("TRY","₺"), "ankara": ("TRY","₺"),
    "cappadocia": ("TRY","₺"), "antalya": ("TRY","₺"),
    "saudi arabia": ("SAR","SAR"), "riyadh": ("SAR","SAR"), "jeddah": ("SAR","SAR"),
    "qatar": ("QAR","QR"), "doha": ("QAR","QR"),
    "kuwait": ("KWD","KD"),
    "bahrain": ("BHD","BD"), "manama": ("BHD","BD"),
    "oman": ("OMR","OMR"), "muscat": ("OMR","OMR"),
    "russia": ("RUB","₽"), "moscow": ("RUB","₽"), "st. petersburg": ("RUB","₽"),
    "sweden": ("SEK","kr"), "stockholm": ("SEK","kr"),
    "norway": ("NOK","kr"), "oslo": ("NOK","kr"),
    "denmark": ("DKK","kr"), "copenhagen": ("DKK","kr"),
    "greece": ("EUR","€"), "athens": ("EUR","€"), "santorini": ("EUR","€"),
    "mykonos": ("EUR","€"),
    "portugal": ("EUR","€"), "lisbon": ("EUR","€"), "porto": ("EUR","€"),
    "netherlands": ("EUR","€"), "amsterdam": ("EUR","€"),
    "belgium": ("EUR","€"), "brussels": ("EUR","€"),
    "austria": ("EUR","€"), "vienna": ("EUR","€"),
    "israel": ("ILS","₪"), "tel aviv": ("ILS","₪"), "jerusalem": ("ILS","₪"),
    "jordan": ("JOD","JD"), "amman": ("JOD","JD"), "petra": ("JOD","JD"),
    "morocco": ("MAD","MAD"), "marrakech": ("MAD","MAD"), "casablanca": ("MAD","MAD"),
    "kenya": ("KES","KSh"), "nairobi": ("KES","KSh"),
    "tanzania": ("TZS","TSh"), "zanzibar": ("TZS","TSh"),
    "cambodia": ("USD","$"), "siem reap": ("USD","$"), "phnom penh": ("USD","$"),
    "myanmar": ("USD","$"), "yangon": ("USD","$"),
    "laos": ("USD","$"), "vientiane": ("USD","$"),
    "czech republic": ("CZK","Kč"), "prague": ("CZK","Kč"),
    "hungary": ("HUF","Ft"), "budapest": ("HUF","Ft"),
    "poland": ("PLN","zł"), "warsaw": ("PLN","zł"), "krakow": ("PLN","zł"),
    "croatia": ("EUR","€"), "dubrovnik": ("EUR","€"),
    "peru": ("USD","$"), "machu picchu": ("USD","$"), "lima": ("USD","$"),
    "colombia": ("USD","$"), "bogota": ("USD","$"), "medellin": ("USD","$"),
}

INDIA_KW = [
    "india","goa","manali","kashmir","rajasthan","mumbai","bombay","delhi","bangalore",
    "bengaluru","chennai","madras","kolkata","calcutta","kerala","himachal","uttarakhand","jaipur",
    "agra","varanasi","ladakh","sikkim","meghalaya","assam","ooty","coorg",
    "munnar","shimla","mussoorie","rishikesh","haridwar","amritsar","pune",
    "hyderabad","ahmedabad","leh","spiti","andaman","lakshadweep","darjeeling",
    "gangtok","kochi","trivandrum","mysore","udaipur","jodhpur","pushkar",
    "hampi","alleppey","kodaikanal","mount abu","nainital","jim corbett","rann",
    "kutch","diu","daman","pondicherry","coimbatore","madurai","vizag",
    "visakhapatnam","bhubaneswar","puri","patna","lucknow","kanpur","nagpur",
    "surat","indore","bhopal","raipur","ranchi","guwahati","imphal","aizawl",
    "kohima","itanagar","shillong","agartala","panaji","dehradun","chandigarh",
    "jammu","srinagar","prayagraj","allahabad","vrindavan","mathura","dwarka",
    "somnath","tirupati","shirdi","bodh gaya","ajmer","ranthambore","kaziranga",
    "lonavala","mahabaleshwar","aurangabad","wayanad","varkala","kovalam",
    "rameshwaram","kanyakumari","mahabalipuram","thanjavur","mysuru","rameswaram",
    "matheran","alibaug","ellora","ajanta","kodaikanal","mount abu",
]


def detect_currency(destination: str):
    d = destination.lower().strip()
    # Check India first
    if any(k in d for k in INDIA_KW):
        return "INR", "₹", 1.0, "INR"
    # Check known international destinations
    for key, (code, sym) in COUNTRY_CURRENCY.items():
        if key in d:
            rate = EXCHANGE_RATES_TO_INR.get(code, 83.5)
            return code, sym, rate, code
    # Default to USD for unknown international
    return "USD", "$", 83.5, "USD"


def trip_type_context(trip_type: str) -> str:
    ctx = {
        "Solo":      "SOLO trip — safe areas, solo-friendly hostels/cafes, social activities, solo traveller spots, safety tips for alone travel.",
        "Couple":    "COUPLE trip — romantic restaurants, scenic viewpoints, couple-friendly hotels, sunset spots, intimate experiences.",
        "Family":    "FAMILY trip — family-friendly activities, kid-safe food, hotels with family rooms, age-friendly sightseeing, avoid extreme adventure.",
        "Friends":   "FRIENDS GROUP trip — group activities, nightlife/cafes, budget hostels/dormitories, adventure sports, group-friendly restaurants.",
        "Honeymoon": "HONEYMOON trip — romantic luxury hotels, candlelight dinners, private beach/mountain experiences, couple spa packages.",
    }
    return ctx.get(trip_type, ctx["Friends"])


def call_ai(prompt: str) -> str:
    """
    Call AI with Groq as primary (fast, generous free tier),
    Gemini as fallback.
    Returns generated text or raises HTTPException.
    """
    # ── Try Groq first ────────────────────────────────────────────
    if GROQ_AVAILABLE and groq_api_key:
        groq_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it",
        ]
        try:
            client = Groq(api_key=groq_api_key)
            for model in groq_models:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=4096,
                        temperature=0.7,
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    err = str(e)
                    if any(c in err for c in ["429", "503", "rate_limit", "quota"]):
                        continue
                    raise
        except Exception:
            pass  # Fall through to Gemini

    # ── Fallback: Gemini ──────────────────────────────────────────
    if not api_key:
        raise HTTPException(status_code=500, detail="No AI API key configured. Set GROQ_API_KEY or GEMINI_API_KEY.")

    gemini_models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash", "gemini-2.0-flash-lite"]
    client = genai.Client(api_key=api_key)
    last_error = None

    for model_name in gemini_models:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            if any(c in str(e) for c in ["429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "404"]):
                continue
            raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

    raise HTTPException(
        status_code=503,
        detail=f"All AI models quota exhausted. Please wait a few minutes or check your API keys. Last error: {last_error}"
    )


@app.get("/")
def home():
    return {"message": "VoyageAI AI Engine Running 🚀 v2.0 — RAG + Smart Features Active"}
@app.get("/test")
def test():
    return {"status": "working"}


# ── NEW: Semantic Destination Search ─────────────────────────────
@app.post("/search-destinations")
def search_destinations(req: SearchRequest):
    """
    Semantic search for destinations using embeddings (TF-IDF cosine similarity).
    Returns top matching destinations with similarity scores.
    """
    kb = get_knowledge_base()
    results = kb.semantic_search(req.query, top_k=req.top_k)
    return {
        "query": req.query,
        "results": results,
        "total": len(results),
    }


# ── NEW: Budget Optimization ──────────────────────────────────────
@app.post("/optimize-budget")
def optimize_budget_endpoint(req: BudgetOptimizeRequest):
    """
    Returns smart budget allocation with per-category breakdown,
    health score, and saving suggestions.
    """
    result = optimize_budget(
        total_budget=req.total_budget,
        days=req.days,
        members=req.members,
        trip_type=req.trip_type,
        is_international=req.is_international,
        currency_symbol=req.currency_symbol,
    )
    return result


# ── NEW: Route Optimization ───────────────────────────────────────
@app.post("/optimize-route")
def optimize_route_endpoint(req: RouteOptimizeRequest):
    """
    Optimizes visiting order for multi-city trip using nearest-neighbor heuristic.
    Returns optimized route with distance/cost/time estimates per leg.
    """
    result = optimize_route(
        cities=req.cities,
        travel_mode=req.travel_mode,
        start_city=req.start_city,
    )
    return result


# ── NEW: Personalized Recommendations ────────────────────────────
@app.post("/recommendations")
def get_recommendations(req: RecommendRequest):
    """
    Returns personalized destination recommendations based on
    trip type, budget, and similarity to current destination.
    """
    recs = generate_recommendations(
        destination=req.destination,
        trip_type=req.trip_type,
        days=req.days,
        members=req.members,
        budget=req.budget,
        is_international=req.is_international,
        exchange_rate=req.exchange_rate,
        past_destinations=req.past_destinations,
    )
    return recs



@app.post("/generate-trip")
def generate_trip(data: TripRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set in .env file")

    cur_code, sym, rate_to_inr, cur_name = detect_currency(data.destination)
    type_context     = trip_type_context(data.trip_type)
    is_international = (cur_code != "INR")

    # ── RAG: retrieve destination context to augment prompt ──────
    kb = get_knowledge_base()
    rag_context = kb.get_destination_context(data.destination)

    # Build INR conversion examples for the prompt
    example_amt   = int(data.budget)
    example_inr   = int(example_amt * rate_to_inr)
    rate_line     = f"1 {sym} = ₹{rate_to_inr}" if is_international else ""
    inr_rule      = (
        f"\nCURRENCY RULE: This is an INTERNATIONAL trip. "
        f"Exchange rate today: 1 {sym} = ₹{rate_to_inr}. "
        f"In the BUDGET ASSESSMENT section you MUST show every amount BOTH in {cur_name} AND in INR brackets. "
        f"Example format: {sym}2,000 (≈ ₹{int(2000*rate_to_inr):,}). "
        f"Also add a line: **Exchange Rate:** 1 {sym} = ₹{rate_to_inr}"
    ) if is_international else ""

    prompt = f"""
You are an expert AI Travel Planner with deep global knowledge.
{f"ADDITIONAL CONTEXT (from knowledge base): {rag_context}" if rag_context else ""}

Trip Details:
- Travelling From : {data.source_city}
- Destination     : {data.destination}
- Duration        : {data.days} days
- Group Size      : {data.members} people
- Trip Type       : {data.trip_type}
- Mode of Travel  : {data.travel_mode}
- Total Budget    : {sym}{int(data.budget)} {cur_name} (≈ ₹{example_inr:,} INR) for all {data.members} people
{inr_rule}

TRIP TYPE: {type_context}

RULES:
1. Use {cur_name} ({sym}) for ALL prices
2. All hotel/food/place names must be REAL, existing places in {data.destination}
3. Prices must be realistic for {data.destination}
4. Include return travel cost from {data.source_city} ↔ {data.destination}
5. Tailor all recommendations to a {data.trip_type} trip

Use EXACTLY these section headers (no changes):

## BUDGET ASSESSMENT

- **Status:** [SUFFICIENT / LOW / VERY LOW]
- **Minimum Recommended Budget:** {sym}[amount]{" (≈ ₹[calculate: amount × " + str(rate_to_inr) + "])" if is_international else ""}
- **Comfortable Budget:** {sym}[amount]{" (≈ ₹[calculate: amount × " + str(rate_to_inr) + "])" if is_international else ""}
{"- **Exchange Rate:** 1 " + sym + " = ₹" + str(rate_to_inr) if is_international else ""}
- **Assessment:** [2-3 sentences on budget sufficiency{", mention INR equivalents" if is_international else ""}]

## TRIP SCORE

- **Adventure:** [score]/10 — [reason]
- **Romance:** [score]/10 — [reason]
- **Food & Culture:** [score]/10 — [reason]
- **Value for Money:** [score]/10 — [reason]
- **Family Friendliness:** [score]/10 — [reason]
- **Overall:** [score]/10 — [summary]

## DAY-WISE ITINERARY

### Day 1: [Title]
**Morning:** [activities]
**Afternoon:** [activities]
**Evening:** [activities + dinner restaurant name]

(repeat ### Day X for all {data.days} days)

## BEST HOTELS

- **[Hotel Name]** - {sym}[price/night] - [why good for {data.trip_type}]
(4-5 hotels)

## FOOD GUIDE

IMPORTANT: Give real, currently known recommendations located in or very close to {data.destination}. Do not repeat the same venue or dish across categories. Include exactly 4-5 bullet points in EACH category. Every bullet must use this exact format: - **[Name]** - [what it is, area/locality, and why it is recommended]. If a destination has little or no club scene, recommend the best legitimate lounge, live-music venue, or nightlife bar instead and clearly say so.

### CAFES
- **[Real Cafe Name]** - [specialty, locality, why visit]
(4-5 real cafes)

### FAMILY RESTAURANTS
- **[Real Restaurant Name]** - [cuisine, locality, why it suits families]
(4-5 real family-friendly restaurants)

### CLUBS & NIGHTLIFE
- **[Real Club / Lounge Name]** - [music/vibe, locality, entry note if useful]
(4-5 real clubs, lounges, or nightlife venues)

### MUST-TRY FOODS
- **[Local Dish]** - [what it is and a real well-known place/area to try it]
(4-5 local foods)

## PLACES TO VISIT

- **[Place]** - [description, time needed] (Entry: {sym}[fee] or Free)
(6-8 places)

## BUDGET BREAKDOWN

- **Travel ({data.source_city} ↔ {data.destination}):** {sym}[amount] ({data.travel_mode})
- **Hotels:** {sym}[amount] ({data.days} nights)
- **Food:** {sym}[amount]
- **Local Transport:** {sym}[amount]
- **Activities & Entry Fees:** {sym}[amount]
- **Miscellaneous:** {sym}[amount]
- **Total Estimated:** {sym}[amount]{" (≈ ₹[INR total])" if is_international else ""}

## PACKING LIST

**Clothing & Gear:**
- [item]
**Documents & Money:**
- [item]
**Health & Safety:**
- [item]
**Electronics:**
- [item]

## EMERGENCY CONTACTS

- **Police / Emergency:** [number]
- **Ambulance:** [number]
- **Tourist Helpline:** [number or N/A]
- **Indian Embassy/Consulate:** [details if international, else N/A]
- **Nearest Hospital Area:** [name]
- **Recommended App:** [app for {data.destination}]

## TRAVEL TIPS

- [Best time to visit]
- [Local transport]
- [Cultural etiquette / safety for {data.trip_type}]
- [What to avoid]
- [Visa/documentation if international, else N/A]
"""

    # Call AI — Groq (primary) with Gemini fallback
    ai_text = call_ai(prompt)

    # ── Budget optimization ──────────────────────────────────────
    budget_opt = optimize_budget(
        total_budget=data.budget,
        days=data.days,
        members=data.members,
        trip_type=data.trip_type,
        is_international=is_international,
        currency_symbol=sym,
    )

    # ── Personalized recommendations ────────────────────────────
    recs = generate_recommendations(
        destination=data.destination,
        trip_type=data.trip_type,
        days=data.days,
        members=data.members,
        budget=data.budget,
        is_international=is_international,
        exchange_rate=rate_to_inr,
    )

    return {
        "source_city":      data.source_city,
        "destination":      data.destination,
        "days":             data.days,
        "members":          data.members,
        "travel_mode":      data.travel_mode,
        "trip_type":        data.trip_type,
        "budget":           int(data.budget),
        "currency_symbol":  sym,
        "currency_code":    cur_code,
        "exchange_rate":    rate_to_inr,
        "is_international": is_international,
        "ai_plan":          ai_text,
        "budget_optimization": budget_opt,
        "recommendations":  recs["recommendations"],
        "rag_context_used": bool(rag_context),
    }


# ── AI Travel Assistant Chat ──────────────────────────────────────
@app.post("/chat")
def travel_chat(req: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")

    trip_ctx = ""
    if req.trip_context:
        tc = req.trip_context
        trip_ctx = f"""
CURRENT TRIP CONTEXT:
- From: {tc.get('source_city','N/A')} → To: {tc.get('destination','N/A')}
- Duration: {tc.get('days','N/A')} days | Members: {tc.get('members','N/A')}
- Trip Type: {tc.get('trip_type','N/A')} | Mode: {tc.get('travel_mode','N/A')}
- Budget: {tc.get('currency_symbol','₹')}{tc.get('budget','N/A')}
"""

    system_prompt = f"""You are VoyageAI's friendly AI Travel Assistant. Help travellers with real-time questions.
{trip_ctx}
You help with: food spots, weather advice, nearby ATMs/pharmacies, itinerary changes, local transport, safety tips, budget advice, cultural tips.
Rules:
- Be conversational, warm, concise (under 150 words unless asked for detail)
- Give specific actionable answers using trip context when available
- For live data (exact ATM locations, live weather) suggest Google Maps / AccuWeather
- Use emojis sparingly
- Stay focused on travel assistance"""

    history_text = ""
    for msg in req.history[-8:]:
        role = "User" if msg.role == "user" else "Assistant"
        history_text += f"\n{role}: {msg.content}"

    full_prompt = f"{system_prompt}\n\nConversation:{history_text}\n\nUser: {req.message}\n\nAssistant:"

    # Call AI — Groq primary, Gemini fallback
    ai_reply = call_ai(full_prompt)
    return {"reply": ai_reply.strip()}
