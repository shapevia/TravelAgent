from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shapevia.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modello Pydantic per l’input
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
        'id': [1, 2, 3],
        'destination': ['Spiaggia Generica', 'Montagna Generica', 'Città Generica'],
        'price': [500, 700, 600],
        'duration_days': [5, 7, 3],
        'tags': [['spiaggia'], ['montagna'], ['città']]
    })

# Crea una matrice binaria per i tag
all_tags = set(tag for tags in travel_data['tags'] for tag in tags)
tag_matrix = pd.DataFrame(0, index=travel_data.index, columns=list(all_tags))
for i, tags in enumerate(travel_data['tags']):
    for tag in tags:
        tag_matrix.loc[i, tag] = 1

# Endpoint base
@app.get("/")
def read_root():
    return {"message": "Travel Agent API is running"}

# Endpoint per raccomandazioni
@app.post("/recommend")
def recommend(preferences: UserPreferences):
    budget = preferences.budget
    interests = [interest.lower() for interest in preferences.interests]
    duration = preferences.duration or 7

    # Filtra per budget e durata
    filtered_data = travel_data[
        (travel_data['price'] <= budget) &
        (travel_data['duration_days'] <= duration)
    ]

    if filtered_data.empty:
        return {"recommendations": [], "message": "Nessuna opzione entro budget e durata"}

    # Vettore utente per interessi
    user_vector = pd.Series(0, index=tag_matrix.columns)
    for interest in interests:
        if interest in user_vector.index:
            user_vector[interest] = 1

    # Calcola similarità coseno
    similarity = cosine_similarity([user_vector], tag_matrix.loc[filtered_data.index])[0]
    filtered_data = filtered_data.copy()
    filtered_data['similarity'] = similarity

    # Ordina per similarità e prezzo
    recommendations = filtered_data.sort_values(['similarity', 'price'], ascending=[False, True]).head(5)

    # Formatta la risposta
    result = [
        {"id": int(row['id']), "destination": row['destination'], "price": float(row['price'])}
        for _, row in recommendations.iterrows()
    ]

    return {"recommendations": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
