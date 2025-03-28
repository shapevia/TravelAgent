from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from pydantic import BaseModel
from typing import List
from sklearn.decomposition import TruncatedSVD
import pickle

# Inizializza l'app FastAPI
app = FastAPI()

# Aggiungi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shapevia.com"],  # Permetti il tuo dominio
    allow_credentials=True,
    allow_methods=["*"],  # Permetti tutti i metodi
    allow_headers=["*"],  # Permetti tutti gli header
)

# Carica o crea un modello semplice (simuliamo un modello pre-addestrato)
try:
    with open('travel_recommender.pkl', 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    # Simulazione di un modello se non esiste
    model = TruncatedSVD(n_components=32)
    # Dati fittizi per inizializzare (sostituiscili con i tuoi dati reali)
    dummy_data = np.random.rand(1000, 5000)  # 1000 utenti, 5000 viaggi
    model.fit(dummy_data)
    with open('travel_recommender.pkl', 'wb') as f:
        pickle.dump(model, f)

# Definisci il modello dati per l'input utente
class UserInput(BaseModel):
    user_id: int
    budget: float
    interests: List[str]

# Endpoint di benvenuto
@app.get("/")
def read_root():
    return {"message": "Travel Agent API is running"}

# Endpoint per le raccomandazioni
@app.post("/recommend")
def recommend_trips(user_input: UserInput):
    user_id = user_input.user_id
    trip_ids = np.arange(5000)  # Simula ID viaggi

    # Simula una matrice utente-viaggio (in un caso reale, useresti dati veri)
    user_vector = np.zeros(5000)  # Vettore utente fittizio
    user_vector[user_id % 5000] = 1  # Simulazione semplice

    # Proiezione con SVD
    user_embedding = model.transform(user_vector.reshape(1, -1))
    predictions = np.dot(user_embedding, model.components_).flatten()
    top_trips = trip_ids[np.argsort(predictions)[-5:]]  # Top 5

    # Risultati
    recommendations = [
        {"id": int(t), "destination": f"Dest_{t}", "price": float(np.random.rand() * user_input.budget)}
        for t in top_trips
    ]
    return {"recommendations": recommendations}
