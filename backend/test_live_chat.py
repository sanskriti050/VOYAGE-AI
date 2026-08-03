import urllib.request, json

BASE = "https://voyage-ai-2.onrender.com"

body = json.dumps({
    "message": "Where should I eat now?",
    "history": [],
    "trip_context": {"destination": "Mumbai", "source_city": "Delhi", "days": 3, "members": 2, "trip_type": "Friends", "travel_mode": "Flight", "budget": 25000, "currency_symbol": "Rs"}
}).encode()

req = urllib.request.Request(f"{BASE}/chat", data=body, headers={"Content-Type": "application/json"}, method="POST")
r = urllib.request.urlopen(req, timeout=30)
data = json.loads(r.read().decode())
print("REPLY:")
print(data.get("reply", "no reply"))
