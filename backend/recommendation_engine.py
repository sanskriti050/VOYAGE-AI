"""
Personalized Recommendation Engine for VoyageAI
Scores and ranks destinations based on trip type, budget, semantic similarity.
"""

from typing import List, Dict, Optional
from rag_knowledge import get_knowledge_base, DESTINATION_DOCS


# ── Trip-type affinity tags ───────────────────────────────────────
TRIP_TYPE_AFFINITY = {
    "Solo":      ["adventure", "off-beat", "budget", "backpacker", "trekking", "spiritual", "peaceful", "solo"],
    "Couple":    ["romantic", "scenic", "culture", "food", "beach", "nature", "peaceful", "honeymoon"],
    "Family":    ["family", "safe", "nature", "wildlife", "heritage", "beach", "culture", "clean", "kids"],
    "Friends":   ["nightlife", "adventure", "beach", "budget", "party", "water sports", "trekking", "backpacker", "affordable"],
    "Honeymoon": ["romantic", "luxury", "overwater bungalow", "exclusive", "scenic", "beach", "peaceful", "honeymoon", "couple"],
}

# ── Trip type emoji map ───────────────────────────────────────────
TRIP_TYPE_EMOJIS = {
    "Solo": "🧍", "Couple": "👫", "Family": "👨‍👩‍👧",
    "Friends": "👯", "Honeymoon": "💍",
}

# ── Budget per day per person (INR) thresholds ───────────────────
BUDGET_RANGES = {
    "budget":                 (0,     1500),
    "budget to mid-range":    (800,   3000),
    "mid-range":              (1500,  5000),
    "mid-range to expensive": (3000,  8000),
    "expensive":              (5000,  15000),
    "expensive to luxury":    (8000,  25000),
    "very expensive":         (10000, 999999),
    "budget to luxury":       (0,     999999),
    "luxury":                 (12000, 999999),
}


def _budget_ppd_inr(total: float, days: int, members: int, is_intl: bool, rate: float) -> float:
    inr = total * rate if is_intl else total
    return inr / max(members, 1) / max(days, 1)


def _budget_match(budget_level: str, ppd: float) -> tuple:
    """Returns (score 0-1, description string)."""
    key = budget_level.lower().strip()
    # Find best matching range key
    best_key = key
    for k in BUDGET_RANGES:
        if k == key:
            best_key = k
            break
        if k in key or key in k:
            best_key = k

    lo, hi = BUDGET_RANGES.get(best_key, (0, 999999))

    if ppd < lo:
        gap = (lo - ppd) / max(lo, 1)
        score = max(0.0, 1.0 - gap * 1.5)
        desc = f"budget might be tight ({budget_level})"
    elif ppd > hi * 2:
        score = 0.7  # way over budget for this — they can afford luxury
        desc = f"well within budget ({budget_level})"
    else:
        score = 1.0
        desc = f"fits your budget ({budget_level})"

    return round(score, 3), desc


def _tag_match(doc_tags: List[str], affinity: List[str]) -> tuple:
    """Returns (score 0-1, matched tags list)."""
    doc_set = set(t.lower() for t in doc_tags)
    aff_set = set(t.lower() for t in affinity)
    matched = list(doc_set & aff_set)
    score = len(matched) / max(len(aff_set), 1)
    return round(score, 3), matched


def _trip_type_match(doc: dict, trip_type: str) -> float:
    """Check if destination explicitly lists this trip type."""
    if trip_type in doc.get("trip_types", []):
        return 1.0
    return 0.0


def generate_recommendations(
    destination: str,
    trip_type: str,
    days: int,
    members: int,
    budget: float,
    is_international: bool,
    exchange_rate: float,
    past_destinations: Optional[List[str]] = None,
) -> Dict:
    """
    Generate personalised destination recommendations with clear reasoning.
    """
    kb = get_knowledge_base()
    affinity = TRIP_TYPE_AFFINITY.get(trip_type, TRIP_TYPE_AFFINITY["Friends"])
    ppd = _budget_ppd_inr(budget, days, members, is_international, exchange_rate)
    emoji = TRIP_TYPE_EMOJIS.get(trip_type, "✨")

    # Semantic similarity from RAG
    semantic_results = kb.semantic_search(
        f"{destination} {trip_type} {' '.join(affinity[:3])}", top_k=10
    )
    sem_score_map = {r["destination"]: r["similarity_score"] for r in semantic_results}

    scored = []
    for doc in DESTINATION_DOCS:
        dest_name = doc["destination"]

        # Skip exact match
        if dest_name.lower() == destination.lower():
            continue

        # Skip past visited
        if past_destinations:
            if any(dest_name.lower() == p.lower() for p in past_destinations):
                continue

        tag_score, matched_tags = _tag_match(doc["tags"], affinity)
        budget_score, budget_desc = _budget_match(doc["budget_level"], ppd)
        type_match = _trip_type_match(doc, trip_type)
        sem_score = sem_score_map.get(dest_name, 0.0)

        # Composite score — weighted
        composite = (
            tag_score   * 0.35 +
            budget_score * 0.25 +
            type_match  * 0.25 +
            sem_score   * 0.15
        )

        # Build clear, specific reasons
        reasons = []

        # Trip type reason
        if type_match == 1.0:
            reasons.append(f"{emoji} Perfect for {trip_type} trips")
        elif tag_score > 0.2:
            top_tags = matched_tags[:3]
            if top_tags:
                reasons.append(f"Great for {trip_type} — {', '.join(top_tags)}")

        # Budget reason
        reasons.append(budget_desc.capitalize())

        # Unique highlight from content
        highlight = _extract_highlight(doc["content"], trip_type)
        if highlight:
            reasons.append(highlight)

        scored.append({
            "destination": dest_name,
            "country": doc["country"],
            "score": round(composite, 4),
            "tag_score": tag_score,
            "budget_score": budget_score,
            "type_match": type_match,
            "semantic_score": round(sem_score, 3),
            "tags": doc["tags"][:6],
            "best_months": doc["best_months"],
            "budget_level": doc["budget_level"],
            "trip_types": doc.get("trip_types", []),
            "why": " · ".join(reasons),
            "snippet": doc["content"][:180] + "...",
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    return {
        "based_on": {
            "destination": destination,
            "trip_type": trip_type,
            "budget_per_person_per_day_inr": round(ppd),
        },
        "recommendations": scored[:5],
        "affinity_tags": affinity,
    }


def _extract_highlight(content: str, trip_type: str) -> str:
    """Pull a short relevant highlight from the destination content."""
    HIGHLIGHTS = {
        "Honeymoon": ["romantic", "honeymoon", "couple", "luxury", "overwater"],
        "Friends":   ["nightlife", "adventure", "party", "backpacker", "budget"],
        "Family":    ["family", "safe", "kid", "children", "theme park"],
        "Couple":    ["romantic", "scenic", "peaceful", "intimate"],
        "Solo":      ["solo", "adventure", "backpacker", "spiritual", "trekking"],
    }
    keywords = HIGHLIGHTS.get(trip_type, [])
    sentences = content.split(".")
    for sent in sentences:
        s = sent.strip()
        if any(kw in s.lower() for kw in keywords) and len(s) > 15:
            # Return a short version
            words = s.split()
            short = " ".join(words[:12])
            return short if len(short) > 10 else ""
    # Fallback — first interesting sentence
    for sent in sentences:
        s = sent.strip()
        if len(s) > 20:
            words = s.split()
            return " ".join(words[:10])
    return ""
