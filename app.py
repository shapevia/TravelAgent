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

# Dati realistici con città e paesi abbinati
locations = [
    ('Positano', 'Italia'), ('Chamonix', 'Francia'), ('New York', 'USA'), ('Kyoto', 'Giappone'),
    ('Nairobi', 'Kenya'), ('Banff', 'Canada'), ('Barcellona', 'Spagna'), ('Santorini', 'Grecia'),
    ('Ubud', 'Indonesia'), ('Reykjavik', 'Islanda'), ('Dubrovnik', 'Croazia'), ('Siem Reap', 'Cambogia'),
    ('Cape Town', 'Sudafrica'), ('Queenstown', 'Nuova Zelanda'), ('Lisbona', 'Portogallo'),
    ('Phuket', 'Thailandia'), ('Cusco', 'Perù'), ('Amsterdam', 'Olanda'), ('Tulum', 'Messico'),
    ('Zermatt', 'Svizzera'), ('Marrakech', 'Marocco'), ('Praga', 'Repubblica Ceca'), ('Sydney', 'Australia')
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
foods = {
    'Italia': ['Pizza', 'Pasta', 'Gelato'], 'Francia': ['Croissant', 'Baguette', 'Formaggi'],
    'USA': ['Burger', 'BBQ', 'Pancakes'], 'Giappone': ['Sushi', 'Ramen', 'Tempura'],
    'Kenya': ['Nyama Choma', 'Ugali'], 'Canada': ['Poutine', 'Maple syrup'], 
    'Spagna': ['Paella', 'Tapas'], 'Grecia': ['Moussaka', 'Souvlaki'],
    'Indonesia': ['Nasi Goreng', 'Satay'], 'Islanda': ['Skyr', 'Pesce affumicato'],
    'Croazia': ['Peka', 'Frutti di mare'], 'Cambogia': ['Fish Amok', 'Lok Lak'],
    'Sudafrica': ['Braai', 'Biltong'], 'Nuova Zelanda': ['Pavlova', 'Lamb'],
    'Portogallo': ['Bacalhau', 'Pastéis de Nata'], 'Thailandia': ['Pad Thai', 'Tom Yum'],
    'Perù': ['Ceviche', 'Lomo Saltado'], 'Olanda': ['Stroopwafel', 'Herring'],
    'Messico': ['Tacos', 'Guacamole'], 'Svizzera': ['Fonduta', 'Cioccolata'],
    'Marocco': ['Tagine', 'Couscous'], 'Repubblica Ceca': ['Goulash', 'Trdelník'],
    'Australia': ['Vegemite', 'Meat Pie']
}
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
    return {"message": "Shapevia Travel Agent API - Realistico"}

async def generate_destination():
    city, country = random.choice(locations)
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
        'activities': list(set(dest_activities)),
        'country': country
    }

@app.post("/recommend")
async def recommend(preferences: UserPreferences):
    budget = preferences.budget
    interests = [interest.lower() for interest in preferences.interests]
    duration = preferences.duration or 7

    tasks = [generate_destination() for _ in range(10)]
    destinations = await asyncio.gather(*tasks)
    filtered_data = [d for d in destinations if 
                     d['price'] <= budget and 
                     d['duration_days'] <= duration and 
                     any(tag in interests for tag in d['tags'])]

    if not filtered_data:
        return {"recommendations": [], "message": "Nessuna opzione disponibile"}

    remaining_budget = budget
    days_left = duration
    recommendations = []
    plan = f"{random.choice(intros)}\n\n"
    day = 1

    random.shuffle(filtered_data)
    for dest in filtered_data:
        if remaining_budget < dest['price']
