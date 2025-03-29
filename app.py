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

# Frasi spontanee per il piano
intros = ["Ecco un viaggio perfetto per te!", "Preparati per un’avventura unica!", "Ti porto in un posto speciale!"]
day_starts = ["Giorno {day}:", "Day {day} sarà così:", "Per il giorno {day}:"]
outros = ["Che ne dici? Pronto a partire?", "Un piano così non si dimentica!", "Viaggio confermato? Fammi sapere!"]

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
        return {"recommendations": [], "message": "Nessuna opzione disponibile"}

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

    # Scegli la destinazione migliore
    top_destination = filtered_data.sort_values(['similarity', 'price'], ascending=[False, True]).iloc[0]
    activities = top_destination['activities']
    days = min(duration, top_destination['duration_days'])

    # Crea un piano narrativo
    plan = f"{random.choice(intros)}\n\n"
    for day in range(1, days + 1):
        activity = random.choice(activities) if activities else "Esplora la zona"
        plan += f"{random.choice(day_starts).format(day=day)} {activity} a {top_destination['destination']}.\n"
    plan += f"\nPrezzo totale: €{top_destination['price']}\n{random.choice(outros)}"

    # Risposta strutturata
    recommendation = {
        "id": int(top_destination['id']),
        "destination": top_destination['destination'],
        "price": float(top_destination['price']),
        "duration_days": int(top_destination['duration_days']),
        "activities": activities
    }

    return {"recommendations": [recommendation], "plan": plan}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
