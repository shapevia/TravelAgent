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
    "Ecco il tuo viaggio da sogno con Shapevia!", 
    "Preparati per un’esperienza incredibile!", 
    "Ti ho creato un piano perfetto!"
]
day_starts = [
    "Giorno {day}:", 
    "Per il {day}° giorno:", 
    "Day {day} sarà speciale:"
]
transitions = [
    "Poi, direzione", 
    "Il giorno dopo, ti sposti a", 
    "Successiva tappa:"
]
outros = [
    "Che ne pensi? Pronto a prenotare con Shapevia?", 
    "Un viaggio così ti aspetta!", 
    "Fammi sapere se vuoi aggiustare qualcosa!"
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

    # Scegli fino a 3 destinazioni
    top_destinations = filtered_data.sort_values(['similarity', 'price'], ascending=[False, True]).head(3)
    total_price = top_destinations['price'].sum()
    if total_price > budget:
        top_destinations = top_destinations.head(1)  # Torna a 1 se supera il budget
        total_price = top_destinations['price'].sum()

    # Crea il piano
    plan = f"{random.choice(intros)}\n\n"
    days_left = duration
    day = 1
    recommendations = []

    for i, (_, dest) in enumerate(top_destinations.iterrows()):
        dest_days = min(dest['duration_days'], days_left)
        activities = dest['activities']
        recommendations.append({
            "id": int(dest['id']),
            "destination": dest['destination'],
            "price": float(dest['price']),
            "duration_days": int(dest['duration_days']),
            "activities": activities
        })

        if i > 0:
            plan += f"{random.choice(transitions)} {dest['destination']}.\n"

        for d in range(dest_days):
            activity = random.choice(activities) if activities else "Tempo libero"
            plan += f"{random.choice(day_starts).format(day=day)} {activity} a {dest['destination']}.\n"
            day += 1
            days_left -= 1
            if days_left <= 0:
                break

        if days_left <= 0:
            break

    # Aggiungi giorni liberi se necessario
    while days_left > 0:
        plan += f"{random.choice(day_starts).format(day=day)} Tempo libero per rilassarti o esplorare.\n"
        day += 1
        days_left -= 1

    plan += f"\nPrezzo totale: €{total_price}\n{random.choice(outros)}"

    return {"recommendations": recommendations, "plan": plan}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
