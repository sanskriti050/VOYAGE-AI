"""
Budget Optimization Engine for VoyageAI
Analyzes trip parameters and returns smart budget allocation with optimization tips.
"""

from typing import Dict, List, Tuple


# ── Category weights by trip type ─────────────────────────────────
TRIP_TYPE_WEIGHTS = {
    "Solo": {
        "travel": 0.25,
        "hotels": 0.20,
        "food": 0.22,
        "local_transport": 0.10,
        "activities": 0.15,
        "miscellaneous": 0.08,
    },
    "Couple": {
        "travel": 0.22,
        "hotels": 0.28,
        "food": 0.22,
        "local_transport": 0.08,
        "activities": 0.14,
        "miscellaneous": 0.06,
    },
    "Family": {
        "travel": 0.28,
        "hotels": 0.25,
        "food": 0.20,
        "local_transport": 0.10,
        "activities": 0.12,
        "miscellaneous": 0.05,
    },
    "Friends": {
        "travel": 0.25,
        "hotels": 0.18,
        "food": 0.20,
        "local_transport": 0.10,
        "activities": 0.18,
        "miscellaneous": 0.09,
    },
    "Honeymoon": {
        "travel": 0.20,
        "hotels": 0.35,
        "food": 0.20,
        "local_transport": 0.07,
        "activities": 0.12,
        "miscellaneous": 0.06,
    },
}

# ── Per-day, per-person saving tips by mode ───────────────────────
SAVING_TIPS = {
    "hotels": [
        "Book hotels 2-3 months in advance for 20-40% discount",
        "Use booking apps like MakeMyTrip, Agoda, or Booking.com for flash deals",
        "Consider homestays or hostels — often 50% cheaper than hotels",
        "Opt for non-peak check-in days (Tue/Wed) for lower rates",
    ],
    "food": [
        "Eat at local dhabas/street stalls — authentic and 3x cheaper than restaurants",
        "Have a heavy lunch (cheaper) and light dinner",
        "Carry water bottles — refill instead of buying packaged water",
        "Avoid hotel restaurants — explore local food markets",
    ],
    "travel": [
        "Book flights 6-8 weeks in advance for best prices",
        "Use IndiGo/SpiceJet for domestic India or budget airlines internationally",
        "Travel on weekdays — 15-30% cheaper than weekends",
        "Use cashback credit cards for flight/hotel bookings",
    ],
    "local_transport": [
        "Use metro/local trains instead of taxis",
        "Rent a bike/scooter for short distances — cheaper and more fun",
        "Use Ola/Uber instead of auto-rickshaws for longer routes",
        "Negotiate taxi rates beforehand or use pre-paid taxi counters",
    ],
    "activities": [
        "Visit free monuments and parks instead of all paid attractions",
        "Buy combo attraction passes if available",
        "Book activities online — often 10-20% cheaper than on-site",
        "Do free walking tours instead of paid guided tours",
    ],
}

INTERNATIONAL_TIPS = [
    "Get a travel card (Niyo/HDFC Forex) to avoid currency exchange fees",
    "Buy travel insurance — saves costs on cancellations/medical emergencies",
    "Get a local SIM card at the airport for cheap data",
    "Use credit cards with zero forex markup for purchases abroad",
    "Download offline maps (Google Maps) before you land",
]


def optimize_budget(
    total_budget: float,
    days: int,
    members: int,
    trip_type: str,
    is_international: bool,
    currency_symbol: str,
) -> Dict:
    """
    Returns optimized budget allocation with per-person, per-day breakdown
    and smart saving suggestions.
    """
    weights = TRIP_TYPE_WEIGHTS.get(trip_type, TRIP_TYPE_WEIGHTS["Friends"])

    # Absolute allocations
    allocation = {k: round(total_budget * v, 2) for k, v in weights.items()}

    # Per person per day breakdown
    per_person_per_day = {}
    per_person_total = {}
    for cat, amt in allocation.items():
        ppd = round(amt / max(members, 1) / max(days, 1), 2)
        ppt = round(amt / max(members, 1), 2)
        per_person_per_day[cat] = ppd
        per_person_total[cat] = ppt

    # Budget health score (0-100)
    budget_per_person = total_budget / max(members, 1)
    budget_per_person_per_day = budget_per_person / max(days, 1)

    # Thresholds (in INR equivalent; rough guide)
    if is_international:
        # International — budget in foreign currency, rough thresholds
        if budget_per_person_per_day >= 100:
            health_score = 90
            health_label = "Excellent"
            health_color = "green"
        elif budget_per_person_per_day >= 60:
            health_score = 70
            health_label = "Good"
            health_color = "blue"
        elif budget_per_person_per_day >= 30:
            health_score = 45
            health_label = "Tight"
            health_color = "orange"
        else:
            health_score = 20
            health_label = "Very Tight"
            health_color = "red"
    else:
        if budget_per_person_per_day >= 3000:
            health_score = 90
            health_label = "Excellent"
            health_color = "green"
        elif budget_per_person_per_day >= 1500:
            health_score = 70
            health_label = "Good"
            health_color = "blue"
        elif budget_per_person_per_day >= 800:
            health_score = 45
            health_label = "Tight"
            health_color = "orange"
        else:
            health_score = 20
            health_label = "Very Tight"
            health_color = "red"

    # Pick relevant saving tips
    saving_suggestions = []
    for cat in ["hotels", "food", "travel", "local_transport", "activities"]:
        tips = SAVING_TIPS.get(cat, [])
        if tips:
            saving_suggestions.append({
                "category": cat.replace("_", " ").title(),
                "tip": tips[hash(trip_type + cat) % len(tips)],
            })

    if is_international:
        saving_suggestions.append({
            "category": "International Travel",
            "tip": INTERNATIONAL_TIPS[hash(trip_type) % len(INTERNATIONAL_TIPS)],
        })

    # Optimization score — how close are they to the ideal allocation
    optimization_tips = _get_optimization_tips(
        allocation, total_budget, days, members, trip_type, is_international
    )

    return {
        "total_budget": total_budget,
        "currency_symbol": currency_symbol,
        "members": members,
        "days": days,
        "allocation": allocation,
        "per_person_total": per_person_total,
        "per_person_per_day": per_person_per_day,
        "budget_health_score": health_score,
        "budget_health_label": health_label,
        "budget_health_color": health_color,
        "budget_per_person": round(budget_per_person, 2),
        "budget_per_person_per_day": round(budget_per_person_per_day, 2),
        "saving_suggestions": saving_suggestions,
        "optimization_tips": optimization_tips,
        "weights_used": weights,
    }


def _get_optimization_tips(
    allocation: Dict,
    total_budget: float,
    days: int,
    members: int,
    trip_type: str,
    is_international: bool,
) -> List[str]:
    tips = []
    budget_per_person = total_budget / max(members, 1)
    budget_ppd = budget_per_person / max(days, 1)

    if trip_type == "Friends" and allocation.get("hotels", 0) / total_budget > 0.25:
        tips.append("💡 Friends trips: Choose hostels or Airbnb to save on accommodation — redirect savings to activities")

    if trip_type == "Honeymoon" and allocation.get("hotels", 0) / total_budget < 0.30:
        tips.append("💡 Honeymoon trips: Consider splurging on accommodation — a special stay creates lasting memories")

    if days >= 7:
        tips.append("💡 Longer trip (7+ days): Cook some meals in a kitchen-equipped stay to significantly reduce food costs")

    if members >= 4:
        tips.append(f"💡 Group of {members}: Hire a private cab — often cheaper than {members} individual Uber/Ola rides")

    if is_international:
        tips.append("💡 International trip: Convert money in India before leaving — airport exchange rates are 8-12% worse")

    if not tips:
        tips.append("💡 Your budget allocation looks well-balanced for this trip type!")

    return tips
