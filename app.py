from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import asyncio

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

# Dati per generazione realistica
real_cities = [
    'Positano', 'Chamonix', 'New York', 'Kyoto', 'Nairobi', 'Banff', 'Barcellona', 'Santorini', 
    'Ubud', 'Reykjavik', 'Dubrovnik', 'Siem Reap', 'Cape Town', 'Queenstown', 'Lisbona', 
    'Phuket', 'Cusco', 'Amsterdam', 'Tulum', 'Zermatt', 'Marrakech', 'Praga', 'Sydney', 
    'Santander', 'Lima'
]
countries = [
    'Italia', 'Francia', 'USA', 'Giappone', 'Kenya', 'Canada', 'Spagna', 'Grecia', 'Indonesia', 
    'Islanda', 'Croazia', 'Cambogia', 'Sudafrica', 'Nuova Zelanda', 'Portogallo', 'Thailandia', 
    'Perù', 'Olanda', 'Messico', 'Svizzera', 'Marocco', 'Repubblica Ceca', 'Australia', 'Spagna', 'Perù'
]
prefixes = ['Baia di', 'Costa di', 'Valle di', '', 'Lago di', 'Monti di']
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
foods = ['Pizza locale', 'Sushi fresco', 'Tapas', 'Pad thai', 'Bistecca', 'Paella', 'Tacos', 'Ramen']
all_tags = list(base_activities.keys())

# Frasi per il piano
intros = [
    "Ecco il tuo viaggio perfetto con Shapevia!", 
    "Un’avventura unica ti aspetta!", 
    "Ho creato un piano epico per te!"
]
day_starts = [
    "Giorno {day}:", 
    "Il {day}° giorno:", 
    "Day {day} è pronto:"
]
transitions = [
    "Poi, via verso", 
    "Prossima fermata:", 
    "Dopo, direzione"
]
outros = [
    "Che ne pensi? Pronto con Shapevia?", 
    "Un viaggio da sogno, vero?", 
    "Personalizziamo ancora?"
]
extras = [
    "Goditi un tramonto speciale!", 
    "Perfetto per un po’ di relax.", 
    "Assaggia i sapori del posto."
]

@app.get("/")
def read_root():
    return {"message": "Shapevia Travel Agent API - Illimitato e Realistico"}

async def generate_destination():
    city = random.choice(real_cities)
    country = random.choice(countries)
    prefix = random.choice(prefixes)
    dest_tags = random.sample(all_tags, random.randint(2, 4))
    dest_activities = []
    for tag in dest_tags:
        dest_activities.extend(random.sample(base_activities[tag], min(2, len(base_activities[tag]))))
    price = random.randint(500, 2000)
    days = random.randint(3, 10)
    return {
        'destination': f"{prefix}{city}, {country}".strip(),
        'price': price,
        'duration_days': days,
        'tags': dest_tags,
        'activities': list(set(dest_activities))
    }

@app.post("/recommend")
async def recommend(preferences: UserPreferences):
    budget = preferences.budget
    interests = [interest.lower() for interest in preferences.interests]
    duration = preferences.duration or 7

    # Genera destinazioni in parallelo per scalabilità
    tasks = [generate_destination() for _ in range(10)]
    destinations = await asyncio.gather(*tasks)
    filtered_data = [d for d in destinations if 
                     d['price'] <= budget and 
                     d['duration_days'] <= duration and 
                     any(tag in interests for tag in d['tags'])]

    if not filtered_data:
        return {"recommendations": [], "message": "Nessuna opzione disponibile"}

    # Scegli destinazioni
    remaining_budget = budget
    days_left = duration
    recommendations = []
    plan = f"{random.choice(intros)}\n\n"
    day = 1

    random.shuffle(filtered_data)
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

        if recommendations:
            plan += f"{random.choice(transitions)} {dest['destination']} con {transport}.\n"
        else:
            plan += f"Arrivo a {dest['destination']} con {transport}.\n"

        for d in range(dest_days):
            activity = random.choice(dest['activities'])
            food = random.choice(foods)
            extra = random.choice(extras) if random.random() > 0.5 else ""
            plan += f"{random.choice(day_starts).format(day=day)} {activity} a {dest['destination']}. Cena con {food}. {extra}\n"
            day += 1
            days_left -= 1

        remaining_budget -= dest['price']

    while days_left > 0:
        last_dest = recommendations[-1]['destination'] if recommendations else "in zona"
        food = random.choice(foods)
        plan += f"{random.choice(day_starts).format(day=day)} Tempo libero a {last_dest}. Prova {food}. {random.choice(extras)}\n"
        day += 1
        days_left -= 1

    total_price = sum(r['price'] for r in recommendations)
    plan += f"\nPrezzo totale: €{total_price} (Budget rimanente: €{remaining_budget})\n{random.choice(outros)}"

    return {"recommendations": recommendations, "plan": plan}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
