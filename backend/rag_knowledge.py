"""
RAG Knowledge Base for VoyageAI
Destination data store with BM25-style weighted search.
No external vector DB needed — fully self-contained, high-quality matching.
"""

import math
import re
from typing import List, Dict, Tuple

# ── Destination Knowledge Base ────────────────────────────────────
DESTINATION_DOCS = [
    {
        "id": "goa",
        "destination": "Goa",
        "country": "India",
        "tags": ["beach", "nightlife", "water sports", "party", "seafood", "portuguese heritage", "budget", "friends", "backpacker"],
        "climate": "tropical",
        "best_months": "November to February",
        "budget_level": "budget to mid-range",
        "trip_types": ["Friends", "Couple", "Solo"],
        "content": "Goa is India's beach paradise known for its stunning coastline, vibrant nightlife, and Portuguese colonial architecture. Perfect for friends and couples. Famous for water sports, beach shacks, Baga Beach, Calangute, Anjuna flea market. Budget-friendly for Indian travellers. Best time November-February.",
    },
    {
        "id": "manali",
        "destination": "Manali",
        "country": "India",
        "tags": ["mountains", "snow", "adventure", "trekking", "honeymoon", "scenic", "himachal", "skiing", "paragliding", "bike trip"],
        "climate": "cold",
        "best_months": "October to June",
        "budget_level": "budget to mid-range",
        "trip_types": ["Friends", "Couple", "Honeymoon", "Solo"],
        "content": "Manali is a Himalayan resort town in Himachal Pradesh. Famous for snow, adventure sports like skiing and paragliding, Rohtang Pass, Solang Valley. Popular for honeymoons and friend groups. Bike trips to Leh via Manali are iconic.",
    },
    {
        "id": "kerala",
        "destination": "Kerala",
        "country": "India",
        "tags": ["backwaters", "houseboat", "nature", "ayurveda", "family", "couple", "spices", "culture", "peaceful", "scenic"],
        "climate": "tropical",
        "best_months": "September to March",
        "budget_level": "mid-range",
        "trip_types": ["Couple", "Family", "Honeymoon"],
        "content": "Kerala, God's Own Country, known for backwaters, houseboat stays in Alleppey, hill stations like Munnar, Ayurveda treatments, spice gardens, wildlife sanctuaries. Perfect for couples and families seeking peace and nature.",
    },
    {
        "id": "rajasthan",
        "destination": "Rajasthan",
        "country": "India",
        "tags": ["heritage", "palace", "desert", "culture", "history", "camel safari", "royal", "forts", "colorful", "traditional"],
        "climate": "desert",
        "best_months": "October to March",
        "budget_level": "budget to luxury",
        "trip_types": ["Family", "Couple", "Friends", "Solo"],
        "content": "Rajasthan is India's royal heritage state. Jaipur Pink City, Udaipur Lake City, Jodhpur Blue City, Jaisalmer desert. Magnificent forts, palaces, camel safaris, folk music, traditional bazaars. Suits all trip types.",
    },
    {
        "id": "kashmir",
        "destination": "Kashmir",
        "country": "India",
        "tags": ["paradise", "dal lake", "shikara", "snow", "mountains", "honeymoon", "scenic", "tulip gardens", "valleys", "peaceful"],
        "climate": "cold",
        "best_months": "April to October",
        "budget_level": "mid-range",
        "trip_types": ["Honeymoon", "Couple", "Family"],
        "content": "Kashmir is often called Paradise on Earth. Dal Lake, Shikara rides, Gulmarg skiing, Pahalgam meadows, Sonmarg glacier, tulip gardens. Famous for honeymoons and romantic getaways. Breathtaking mountain scenery.",
    },
    {
        "id": "bali",
        "destination": "Bali",
        "country": "Indonesia",
        "tags": ["beach", "temples", "culture", "rice terraces", "surfing", "nightlife", "spa", "romantic", "yoga", "tropical"],
        "climate": "tropical",
        "best_months": "April to October",
        "budget_level": "budget to mid-range",
        "trip_types": ["Couple", "Friends", "Honeymoon", "Solo"],
        "content": "Bali is Indonesia's island of gods. Ubud rice terraces, Tanah Lot temple, Seminyak beach clubs, Kuta surfing, Nusa Penida cliffs. Amazing food, spa treatments, yoga retreats, vibrant nightlife.",
    },
    {
        "id": "paris",
        "destination": "Paris",
        "country": "France",
        "tags": ["romantic", "eiffel tower", "art", "fashion", "museums", "couple", "honeymoon", "culture", "food", "luxury"],
        "climate": "temperate",
        "best_months": "April to June, September to October",
        "budget_level": "expensive",
        "trip_types": ["Couple", "Honeymoon", "Solo"],
        "content": "Paris, the City of Love. Eiffel Tower, Louvre Museum, Versailles Palace, Notre Dame Cathedral, Champs-Elysees. World-class French cuisine, fashion, wine, art. Most romantic city in the world.",
    },
    {
        "id": "tokyo",
        "destination": "Tokyo",
        "country": "Japan",
        "tags": ["tech", "culture", "food", "anime", "shopping", "temples", "cherry blossom", "modern", "family", "unique"],
        "climate": "temperate",
        "best_months": "March to May, September to November",
        "budget_level": "mid-range to expensive",
        "trip_types": ["Family", "Friends", "Solo", "Couple"],
        "content": "Tokyo blends ultra-modern and traditional Japan. Shibuya crossing, Senso-ji temple, Akihabara, Harajuku, ramen, sushi, cherry blossoms in spring. One of the world's safest and cleanest cities.",
    },
    {
        "id": "dubai",
        "destination": "Dubai",
        "country": "UAE",
        "tags": ["luxury", "shopping", "burj khalifa", "desert safari", "family", "modern", "gold souk", "skyscrapers", "nightlife"],
        "climate": "desert",
        "best_months": "November to April",
        "budget_level": "expensive to luxury",
        "trip_types": ["Family", "Friends", "Couple"],
        "content": "Dubai is the city of superlatives. Burj Khalifa tallest building, Dubai Mall world's largest, desert safari at sunset, Palm Jumeirah, gold and spice souks, world-class hotels and restaurants.",
    },
    {
        "id": "singapore",
        "destination": "Singapore",
        "country": "Singapore",
        "tags": ["clean", "modern", "family", "food", "gardens by the bay", "marina bay", "shopping", "multicultural", "safe"],
        "climate": "tropical",
        "best_months": "February to April",
        "budget_level": "mid-range to expensive",
        "trip_types": ["Family", "Couple", "Friends"],
        "content": "Singapore is a vibrant city-state. Marina Bay Sands, Gardens by the Bay, Sentosa Island, amazing hawker centre food, Universal Studios, Night Safari. Extremely safe and family-friendly.",
    },
    {
        "id": "bangkok",
        "destination": "Bangkok",
        "country": "Thailand",
        "tags": ["temples", "street food", "nightlife", "shopping", "floating market", "budget", "backpacker", "affordable", "party"],
        "climate": "tropical",
        "best_months": "November to February",
        "budget_level": "budget",
        "trip_types": ["Friends", "Solo", "Couple"],
        "content": "Bangkok is Thailand's vibrant capital. Grand Palace, Wat Pho, Chatuchak weekend market, Khao San Road backpacker street, floating markets, incredible street food. One of the cheapest major cities for travellers.",
    },
    {
        "id": "maldives",
        "destination": "Maldives",
        "country": "Maldives",
        "tags": ["luxury", "overwater bungalow", "honeymoon", "beach", "snorkeling", "diving", "romantic", "exclusive", "crystal water", "coral reef"],
        "climate": "tropical",
        "best_months": "November to April",
        "budget_level": "luxury",
        "trip_types": ["Honeymoon", "Couple"],
        "content": "Maldives is the ultimate luxury escape. Overwater bungalows, crystal-clear turquoise lagoons, vibrant coral reefs, dolphin watching, snorkeling, diving. The world's top honeymoon and romantic destination.",
    },
    {
        "id": "ladakh",
        "destination": "Ladakh",
        "country": "India",
        "tags": ["high altitude", "bike trip", "adventure", "monastery", "pangong lake", "mountains", "off-beat", "friends", "road trip", "rugged"],
        "climate": "cold desert",
        "best_months": "June to September",
        "budget_level": "budget to mid-range",
        "trip_types": ["Friends", "Solo", "Couple"],
        "content": "Ladakh is India's top adventure destination. Pangong Lake, Nubra Valley, Khardung La Pass (world's highest motorable road), Hemis Monastery. Famous for epic bike trips from Manali or Srinagar.",
    },
    {
        "id": "andaman",
        "destination": "Andaman",
        "country": "India",
        "tags": ["beach", "snorkeling", "diving", "island", "honeymoon", "nature", "pristine", "blue water", "isolated", "coral"],
        "climate": "tropical",
        "best_months": "October to May",
        "budget_level": "mid-range",
        "trip_types": ["Honeymoon", "Couple", "Family"],
        "content": "Andaman Islands offer India's most pristine beaches and crystal-clear waters. Radhanagar Beach (Asia's best beach), Cellular Jail, scuba diving, snorkeling at Havelock Island. Perfect for honeymoons.",
    },
    {
        "id": "london",
        "destination": "London",
        "country": "UK",
        "tags": ["history", "culture", "museums", "theatre", "buckingham palace", "shopping", "family", "couple", "iconic", "british"],
        "climate": "temperate",
        "best_months": "May to September",
        "budget_level": "expensive",
        "trip_types": ["Family", "Couple", "Solo", "Friends"],
        "content": "London is a global cultural capital. Big Ben, Tower of London, Buckingham Palace, British Museum (free), West End theatre, Notting Hill, Oxford Street, world-class food from every cuisine.",
    },
    {
        "id": "new_york",
        "destination": "New York",
        "country": "USA",
        "tags": ["iconic", "times square", "statue of liberty", "broadway", "shopping", "museums", "food", "urban", "diverse", "energy"],
        "climate": "temperate",
        "best_months": "April to June, September to November",
        "budget_level": "expensive",
        "trip_types": ["Friends", "Couple", "Solo", "Family"],
        "content": "New York City, the city that never sleeps. Times Square, Central Park, Statue of Liberty, Broadway shows, Met Museum, Brooklyn Bridge, world's most diverse food scene. Pure energy and excitement.",
    },
    {
        "id": "switzerland",
        "destination": "Switzerland",
        "country": "Switzerland",
        "tags": ["alps", "skiing", "scenic train", "chocolate", "watches", "honeymoon", "nature", "romantic", "luxury", "snow", "mountains"],
        "climate": "alpine",
        "best_months": "June to September, December to February",
        "budget_level": "very expensive",
        "trip_types": ["Honeymoon", "Couple", "Family"],
        "content": "Switzerland is Europe's most scenic country. Swiss Alps, Jungfrau peak, Glacier Express scenic train, Geneva lake, Zurich city, Interlaken adventure hub. Paradise for honeymoons and luxury travellers.",
    },
    {
        "id": "vietnam",
        "destination": "Vietnam",
        "country": "Vietnam",
        "tags": ["history", "street food", "halong bay", "culture", "beaches", "budget", "backpacker", "hoi an", "affordable", "scenic"],
        "climate": "tropical",
        "best_months": "February to April",
        "budget_level": "budget",
        "trip_types": ["Friends", "Solo", "Couple"],
        "content": "Vietnam is Southeast Asia's most diverse destination. Ha Long Bay cruise, Hoi An ancient town lanterns, Ho Chi Minh City energy, Hanoi old quarter, Pho and Banh Mi street food. Extremely budget-friendly.",
    },
    {
        "id": "istanbul",
        "destination": "Istanbul",
        "country": "Turkey",
        "tags": ["history", "bazaar", "culture", "hagia sophia", "bosphorus", "food", "europe asia crossroads", "romantic", "ancient"],
        "climate": "mediterranean",
        "best_months": "April to June, September to November",
        "budget_level": "budget to mid-range",
        "trip_types": ["Couple", "Friends", "Solo", "Family"],
        "content": "Istanbul bridges Europe and Asia. Hagia Sophia, Blue Mosque, Grand Bazaar, Bosphorus strait cruise, incredible Turkish cuisine, hammam bath experience. Rich Ottoman and Byzantine history.",
    },
    {
        "id": "ooty",
        "destination": "Ooty",
        "country": "India",
        "tags": ["hill station", "tea gardens", "family", "nature", "train", "honeymoon", "south india", "peaceful", "cool climate", "scenic"],
        "climate": "cool",
        "best_months": "April to June, September to November",
        "budget_level": "budget",
        "trip_types": ["Family", "Couple", "Honeymoon"],
        "content": "Ooty, the Queen of Hill Stations in Tamil Nadu. Nilgiri Mountain Railway toy train, sprawling tea gardens, Ooty Lake boating, Botanical Gardens. Perfect for family holidays and romantic getaways.",
    },
    {
        "id": "rishikesh",
        "destination": "Rishikesh",
        "country": "India",
        "tags": ["yoga", "adventure", "rafting", "spiritual", "ganges", "backpacker", "bungee jumping", "trekking", "budget", "peaceful"],
        "climate": "pleasant",
        "best_months": "September to June",
        "budget_level": "budget",
        "trip_types": ["Solo", "Friends", "Couple"],
        "content": "Rishikesh is India's adventure and spiritual capital. White water rafting on Ganga, bungee jumping, yoga ashrams, Laxman Jhula, Beatles Ashram. Gateway to Himalayan treks.",
    },
    {
        "id": "coorg",
        "destination": "Coorg",
        "country": "India",
        "tags": ["coffee", "nature", "peaceful", "trekking", "waterfalls", "family", "couple", "honeymoon", "hill station", "misty"],
        "climate": "cool",
        "best_months": "October to May",
        "budget_level": "budget to mid-range",
        "trip_types": ["Couple", "Family", "Honeymoon"],
        "content": "Coorg, the Scotland of India, is Karnataka's most scenic hill station. Coffee and spice plantations, Abbey Falls, Namdroling Monastery, Raja's Seat viewpoint. Perfect romantic weekend getaway.",
    },
    {
        "id": "shimla",
        "destination": "Shimla",
        "country": "India",
        "tags": ["hill station", "colonial", "snow", "mall road", "mountains", "family", "couple", "scenic", "toy train", "cool climate"],
        "climate": "cold",
        "best_months": "October to February for snow, March to June pleasant",
        "budget_level": "budget to mid-range",
        "trip_types": ["Family", "Couple", "Friends"],
        "content": "Shimla, the former summer capital of British India. Mall Road, Christ Church, Jakhu Temple, Kufri snow point. Famous toy train from Kalka. Snow in winter, pleasant in summer.",
    },
    {
        "id": "munnar",
        "destination": "Munnar",
        "country": "India",
        "tags": ["tea gardens", "misty", "nature", "trekking", "wildlife", "couple", "honeymoon", "peaceful", "hills", "green"],
        "climate": "cool",
        "best_months": "September to March",
        "budget_level": "budget to mid-range",
        "trip_types": ["Couple", "Honeymoon", "Family"],
        "content": "Munnar in Kerala is famous for vast emerald tea estates rolling over misty hills. Eravikulam National Park, Mattupetty Dam, Top Station viewpoint. One of South India's most romantic destinations.",
    },
    {
        "id": "phuket",
        "destination": "Phuket",
        "country": "Thailand",
        "tags": ["beach", "nightlife", "party", "island hopping", "diving", "affordable", "friends", "couple", "tropical", "water sports"],
        "climate": "tropical",
        "best_months": "November to April",
        "budget_level": "budget to mid-range",
        "trip_types": ["Friends", "Couple", "Solo"],
        "content": "Phuket is Thailand's largest island and top beach destination. Patong nightlife, Phi Phi Islands, Maya Bay, snorkeling, Bangla Road party scene. Budget-friendly with stunning tropical beauty.",
    },
    {
        "id": "rome",
        "destination": "Rome",
        "country": "Italy",
        "tags": ["history", "colosseum", "art", "food", "culture", "romantic", "ancient", "architecture", "couple", "family"],
        "climate": "mediterranean",
        "best_months": "April to June, September to October",
        "budget_level": "mid-range to expensive",
        "trip_types": ["Couple", "Family", "Solo", "Friends"],
        "content": "Rome, the Eternal City. Colosseum, Vatican City, Sistine Chapel, Roman Forum, Trevi Fountain, gelato and pasta. 2000 years of history around every corner. Incredibly romantic for couples.",
    },
]


# ── Improved BM25-style keyword matching ─────────────────────────

STOP_WORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for",
    "of", "is", "are", "was", "were", "with", "by", "from", "as",
    "its", "it", "be", "this", "that", "have", "has", "had",
}

# High-value travel intent keywords → boost multiplier
INTENT_KEYWORDS = {
    "honeymoon": 3.0, "romantic": 3.0, "romance": 3.0, "couple": 2.5,
    "adventure": 2.5, "trekking": 2.5, "trek": 2.5, "hiking": 2.5,
    "beach": 2.5, "beaches": 2.5, "island": 2.0,
    "luxury": 2.5, "budget": 2.0, "cheap": 2.0, "affordable": 2.0,
    "family": 2.5, "kids": 2.0, "children": 2.0,
    "friends": 2.0, "group": 1.8, "solo": 2.0,
    "snow": 2.5, "ski": 2.5, "skiing": 2.5, "mountains": 2.0, "mountain": 2.0,
    "nightlife": 2.5, "party": 2.5, "clubs": 2.0,
    "culture": 1.8, "history": 1.8, "heritage": 2.0, "temples": 2.0,
    "nature": 1.8, "wildlife": 2.0, "peaceful": 1.8,
    "food": 1.8, "street food": 2.0, "cuisine": 1.8,
    "diving": 2.5, "snorkeling": 2.5, "water sports": 2.5,
    "backpacker": 2.0, "spiritual": 2.0, "yoga": 2.0,
    "scenic": 1.8, "views": 1.8, "photography": 1.8,
}


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r'[a-z]+', text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def _doc_text(doc: dict) -> str:
    """Rich text representation of a document for matching."""
    tag_str = " ".join(doc["tags"])
    # Repeat tags 3x for stronger signal
    return (
        f"{doc['destination']} {doc['destination']} {doc['country']} "
        f"{tag_str} {tag_str} {tag_str} "
        f"{doc['content']} "
        f"{doc['climate']} {doc['budget_level']} "
        f"{' '.join(doc.get('trip_types', []))}"
    )


def _score_doc(query_tokens: List[str], doc: dict) -> float:
    """BM25-inspired scoring with intent keyword boosting."""
    doc_text = _doc_text(doc).lower()
    doc_tokens = _tokenize(doc_text)
    doc_token_set = set(doc_tokens)

    # Tag set for exact tag matching
    tag_set = set(t.lower() for t in doc["tags"])
    trip_type_set = set(t.lower() for t in doc.get("trip_types", []))
    dest_lower = doc["destination"].lower()

    score = 0.0

    for token in query_tokens:
        boost = INTENT_KEYWORDS.get(token, 1.0)

        # Destination name exact match — big bonus
        if token == dest_lower or token in dest_lower:
            score += 8.0 * boost
            continue

        # Exact tag match
        if token in tag_set:
            score += 4.0 * boost
            continue

        # Trip type match
        if token in trip_type_set:
            score += 3.0 * boost
            continue

        # Content/description match
        if token in doc_token_set:
            score += 1.5 * boost

    # Normalize by query length to avoid bias toward longer docs
    if len(query_tokens) > 0:
        score /= math.sqrt(len(query_tokens))

    return round(score, 4)


class RAGKnowledgeBase:
    """In-memory RAG knowledge base with BM25-style semantic scoring."""

    def __init__(self):
        self.docs = DESTINATION_DOCS

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Find top-k most semantically similar destinations.
        Returns list of results with similarity scores.
        """
        query_tokens = _tokenize(query)

        # Also add multi-word phrases detection
        query_lower = query.lower()
        multi_word_boosts = []
        for kw, boost in INTENT_KEYWORDS.items():
            if " " in kw and kw in query_lower:
                multi_word_boosts.append((kw, boost))

        scored = []
        for doc in self.docs:
            base_score = _score_doc(query_tokens, doc)

            # Apply multi-word phrase boosts
            doc_text = _doc_text(doc).lower()
            for kw, boost in multi_word_boosts:
                if kw in doc_text:
                    base_score += 2.0 * boost

            scored.append((base_score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Normalize scores to 0-1 range
        max_score = scored[0][0] if scored and scored[0][0] > 0 else 1.0
        results = []
        for raw_score, doc in scored[:top_k]:
            normalized = round(raw_score / max_score, 4) if max_score > 0 else 0.0
            results.append({
                "destination": doc["destination"],
                "country": doc["country"],
                "similarity_score": normalized,
                "raw_score": raw_score,
                "tags": doc["tags"],
                "best_months": doc["best_months"],
                "budget_level": doc["budget_level"],
                "trip_types": doc.get("trip_types", []),
                "content": doc["content"],
            })

        return results

    def get_destination_context(self, destination: str) -> str:
        """
        Retrieve relevant context for a destination to augment AI prompt (RAG).
        """
        results = self.semantic_search(destination, top_k=1)
        if results and results[0]["raw_score"] > 1.0:
            doc = results[0]
            return (
                f"[RAG Context] {doc['destination']}, {doc['country']}. "
                f"Best time to visit: {doc['best_months']}. "
                f"Budget level: {doc['budget_level']}. "
                f"Key highlights: {doc['content']}"
            )
        return ""

    def get_similar_destinations(self, destination: str, trip_type: str = "", budget_hint: str = "") -> List[Dict]:
        """Return similar destinations for recommendations."""
        query = f"{destination} {trip_type} {budget_hint}"
        results = self.semantic_search(query, top_k=8)
        return [r for r in results if r["destination"].lower() != destination.lower()][:6]


# Singleton instance
_kb = None

def get_knowledge_base() -> RAGKnowledgeBase:
    global _kb
    if _kb is None:
        _kb = RAGKnowledgeBase()
    return _kb
