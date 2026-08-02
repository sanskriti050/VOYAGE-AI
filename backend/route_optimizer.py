"""
Route Optimization Engine for VoyageAI
Calculates optimal multi-city route using nearest-neighbor heuristic
and provides cost/time estimates.
"""

import math
from typing import List, Dict, Optional, Tuple

# ── City coordinates (lat, lon) ───────────────────────────────────
CITY_COORDS = {
    # India
    "delhi": (28.6139, 77.2090), "mumbai": (19.0760, 72.8777),
    "bombay": (19.0760, 72.8777),  # alias
    "bangalore": (12.9716, 77.5946), "bengaluru": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707), "madras": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639), "calcutta": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867), "pune": (18.5204, 73.8567),
    "jaipur": (26.9124, 75.7873), "ahmedabad": (23.0225, 72.5714),
    "goa": (15.2993, 74.1240), "panaji": (15.4989, 73.8278),
    "kochi": (9.9312, 76.2673), "trivandrum": (8.5241, 76.9366),
    "manali": (32.2396, 77.1887), "shimla": (31.1048, 77.1734),
    "dharamshala": (32.2190, 76.3234), "mussoorie": (30.4590, 78.0667),
    "rishikesh": (30.0869, 78.2676), "haridwar": (29.9457, 78.1642),
    "agra": (27.1767, 78.0081), "varanasi": (25.3176, 82.9739),
    "benares": (25.3176, 82.9739),  # alias for varanasi
    "lucknow": (26.8467, 80.9462), "chandigarh": (30.7333, 76.7794),
    "amritsar": (31.6340, 74.8723), "srinagar": (34.0837, 74.7973),
    "leh": (34.1526, 77.5771), "ladakh": (34.1526, 77.5771),
    "udaipur": (24.5854, 73.7125), "jodhpur": (26.2389, 73.0243),
    "jaisalmer": (26.9157, 70.9083), "ajmer": (26.4499, 74.6399),
    "pushkar": (26.4897, 74.5511), "bikaner": (28.0229, 73.3119),
    "darjeeling": (27.0410, 88.2663), "gangtok": (27.3389, 88.6065),
    "alleppey": (9.4981, 76.3388), "munnar": (10.0889, 77.0595),
    "ooty": (11.4102, 76.6950), "coorg": (12.4244, 75.7382),
    "mysore": (12.2958, 76.6394), "mysuru": (12.2958, 76.6394),
    "andaman": (11.7401, 92.6586), "port blair": (11.6234, 92.7265),
    "puri": (19.8135, 85.8312), "bhubaneswar": (20.2961, 85.8245),
    # International
    "bali": (-8.3405, 115.0920), "jakarta": (-6.2088, 106.8456),
    "bangkok": (13.7563, 100.5018), "phuket": (7.8804, 98.3923),
    "singapore": (1.3521, 103.8198), "kuala lumpur": (3.1390, 101.6869),
    "tokyo": (35.6762, 139.6503), "osaka": (34.6937, 135.5023),
    "kyoto": (35.0116, 135.7681), "seoul": (37.5665, 126.9780),
    "hong kong": (22.3193, 114.1694),
    "paris": (48.8566, 2.3522), "london": (51.5074, -0.1278),
    "rome": (41.9028, 12.4964), "barcelona": (41.3851, 2.1734),
    "amsterdam": (52.3676, 4.9041), "berlin": (52.5200, 13.4050),
    "vienna": (48.2082, 16.3738), "prague": (50.0755, 14.4378),
    "istanbul": (41.0082, 28.9784), "athens": (37.9838, 23.7275),
    "dubai": (25.2048, 55.2708), "abu dhabi": (24.4539, 54.3773),
    "new york": (40.7128, -74.0060), "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298), "miami": (25.7617, -80.1918),
    "sydney": (-33.8688, 151.2093), "melbourne": (-37.8136, 144.9631),
    "cairo": (30.0444, 31.2357), "nairobi": (-1.2921, 36.8219),
    "cape town": (-33.9249, 18.4241),
    "maldives": (3.2028, 73.2207), "colombo": (6.9271, 79.8612),
    "kathmandu": (27.7172, 85.3240), "dhaka": (23.8103, 90.4125),
    "switzerland": (46.8182, 8.2275), "zurich": (47.3769, 8.5417),
    "geneva": (46.2044, 6.1432), "interlaken": (46.6863, 7.8632),
}


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _get_coords(city: str) -> Optional[Tuple[float, float]]:
    key = city.lower().strip()
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    # Partial match
    for k, v in CITY_COORDS.items():
        if k in key or key in k:
            return v
    return None


def _travel_estimate(distance_km: float, mode: str) -> Dict:
    """Estimate travel time and cost for a leg."""
    mode_lower = mode.lower()
    if "flight" in mode_lower or "fly" in mode_lower:
        speed_kmh = 800
        base_cost_per_km = 5.0  # INR rough
    elif "train" in mode_lower:
        speed_kmh = 90
        base_cost_per_km = 0.5
    elif "car" in mode_lower or "drive" in mode_lower:
        speed_kmh = 65
        base_cost_per_km = 2.5
    elif "bus" in mode_lower:
        speed_kmh = 55
        base_cost_per_km = 0.3
    elif "bike" in mode_lower:
        speed_kmh = 50
        base_cost_per_km = 0.8
    else:
        speed_kmh = 65
        base_cost_per_km = 2.5

    hours = round(distance_km / speed_kmh, 1)
    # Minimum base for flight (airport time etc.)
    if "flight" in mode_lower and hours < 1.5:
        hours = 1.5
    cost_inr = round(distance_km * base_cost_per_km)

    if hours < 1:
        time_str = f"{int(hours * 60)} mins"
    elif hours < 24:
        time_str = f"{hours:.1f} hrs"
    else:
        time_str = f"{hours / 24:.1f} days"

    return {
        "distance_km": round(distance_km),
        "estimated_time": time_str,
        "estimated_cost_inr": cost_inr,
    }


def _route_total_distance(order: List[int], resolved: List[Dict]) -> float:
    """Calculate total distance for a given city order."""
    total = 0.0
    for i in range(len(order) - 1):
        total += _haversine(*resolved[order[i]]["coords"], *resolved[order[i+1]]["coords"])
    return total


def _two_opt(order: List[int], resolved: List[Dict]) -> List[int]:
    """2-opt improvement: try all edge swaps to reduce total distance."""
    best = order[:]
    best_dist = _route_total_distance(best, resolved)
    improved = True
    n = len(best)

    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # Reverse the segment between i and j
                new_order = best[:i] + best[i:j+1][::-1] + best[j+1:]
                new_dist = _route_total_distance(new_order, resolved)
                if new_dist < best_dist - 0.1:  # small epsilon to avoid floating issues
                    best = new_order
                    best_dist = new_dist
                    improved = True
    return best


# ── India city keys for international route detection ─────────────
INDIA_CITY_KEYS = {
    "delhi", "mumbai", "bombay", "bangalore", "bengaluru", "chennai", "madras", "kolkata", "calcutta",
    "hyderabad", "pune", "jaipur", "ahmedabad", "goa", "panaji",
    "kochi", "trivandrum", "manali", "shimla", "dharamshala", "mussoorie",
    "rishikesh", "haridwar", "agra", "varanasi", "lucknow", "chandigarh",
    "amritsar", "srinagar", "leh", "ladakh", "udaipur", "jodhpur",
    "jaisalmer", "ajmer", "pushkar", "bikaner", "darjeeling", "gangtok",
    "alleppey", "munnar", "ooty", "coorg", "mysore", "mysuru",
    "andaman", "port blair", "puri", "bhubaneswar",
}


def optimize_route(
    cities: List[str],
    travel_mode: str = "Flight",
    start_city: str = "",
) -> Dict:
    """
    Given a list of cities, compute the optimal visiting order
    using nearest-neighbor + 2-opt improvement to minimize total distance.

    Returns:
        - original_route: as provided
        - optimized_route: reordered for minimum travel
        - total_distance_km, legs, total_estimated_cost_inr
        - distance_saved_km, savings_percentage
        - is_international_route, available_modes, mode_warning
    """
    if not cities or len(cities) < 2:
        return {"error": "Need at least 2 cities for route optimization"}

    # Normalize and resolve coordinates
    resolved = []
    unresolved = []
    for city in cities:
        coords = _get_coords(city)
        if coords:
            resolved.append({"city": city, "coords": coords})
        else:
            unresolved.append(city)

    if len(resolved) < 2:
        return {
            "error": f"Could not find coordinates for: {', '.join(unresolved or cities)}",
            "unresolved": unresolved,
        }

    # ── Detect international route ────────────────────────────────
    india_cities = {r["city"] for r in resolved if r["city"].lower().strip() in INDIA_CITY_KEYS}
    intl_cities = {r["city"] for r in resolved if r["city"].lower().strip() not in INDIA_CITY_KEYS}

    if len(india_cities) > 0 and len(intl_cities) > 0:
        is_international_route = True
    elif len(intl_cities) > 1:
        is_international_route = True
    else:
        is_international_route = False

    # For international routes, force Flight for cost/time estimates
    effective_mode = "Flight" if is_international_route else travel_mode

    n = len(resolved)

    # Fix start city
    start_idx = 0
    if start_city:
        for i, r in enumerate(resolved):
            if r["city"].lower() == start_city.lower():
                start_idx = i
                break

    # Step 1: Nearest-neighbor greedy construction
    unvisited = list(range(n))
    unvisited.remove(start_idx)
    nn_order = [start_idx]

    while unvisited:
        current = nn_order[-1]
        lat1, lon1 = resolved[current]["coords"]
        nearest = min(
            unvisited,
            key=lambda j: _haversine(lat1, lon1, *resolved[j]["coords"]),
        )
        nn_order.append(nearest)
        unvisited.remove(nearest)

    # Step 2: 2-opt improvement (keep start fixed)
    if n <= 10:  # only for small routes; larger = too slow
        # Fix start position, optimize the rest
        rest = nn_order[1:]
        from itertools import permutations
        if len(rest) <= 6:
            # Brute force for very small routes
            best_order = nn_order[:]
            best_dist = _route_total_distance(nn_order, resolved)
            for perm in permutations(rest):
                candidate = [start_idx] + list(perm)
                dist = _route_total_distance(candidate, resolved)
                if dist < best_dist:
                    best_dist = dist
                    best_order = candidate
            final_order = best_order
        else:
            final_order = _two_opt(nn_order, resolved)
    else:
        final_order = nn_order

    optimized_cities = [resolved[i]["city"] for i in final_order]

    # Compute legs for optimized route
    legs = []
    total_distance = 0
    total_cost = 0
    for i in range(len(final_order) - 1):
        a = resolved[final_order[i]]
        b = resolved[final_order[i + 1]]
        dist = _haversine(*a["coords"], *b["coords"])
        est = _travel_estimate(dist, effective_mode)
        legs.append({
            "from": a["city"],
            "to": b["city"],
            **est,
        })
        total_distance += est["distance_km"]
        total_cost += est["estimated_cost_inr"]

    # Compute original route distance for comparison
    original_distance = 0
    for i in range(len(cities) - 1):
        c1 = _get_coords(cities[i])
        c2 = _get_coords(cities[i + 1])
        if c1 and c2:
            original_distance += round(_haversine(*c1, *c2))

    savings = max(0, original_distance - total_distance)
    savings_pct = round(savings / original_distance * 100) if original_distance > 0 else 0

    return {
        "original_route": cities,
        "optimized_route": optimized_cities,
        "total_distance_km": total_distance,
        "total_estimated_cost_inr": total_cost,
        "legs": legs,
        "original_distance_km": original_distance,
        "distance_saved_km": savings,
        "savings_percentage": savings_pct,
        "unresolved_cities": unresolved,
        "travel_mode": travel_mode,
        "is_international_route": is_international_route,
        "available_modes": ["Flight"] if is_international_route else ["Flight", "Train", "Car", "Bus", "Bike"],
        "mode_warning": (
            "Only flight is available for international routes"
            if is_international_route and travel_mode.lower() != "flight"
            else ""
        ),
    }
