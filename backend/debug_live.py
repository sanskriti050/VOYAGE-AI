import urllib.request, json

BASE = "https://voyage-ai-2.onrender.com"

def post(endpoint, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{endpoint}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    r = urllib.request.urlopen(req, timeout=30)
    return json.loads(r.read().decode())

# Test 1: Check backend version
print("=== BACKEND VERSION ===")
r = urllib.request.urlopen(f"{BASE}/", timeout=10)
print(r.read().decode())

# Test 2: Budget optimize - India
print("\n=== BUDGET OPTIMIZE (India) ===")
r2 = post("/optimize-budget", {
    "total_budget": 25000,
    "days": 5,
    "members": 2,
    "trip_type": "Friends",
    "is_international": False,
    "currency_symbol": "Rs"
})
print("currency_symbol:", repr(r2.get("currency_symbol")))
print("health:", r2.get("budget_health_label"))

# Test 3: Route optimize
print("\n=== ROUTE OPTIMIZE ===")
r3 = post("/optimize-route", {
    "cities": ["Delhi", "Jaipur", "Agra"],
    "travel_mode": "Train",
    "start_city": "Delhi"
})
print("optimized_route:", r3.get("optimized_route"))
print("error:", r3.get("error"))
print("legs count:", len(r3.get("legs", [])))

# Test 4: Search
print("\n=== SEARCH ===")
r4 = post("/search-destinations", {"query": "beach honeymoon", "top_k": 3})
print("results:", [x["destination"] for x in r4.get("results", [])])

print("\n=== DONE ===")
