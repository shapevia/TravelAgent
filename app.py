from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import asyncio
import aiohttp
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shapevia.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserPreferences(BaseModel):
    user_id: int
    budget: float
    interests: list[str]
    duration: int = None

# Attività predefinite
base_activities = {
    'spiaggia': ['Gita in barca', 'Snorkeling', 'Relax in spiaggia', 'Cena sul mare'],
    'montagna': ['Trekking', 'Sci', 'Escursione panoramica', 'Rifugio alpino'],
    'città': ['Tour storico', 'Shopping', 'Museo', 'Cena in centro'],
    'cultura': ['Visita templi', 'Mercato locale', 'Festival', 'Lezione di cucina'],
    'natura': ['Safari', 'Canoa', 'Osservazione stelle', 'Cascate'],
    'avventura': ['Rafting', 'Parapendio', 'Bungee jumping', 'Quad'],
    'relax': ['Spa', 'Yoga', 'Passeggiata tranquilla', 'Lettura al tramonto'],
    'cibo': ['Degustazione vini', 'Street food', 'Cena gourmet', 'Corso culinario']
}
transports = ['Volo diretto', 'Treno panoramico', 'Auto a noleggio', 'Traghetto', 'Bus locale']
all_tags = list(base_activities.keys())

# Frasi
intros = ["Ecco il tuo viaggio perfetto con Shapevia!", "Un’avventura unica ti aspetta!", "Ho creato un piano epico per te!"]
day_starts = ["Giorno {day}:", "Il {day}° giorno:", "Day {day} è pronto:"]
transitions = ["Poi, via verso", "Prossima fermata:", "Dopo, direzione"]
outros = ["Che ne pensi? Pronto con Shapevia?", "Un viaggio da sogno, vero?", "Personalizziamo ancora?"]
extras = ["Goditi un tramonto speciale!", "Perfetto per un po’ di relax.", "Assaggia i sapori del posto."]

# Cache per i paesi (illimitati)
countries_cache = []

async def fetch_countries():
    global countries_cache
    if not countries_cache:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://restcountries.com/v3.1/all') as response:
                if response.status == 200:
                    countries_cache = await response.json()
    return countries_cache

@app.get("/")
def read_root():
    return {"message": "Shapevia Travel Agent API - Dati Esterni Illimitati"}

async def generate_destination(interests, budget, duration):
    countries = await fetch_countries()
    if not countries:
        return None  # Fallback se l'API fallisce
    
    country = random.choice(countries)
    city = country.get('capital', [''])[0] or country['name']['common']
    dest_tags = random.sample(all_tags, random.randint(1, 3))
    if interests:
        dest_tags.append(random.choice(interests))
    dest_tags = list(set(dest_tags))
    dest_activities = []
    for tag in dest_tags:
        dest_activities.extend(random.sample(base_activities[tag], min(2, len(base_activities[tag]))))
    price = random.randint(200, min(1000, int(budget)))
    days = random.randint(3, min(10, duration or 7))
    return {
        'destination': f"{city}, {country['name']['common']}",
        'price': price,
        'duration_days': days,
        'tags': dest_tags,
        'activities': list(set(dest_activities)),
        'country': country['name']['common']
    }

@app.post("/recommend")
async def recommend(preferences: UserPreferences):
    budget = preferences.budget
    interests = [interest.lower() for interest in preferences.interests]
    duration = preferences.duration or 7

    tasks = [generate_destination(interests, budget, duration) for _ in range(20)]
    destinations = await asyncio.gather(*tasks)
    destinations = [d for d in destinations if d is not None]

    if not destinations:
        return {"recommendations": [], "plan": "Problema con i dati esterni. Riprova più tardi!"}

    # Vettorizzazione interessi
    tag_vectors = {tag: np.random.rand(10) for tag in all_tags}
    user_vector = np.zeros(10)
    for interest in interests:
        if interest in tag_vectors:
            user_vector += tag_vectors[interest]
    user_vector = user_vector / (len(interests) or 1)

    # Similarità
    dest_similarities = []
    for dest in destinations:
        dest_vector = np.zeros(10)
        for tag in dest['tags']:
            if tag in tag_vectors:
                dest_vector += tag_vectors[tag]
        dest_vector = dest_vector / (len(dest['tags']) or 1)
        similarity = cosine_similarity([user_vector], [dest_vector])[0][0]
        dest_similarities.append((dest, similarity))

    filtered_data = [d for d, sim in dest_similarities if d['price'] <= budget and d['duration_days'] <= duration]
    filtered_data.sort(key=lambda x: dest_similarities[destinations.index(x)][1], reverse=True)

    if not filtered_data:
        return {"recommendations": [], "plan": "Nessun piano disponibile con questo budget e interessi. Prova ad aumentare il budget!"}

    remaining_budget = budget
    days_left = duration
    recommendations = []
    plan = f"{random.choice(intros)}\n\n"
    day = 1

    for dest in filtered_data:
        if remaining_budget < dest['price'] or days_left < 1 or len(recommendations) >= 3:
            break

        dest_days = min(random.randint(2, dest['duration_days']), days_left)
        transport = random.choice(transports)
        recommendations.append({
            "id": random.randint(1000, 9999),
            "destination": dest['destination'],
            "price": float(dest['price']),
            "duration_days": int(dest['duration_days']),
            "activities": dest['activities']
        })

        if len(recommendations) > 1:
            plan += f"{random.choice(transitions)} {dest['destination']} con {transport}.\n"
        else:
            plan += f"Arrivo a {dest['destination']} con {transport}.\n"

        for d in range(dest_days):
            activity = random.choice(dest['activities'])
            extra = random.choice(extras) if random.random() > 0.5 else ""
            plan += f"{random.choice(day_starts).format(day=day)} {activity} a {dest['destination']}. {extra}\n"
            day += 1
            days_left -= 1

        remaining_budget -= dest['price']

    while days_left > 0:
        last_dest = recommendations[-1]['destination']
        plan += f"{random.choice(day_starts).format(day=day)} Tempo libero a {last_dest}. {random.choice(extras)}\n"
        day += 1
        days_left -= 1

    total_price = sum(r['price'] for r in recommendations)
    plan += f"\nPrezzo totale: €{total_price} (Budget rimanente: €{remaining_budget})\n{random.choice(outros)}"

    return {"recommendations": recommendations, "plan": plan}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
