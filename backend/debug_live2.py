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
    r = urllib.request.urlopen(req, timeout=90)
    return json.loads(r.read().decode())

print("Testing /generate-trip for Goa (India)...")
r = post("/generate-trip", {
    "source_city": "Delhi",
    "destination": "Goa",
    "days": 3,
    "members": 2,
    "travel_mode": "Flight",
    "trip_type": "Friends",
    "budget": 25000
})

print("currency_symbol (top level):", repr(r.get("currency_symbol")))
bo = r.get("budget_optimization", {})
print("budget_optimization.currency_symbol:", repr(bo.get("currency_symbol")))
print("budget_optimization.health:", bo.get("budget_health_label"))
print("allocation keys:", list(bo.get("allocation", {}).keys()))
print("recommendations count:", len(r.get("recommendations", [])))
print("rag_context_used:", r.get("rag_context_used"))
