from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

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

# Dati per generazione dinamica
places = ['Baia', 'Costa', 'Valle', 'Città', 'Villaggio', 'Montagna', 'Isola', 'Lago']
adjectives = ['Smeraldo', 'Azzurra', 'Dorata', 'Antica', 'Nascosta', 'Selvaggia', 'Tramonti', 'Luminosa']
regions = ['Italia', 'Francia', 'Spagna', 'Grecia', 'Thailandia', 'Messico', 'Canada', 'Giappone', 'Croazia', 'Sudafrica']
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
all_tags = list(base_activities.keys())

# Frasi per il piano
intros = [
    "Ecco un viaggio epico con Shapevia!", 
    "Ti ho preparato un’avventura unica!", 
    "Partiamo con un piano su misura!"
]
day_starts = [
    "Giorno {day}:", 
    "Il {day}° giorno ti aspetta:", 
    "Day {day} è per te:"
]
transitions = [
    "Poi, si vola verso", 
    "Prossima tappa:", 
    "Dopo, scopri"
]
outros = [
    "Pronto a partire con Shapevia?", 
    "Un viaggio da sogno, che ne dici?", 
    "Fammi sapere se vuoi rifinirlo!"
]
extras = [
    "Perfetto per una serata speciale!", 
    "Aggiungi un po’ di relax extra.", 
    "Non perderti i sapori locali."
]

@app.get("/")
def read_root():
    return {"message": "Shapevia Travel Agent API - Illimitato"}

@app.post("/recommend")
def recommend(preferences: UserPreferences):
    budget = preferences.budget
    interests = [interest.lower() for interest in preferences.interests]
    duration = preferences.duration or 7

    # Genera destinazioni dinamiche
    def generate_destination():
        place = random.choice(places)
        adj = random.choice(adjectives)
        region = random.choice(regions)
        dest_tags = random.sample(all_tags, random.randint(2, 4))
        dest_activities = []
        for tag in dest_tags:
            dest_activities.extend(random.sample(base_activities[tag], min(2, len(base_activities[tag]))))
        price = random.randint(500, 2000)
        days = random.randint(3, 10)
        return {
            'destination': f"{place} {adj}, {region}",
            'price': price,
            'duration_days': days,
            'tags': dest_tags,
            'activities': list(set(dest_activities))  # Rimuovi duplicati
        }

    # Crea un "dataset" dinamico
    destinations = [generate_destination() for _ in range(10)]  # Genera 10 opzioni
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
        if remaining_budget < dest['price'] or days_left < 1:
            break
        if len(recommendations) >= 3:
            break

        dest_days = min(random.randint(2, dest['duration_days']), days_left)
        recommendations.append({
            "id": random.randint(1000, 9999),  # ID fittizio
            "destination": dest['destination'],
            "price": float(dest['price']),
            "duration_days": int(dest['duration_days']),
            "activities": dest['activities']
        })

        if recommendations:
            plan += f"{random.choice(transitions)} {dest['destination']}.\n"

        for d in range(dest_days):
            activity = random.choice(dest['activities'])
            extra = random.choice(extras) if random.random() > 0.5 else ""
            plan += f"{random.choice(day_starts).format(day=day)} {activity} a {dest['destination']}. {extra}\n"
            day += 1
            days_left -= 1

        remaining_budget -= dest['price']

    while days_left > 0:
        last_dest = recommendations[-1]['destination'] if recommendations else "in zona"
        plan += f"{random.choice(day_starts).format(day=day)} Tempo libero a {last_dest}. {random.choice(extras)}\n"
        day += 1
        days_left -= 1

    total_price = sum(r['price'] for r in recommendations)
    plan += f"\nPrezzo totale: €{total_price} (Budget rimanente: €{remaining_budget})\n{random.choice(outros)}"

    return {"recommendations": recommendations, "plan": plan}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
