"""Script to rewrite rag_knowledge.py with weather/mood tags + improved scoring."""
content = '''"""
RAG Knowledge Base for VoyageAI — v3
Weather, mood, season-aware semantic search using BM25-style scoring.
"""
import math, re
from typing import List, Dict

DESTINATION_DOCS = [
  {"id":"goa","destination":"Goa","country":"India","tags":["beach","nightlife","water sports","party","seafood","budget","friends","sunny","hot","tropical","coastal","summer vibes","swimming","diving"],"weather":"sunny hot tropical coastal warm humid","mood":"party fun chill beach vibes","best_months":"November to February","budget_level":"budget to mid-range","trip_types":["Friends","Couple","Solo"],"content":"Goa is India beach paradise. Stunning coastline, vibrant nightlife, Portuguese heritage. Baga Beach, Calangute, Anjuna flea market, water sports. Best November-February."},
  {"id":"manali","destination":"Manali","country":"India","tags":["mountains","snow","adventure","trekking","honeymoon","scenic","skiing","paragliding","bike trip","cold","snowy","winter wonderland","misty","freezing"],"weather":"cold snowy misty winter mountains chilly freezing alpine snowfall","mood":"adventure thrill romantic scenic snowy","best_months":"October to June","budget_level":"budget to mid-range","trip_types":["Friends","Couple","Honeymoon","Solo"],"content":"Manali is a Himalayan resort in Himachal Pradesh. Snow, skiing, paragliding, Rohtang Pass, Solang Valley. Popular for honeymoons and bike trips to Leh."},
  {"id":"kerala","destination":"Kerala","country":"India","tags":["backwaters","houseboat","nature","ayurveda","family","couple","peaceful","rainy","lush green","monsoon","tropical green","misty","waterfalls"],"weather":"rainy monsoon lush green humid tropical warm peaceful drizzle waterfalls","mood":"peaceful relaxing romantic nature serene rainy retreat","best_months":"September to March","budget_level":"mid-range","trip_types":["Couple","Family","Honeymoon"],"content":"Kerala, Gods Own Country. Backwaters, houseboat stays in Alleppey, Munnar hill station, Ayurveda treatments, spice gardens, wildlife sanctuaries."},
  {"id":"rajasthan","destination":"Rajasthan","country":"India","tags":["heritage","palace","desert","culture","history","camel safari","royal","forts","colorful","hot dry","arid","sunny","golden","traditional"],"weather":"hot dry sunny arid desert warm golden clear skies","mood":"cultural historical royal majestic grand","best_months":"October to March","budget_level":"budget to luxury","trip_types":["Family","Couple","Friends","Solo"],"content":"Rajasthan is India royal heritage state. Jaipur Pink City, Udaipur Lake City, Jodhpur Blue City, Jaisalmer desert. Forts, palaces, camel safaris, folk music."},
  {"id":"kashmir","destination":"Kashmir","country":"India","tags":["paradise","dal lake","shikara","snow","mountains","honeymoon","scenic","valleys","peaceful","cold","snowy","misty","foggy","freezing","white","winter"],"weather":"cold snowy misty foggy winter mountains chilly alpine freezing white","mood":"romantic peaceful scenic paradise snowy magical","best_months":"April to October","budget_level":"mid-range","trip_types":["Honeymoon","Couple","Family"],"content":"Kashmir is Paradise on Earth. Dal Lake, Shikara rides, Gulmarg skiing, Pahalgam meadows, Sonmarg glacier, tulip gardens. Famous for honeymoons."},
  {"id":"coorg","destination":"Coorg","country":"India","tags":["coffee","nature","peaceful","trekking","waterfalls","honeymoon","hill station","misty","rainy","lush green","cool","foggy","drizzle","clouds"],"weather":"misty rainy foggy cool lush green refreshing drizzle clouds peaceful","mood":"peaceful romantic nature serene refreshing rainy retreat","best_months":"October to May","budget_level":"budget to mid-range","trip_types":["Couple","Family","Honeymoon"],"content":"Coorg, Scotland of India, Karnataka most scenic hill station. Coffee plantations, Abbey Falls, Namdroling Monastery. Perfect romantic weekend getaway."},
  {"id":"munnar","destination":"Munnar","country":"India","tags":["tea gardens","misty","nature","trekking","wildlife","honeymoon","peaceful","hills","green","cool","rainy","foggy","clouds","mist","serene"],"weather":"misty cool foggy rainy clouds tea gardens green refreshing drizzle","mood":"peaceful romantic serene nature misty magical","best_months":"September to March","budget_level":"budget to mid-range","trip_types":["Couple","Honeymoon","Family"],"content":"Munnar Kerala famous for emerald tea estates on misty hills. Eravikulam National Park, Mattupetty Dam, Top Station viewpoint. Most romantic destination."},
  {"id":"shimla","destination":"Shimla","country":"India","tags":["hill station","colonial","snow","mall road","mountains","family","couple","scenic","toy train","cool","cold","snowy","winter","christmas"],"weather":"cold snowy cool winter mountains colonial charming christmas snow","mood":"scenic charming family romantic snowy cozy","best_months":"October to February for snow, March to June pleasant","budget_level":"budget to mid-range","trip_types":["Family","Couple","Friends"],"content":"Shimla, former summer capital of British India. Mall Road, Christ Church, Kufri snow point. Famous toy train from Kalka. Snow in winter."},
  {"id":"rishikesh","destination":"Rishikesh","country":"India","tags":["yoga","adventure","rafting","spiritual","ganges","backpacker","bungee jumping","trekking","budget","peaceful","riverside","sunny","pleasant"],"weather":"pleasant sunny riverside spiritual calm adventure clear","mood":"adventure spiritual peaceful backpacker thrill","best_months":"September to June","budget_level":"budget","trip_types":["Solo","Friends","Couple"],"content":"Rishikesh is India adventure and spiritual capital. White water rafting on Ganga, bungee jumping, yoga ashrams, Laxman Jhula. Gateway to Himalayan treks."},
  {"id":"ladakh","destination":"Ladakh","country":"India","tags":["high altitude","bike trip","adventure","monastery","pangong lake","mountains","off-beat","friends","road trip","rugged","cold desert","sunny cold","dramatic","landscape"],"weather":"cold sunny dry high altitude crisp clear dramatic barren beautiful","mood":"adventure thrill rugged off-beat dramatic","best_months":"June to September","budget_level":"budget to mid-range","trip_types":["Friends","Solo","Couple"],"content":"Ladakh is India top adventure destination. Pangong Lake, Nubra Valley, Khardung La Pass world highest motorable road, Hemis Monastery. Epic bike trips."},
  {"id":"andaman","destination":"Andaman","country":"India","tags":["beach","snorkeling","diving","island","honeymoon","nature","pristine","blue water","coral","sunny","tropical","clear water","swimming","paradise"],"weather":"sunny tropical warm clear blue water pristine paradise","mood":"romantic peaceful island honeymoon paradise","best_months":"October to May","budget_level":"mid-range","trip_types":["Honeymoon","Couple","Family"],"content":"Andaman Islands - India most pristine beaches and crystal-clear waters. Radhanagar Beach Asia best beach, scuba diving, snorkeling at Havelock Island."},
  {"id":"darjeeling","destination":"Darjeeling","country":"India","tags":["tea gardens","toy train","mountains","cold","misty","foggy","scenic","family","couple","peaceful","rainy","clouds","cool","chilly"],"weather":"cold misty foggy rainy clouds mountains cool chilly drizzle tea","mood":"peaceful scenic romantic nature misty cozy","best_months":"March to May, September to November","budget_level":"budget","trip_types":["Family","Couple","Solo"],"content":"Darjeeling famous for tea gardens, Himalayan views, iconic toy train. Stunning views of Kangchenjunga, Tiger Hill sunrise. Cool misty weather year round."},
  {"id":"spiti","destination":"Spiti Valley","country":"India","tags":["cold desert","adventure","off-beat","monastery","mountains","bike trip","rugged","isolated","friends","solo","cold","dry","high altitude","dramatic"],"weather":"cold dry high altitude sunny crisp clear dramatic barren","mood":"adventure off-beat rugged thrill isolated","best_months":"June to September","budget_level":"budget to mid-range","trip_types":["Friends","Solo"],"content":"Spiti Valley most remote and dramatic destination. Key Monastery, Chandratal Lake, Pin Valley. Perfect for adventure seekers and off-beat travellers."},
  {"id":"bali","destination":"Bali","country":"Indonesia","tags":["beach","temples","culture","rice terraces","surfing","nightlife","spa","romantic","yoga","tropical","sunny","warm","lush green","paradise"],"weather":"sunny warm tropical lush green humid paradise","mood":"romantic chill adventure party yoga spiritual","best_months":"April to October","budget_level":"budget to mid-range","trip_types":["Couple","Friends","Honeymoon","Solo"],"content":"Bali is Indonesia island of gods. Ubud rice terraces, Tanah Lot temple, Seminyak beach clubs, Kuta surfing, Nusa Penida cliffs. Spa treatments, yoga retreats."},
  {"id":"paris","destination":"Paris","country":"France","tags":["romantic","eiffel tower","art","fashion","museums","couple","honeymoon","culture","food","luxury","mild","temperate","spring","rainy","chic"],"weather":"mild cool spring autumn pleasant rainy sometimes drizzle chic","mood":"romantic luxury cultural artistic sophisticated","best_months":"April to June, September to October","budget_level":"expensive","trip_types":["Couple","Honeymoon","Solo"],"content":"Paris, City of Love. Eiffel Tower, Louvre Museum, Versailles Palace, Champs-Elysees. World-class French cuisine, fashion, wine, art."},
  {"id":"tokyo","destination":"Tokyo","country":"Japan","tags":["tech","culture","food","anime","shopping","temples","cherry blossom","modern","family","unique","cool","spring","autumn leaves","seasonal"],"weather":"cool pleasant spring cherry blossom autumn colourful seasonal mild","mood":"unique cultural foodie family quirky","best_months":"March to May, September to November","budget_level":"mid-range to expensive","trip_types":["Family","Friends","Solo","Couple"],"content":"Tokyo blends ultra-modern and traditional Japan. Shibuya crossing, Senso-ji temple, Akihabara, cherry blossoms in spring. World safest cleanest city."},
  {"id":"dubai","destination":"Dubai","country":"UAE","tags":["luxury","shopping","burj khalifa","desert safari","family","modern","gold souk","skyscrapers","nightlife","hot","sunny","desert heat","glamorous"],"weather":"hot sunny dry desert heat warm clear skies arid","mood":"luxury modern glam shopping spectacular","best_months":"November to April","budget_level":"expensive to luxury","trip_types":["Family","Friends","Couple"],"content":"Dubai city of superlatives. Burj Khalifa, Dubai Mall, desert safari, Palm Jumeirah, gold souks, world-class hotels."},
  {"id":"singapore","destination":"Singapore","country":"Singapore","tags":["clean","modern","family","food","gardens by the bay","marina bay","shopping","safe","warm","tropical","sunny","multicultural"],"weather":"warm tropical humid sunny occasionally rainy","mood":"family friendly modern clean safe urban","best_months":"February to April","budget_level":"mid-range to expensive","trip_types":["Family","Couple","Friends"],"content":"Singapore vibrant city-state. Marina Bay Sands, Gardens by the Bay, Sentosa Island, hawker centre food, Universal Studios. Extremely safe and family-friendly."},
  {"id":"bangkok","destination":"Bangkok","country":"Thailand","tags":["temples","street food","nightlife","shopping","budget","backpacker","affordable","party","hot","tropical","humid","floating market"],"weather":"hot tropical humid sunny","mood":"party budget backpacker foodie vibrant","best_months":"November to February","budget_level":"budget","trip_types":["Friends","Solo","Couple"],"content":"Bangkok Thailand vibrant capital. Grand Palace, Wat Pho, Chatuchak market, Khao San Road, floating markets, incredible street food."},
  {"id":"maldives","destination":"Maldives","country":"Maldives","tags":["luxury","overwater bungalow","honeymoon","beach","snorkeling","diving","romantic","exclusive","crystal water","coral reef","sunny","warm","tropical paradise"],"weather":"sunny warm tropical clear blue water paradise perfect","mood":"romantic luxury exclusive honeymoon paradise ultimate","best_months":"November to April","budget_level":"luxury","trip_types":["Honeymoon","Couple"],"content":"Maldives ultimate luxury escape. Overwater bungalows, crystal-clear turquoise lagoons, coral reefs, snorkeling, diving. World top honeymoon destination."},
  {"id":"switzerland","destination":"Switzerland","country":"Switzerland","tags":["alps","skiing","scenic train","chocolate","honeymoon","nature","romantic","luxury","snow","mountains","cold","snowy winter","green summer","alpine"],"weather":"cold snowy winter green summer alpine crisp fresh mountain air clear","mood":"romantic luxury scenic adventure snowy majestic","best_months":"June to September, December to February","budget_level":"very expensive","trip_types":["Honeymoon","Couple","Family"],"content":"Switzerland most scenic country. Swiss Alps, Jungfrau, Glacier Express scenic train, Geneva lake, Interlaken adventure hub. Honeymoon paradise."},
  {"id":"london","destination":"London","country":"UK","tags":["history","culture","museums","theatre","shopping","family","couple","iconic","british","cool","rainy","cloudy","mild","drizzle"],"weather":"cool rainy cloudy mild drizzle overcast grey british weather","mood":"cultural historical iconic family sophisticated","best_months":"May to September","budget_level":"expensive","trip_types":["Family","Couple","Solo","Friends"],"content":"London global cultural capital. Big Ben, Tower of London, Buckingham Palace, British Museum, West End theatre, Notting Hill, Oxford Street."},
  {"id":"new_york","destination":"New York","country":"USA","tags":["iconic","times square","broadway","shopping","museums","food","urban","diverse","energy","cold winters","hot summers","autumn leaves"],"weather":"variable cold winter hot summer pleasant spring autumn colourful","mood":"urban energy iconic diverse vibrant","best_months":"April to June, September to November","budget_level":"expensive","trip_types":["Friends","Couple","Solo","Family"],"content":"New York City never sleeps. Times Square, Central Park, Statue of Liberty, Broadway shows, Brooklyn Bridge, world diverse food scene."},
  {"id":"vietnam","destination":"Vietnam","country":"Vietnam","tags":["history","street food","halong bay","culture","beaches","budget","backpacker","hoi an","affordable","tropical","warm","humid"],"weather":"tropical warm humid sometimes rainy seasonal","mood":"budget backpacker cultural foodie adventurous","best_months":"February to April","budget_level":"budget","trip_types":["Friends","Solo","Couple"],"content":"Vietnam most diverse destination. Ha Long Bay cruise, Hoi An ancient town, Hanoi old quarter, Pho street food. Extremely budget-friendly."},
  {"id":"istanbul","destination":"Istanbul","country":"Turkey","tags":["history","bazaar","culture","hagia sophia","bosphorus","food","romantic","ancient","mild","temperate","europe asia"],"weather":"mild temperate warm summer cool winter pleasant spring autumn","mood":"cultural historical romantic foodie mystical","best_months":"April to June, September to November","budget_level":"budget to mid-range","trip_types":["Couple","Friends","Solo","Family"],"content":"Istanbul bridges Europe and Asia. Hagia Sophia, Blue Mosque, Grand Bazaar, Bosphorus cruise, Turkish cuisine, hammam bath. Rich Ottoman history."},
  {"id":"phuket","destination":"Phuket","country":"Thailand","tags":["beach","nightlife","party","island hopping","diving","affordable","friends","couple","tropical","water sports","sunny","hot","paradise"],"weather":"sunny hot tropical warm beach paradise clear water","mood":"party beach adventure fun vibrant","best_months":"November to April","budget_level":"budget to mid-range","trip_types":["Friends","Couple","Solo"],"content":"Phuket Thailand largest island. Patong nightlife, Phi Phi Islands, Maya Bay, snorkeling, Bangla Road party scene. Budget-friendly with stunning tropical beauty."},
]

STOP_WORDS = {"a","an","the","and","or","in","on","at","to","for","of","is","are","was","were","with","by","from","as","its","it","be","this","that","have","has","had","i","me","my","want","place","go","visit","trip","travel","destination","where","should","best","top","good","great","nice"}

# Weather/mood/season keyword mappings
WEATHER_MAP = {
  "rainy": ["rainy","monsoon","drizzle","rainfall","rain","wet","cloudy","overcast"],
  "snowy": ["snowy","snow","snowfall","blizzard","white","freezing","icy","winter wonderland"],
  "cold": ["cold","chilly","freezing","cool","chill","chilled","winter","frosty","nippy"],
  "hot": ["hot","sunny","warm","tropical","heat","summer","blazing","scorching"],
  "misty": ["misty","foggy","mist","fog","clouds","overcast","hazy"],
  "pleasant": ["pleasant","mild","moderate","perfect weather","nice weather","comfortable","spring","autumn"],
  "tropical": ["tropical","humid","lush green","green","paradise"],
  "dry": ["dry","arid","desert","barren","clear skies"],
}

MOOD_MAP = {
  "romantic": ["romantic","romance","love","couple","honeymoon","intimate","cozy"],
  "adventure": ["adventure","adventurous","thrill","exciting","extreme","trek","hike","bike","rugged"],
  "peaceful": ["peaceful","calm","serene","quiet","relax","relaxing","tranquil","slow","chill"],
  "party": ["party","nightlife","clubs","rave","dance","festival","fun","lively"],
  "cultural": ["cultural","culture","history","heritage","temples","monuments","art","museum"],
  "nature": ["nature","wildlife","forest","jungle","national park","green","scenic","landscape"],
  "budget": ["budget","cheap","affordable","backpacker","low cost","economical"],
  "luxury": ["luxury","luxurious","premium","5 star","opulent","exclusive","lavish"],
}

INTENT_KEYWORDS = {
  "honeymoon":3.0,"romantic":3.0,"romance":3.0,"couple":2.5,
  "adventure":2.5,"trekking":2.5,"trek":2.5,"hiking":2.5,
  "beach":2.5,"beaches":2.5,"island":2.0,
  "luxury":2.5,"budget":2.0,"cheap":2.0,"affordable":2.0,
  "family":2.5,"kids":2.0,"children":2.0,
  "friends":2.0,"group":1.8,"solo":2.0,
  "snow":2.5,"ski":2.5,"skiing":2.5,"mountains":2.0,"mountain":2.0,
  "nightlife":2.5,"party":2.5,"clubs":2.0,
  "culture":1.8,"history":1.8,"heritage":2.0,"temples":2.0,
  "nature":1.8,"wildlife":2.0,"peaceful":1.8,
  "food":1.8,"street food":2.0,
  "diving":2.5,"snorkeling":2.5,"water sports":2.5,
  "backpacker":2.0,"spiritual":2.0,"yoga":2.0,
  "rainy":2.5,"rain":2.5,"monsoon":2.5,"drizzle":2.0,"wet":2.0,
  "cold":2.5,"snowy":2.5,"winter":2.5,"snow":2.5,"freezing":2.0,"chilly":2.0,
  "hot":2.0,"sunny":2.0,"tropical":2.0,"warm":1.8,
  "misty":2.5,"foggy":2.5,"mist":2.5,"fog":2.0,"clouds":2.0,
  "pleasant":1.8,"mild":1.8,"cool":1.8,
  "green":2.0,"lush":2.0,"waterfall":2.5,"waterfalls":2.5,
  "desert":2.0,"arid":1.8,"dry":1.8,
  "spring":2.0,"autumn":2.0,"summer":1.8,"monsoon":2.5,
  "scenic":1.8,"views":1.8,"photography":1.8,"dramatic":2.0,
}

def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r[a-z]+, text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

def _expand_query(query: str) -> str:
    """Expand query with weather/mood synonyms."""
    q_lower = query.lower()
    expansions = []
    for key, synonyms in WEATHER_MAP.items():
        if any(s in q_lower for s in synonyms):
            expansions.extend(synonyms)
    for key, synonyms in MOOD_MAP.items():
        if any(s in q_lower for s in synonyms):
            expansions.extend(synonyms)
    if expansions:
        return query + " " + " ".join(set(expansions))
    return query

def _score_doc(query_tokens: List[str], doc: dict) -> float:
    doc_text = (
        doc["destination"] + " " + doc["country"] + " " +
        " ".join(doc["tags"]) * 3 + " " +
        doc.get("weather","") * 3 + " " +
        doc.get("mood","") * 2 + " " +
        doc["content"] + " " +
        doc.get("budget_level","") + " " +
        " ".join(doc.get("trip_types",[]))
    ).lower()
    doc_tokens = set(_tokenize(doc_text))
    tag_set = set(t.lower() for t in doc["tags"])
    weather_set = set(_tokenize(doc.get("weather","")))
    mood_set = set(_tokenize(doc.get("mood","")))
    trip_type_set = set(t.lower() for t in doc.get("trip_types",[]))
    dest_lower = doc["destination"].lower()
    score = 0.0
    for token in query_tokens:
        boost = INTENT_KEYWORDS.get(token, 1.0)
        if token == dest_lower or token in dest_lower:
            score += 8.0 * boost; continue
        if token in tag_set:
            score += 4.0 * boost; continue
        if token in weather_set:
            score += 4.5 * boost; continue
        if token in mood_set:
            score += 3.5 * boost; continue
        if token in trip_type_set:
            score += 3.0 * boost; continue
        if token in doc_tokens:
            score += 1.5 * boost
    if len(query_tokens) > 0:
        score /= math.sqrt(len(query_tokens))
    return round(score, 4)

class RAGKnowledgeBase:
    def __init__(self):
        self.docs = DESTINATION_DOCS

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        expanded = _expand_query(query)
        query_tokens = _tokenize(expanded)
        scored = []
        for doc in self.docs:
            s = _score_doc(query_tokens, doc)
            scored.append((s, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
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
                "trip_types": doc.get("trip_types",[]),
                "content": doc["content"],
            })
        return results

    def get_destination_context(self, destination: str) -> str:
        results = self.semantic_search(destination, top_k=1)
        if results and results[0]["raw_score"] > 1.0:
            doc = results[0]
            return (
                f"[RAG Context] {doc[destination]}, {doc[country]}. "
                f"Best time: {doc[best_months]}. Budget: {doc[budget_level]}. "
                f"Highlights: {doc[content]}"
            )
        return ""

    def get_similar_destinations(self, destination: str, trip_type: str = "", budget_hint: str = "") -> List[Dict]:
        query = f"{destination} {trip_type} {budget_hint}"
        results = self.semantic_search(query, top_k=8)
        return [r for r in results if r["destination"].lower() != destination.lower()][:6]

_kb = None
def get_knowledge_base() -> RAGKnowledgeBase:
    global _kb
    if _kb is None:
        _kb = RAGKnowledgeBase()
    return _kb
'''

# Fix the f-string quotes issue
content = content.replace("r[a-z]+", "r'[a-z]+'")
content = content.replace("doc[destination]", "doc['destination']")
content = content.replace("doc[country]", "doc['country']")
content = content.replace("doc[best_months]", "doc['best_months']")
content = content.replace("doc[budget_level]", "doc['budget_level']")
content = content.replace("doc[content]", "doc['content']")

with open("rag_knowledge.py", "w", encoding="utf-8") as f:
    f.write(content)
print("rag_knowledge.py written successfully")

# Verify syntax
import ast
try:
    ast.parse(content)
    print("Syntax OK")
except SyntaxError as e:
    print("Syntax Error:", e)
