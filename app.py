from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
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

# Carica il dataset
try:
    with open('travel_data.pkl', 'rb') as f:
        travel_data = pickle.load(f)
except FileNotFoundError:
    travel_data = pd.DataFrame({
        'id': [1], 'destination': ['Generica'], 'price': [500], 
        'duration_days': [5], 'tags': [['spiaggia']], 'activities': [['Relax']]
    })

# Frasi per il piano
intros = [
    "Ecco un viaggio epico con Shapevia!", 
    "Ti ho preparato un’avventura su misura!", 
    "Partiamo con un piano fantastico!"
]
day_starts = [
    "Giorno {day}:", 
    "Il {day}° giorno ti aspetta:", 
    "Day {day} è tutto per te:"
]
transitions = [
    "Poi, si vola verso", 
    "Il prossimo stop è", 
    "Dopo, ti porto a"
]
outros = [
    "Pronto a vivere questo viaggio con Shapevia?", 
    "Un itinerario da sogno, che dici?", 
    "Fammi sapere se vuoi personalizzarlo ancora!"
]
extras = [
    "Aggiungi una passeggiata serale!", 
    "Perfetto per un po’ di shopping locale.", 
    "Non perderti un tramonto da cartolina."
]

@app.get("/")
def read_root():
    return {"message": "Shapevia Travel Agent API"}

@app.post("/recommend")
def recommend(preferences: UserPreferences):
    budget = preferences.budget
    interests = [interest.lower() for interest in preferences.interests]
    duration = preferences.duration or 7

    # Filtra il dataset
    filtered_data = travel_data[
        (travel_data['price'] <= budget) &
        (travel_data['duration_days'] <= duration)
    ]

    if filtered_data.empty:
        return {"recommendations": [], "message": "Nessuna opzione disponibile entro il budget"}

    # Calcola similarità
    all_tags = set(tag for tags in travel_data['tags'] for tag in tags)
    tag_matrix = pd.DataFrame(0, index=travel_data.index, columns=list(all_tags))
    for i, tags in enumerate(travel_data['tags']):
        for tag in tags:
            tag_matrix.loc[i, tag] = 1

    user_vector = pd.Series(0, index=tag_matrix.columns)
    for interest in interests:
        if interest in user_vector.index:
            user_vector[interest] = 1

    similarity = cosine_similarity([user_vector], tag_matrix.loc[filtered_data.index])[0]
    filtered_data = filtered_data.copy()
    filtered_data['similarity'] = similarity

    # Scegli destinazioni dinamicamente
    remaining_budget = budget
    days_left = duration
    recommendations = []
    plan = f"{random.choice(intros)}\n\n"
    day = 1

    sorted_data = filtered_data.sort_values(['similarity', 'price'], ascending=[False, True])
    for _, dest in sorted_data.iterrows():
        if remaining_budget < dest['price'] or days_left < 1:
            break
        if len(recommendations) >= 3:  # Limite massimo di tappe
            break

        dest_days = min(random.randint(2, dest['duration_days']), days_left)
        activities = dest['activities']
        recommendations.append({
            "id": int(dest['id']),
            "destination": dest['destination'],
            "price": float(dest['price']),
            "duration_days": int(dest['duration_days']),
            "activities": activities
        })

        if recommendations:
            plan += f"{random.choice(transitions)} {dest['destination']}.\n"

        for d in range(dest_days):
            activity = random.choice(activities) if activities else "Tempo libero"
            extra = random.choice(extras) if random.random() > 0.5 else ""
            plan += f"{random.choice(day_starts).format(day=day)} {activity} a {dest['destination']}. {extra}\n"
            day += 1
            days_left -= 1

        remaining_budget -= dest['price']

    # Riempi i giorni rimanenti
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
