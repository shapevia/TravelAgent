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

OPENWEATHER_API_KEY = 'd03c9fb597c1b76387c444d9843a86ba'  # Sostituisci con la tua chiave OpenWeatherMap

base_activities = {
    'spiaggia': ['Gita in barca', 'Snorkeling', 'Nuoto con delfini', 'Pesca al tramonto'],
    'montagna': ['Trekking', 'Arrampicata', 'Mountain bike', 'Picnic panoramico'],
    'città': ['Tour a piedi', 'Shopping nei mercati', 'Visita a gallerie d’arte', 'Cena panoramica'],
    'cultura': ['Visita a siti archeologici', 'Lezione di danza locale', 'Tour dei musei', 'Laboratorio artigianale'],
    'natura': ['Escursione nella giungla', 'Birdwatching', 'Kayak nei fiumi', 'Campeggio sotto le stelle'],
    'avventura': ['Zip-line', 'Paracadutismo', 'Safari in jeep', 'Immersioni subacquee'],
    'relax': ['Giornata in spa', 'Meditazione al tramonto', 'Lettura in riva al mare', 'Bagno termale'],
    'cibo': ['Degustazione di vini', 'Tour gastronomico', 'Corso di cucina locale', 'Cena con chef stellato']
}
transports = ['Volo diretto', 'Treno ad alta velocità', 'Noleggio auto', 'Traghetto panoramico', 'Bus turistico']
all_tags = list(base_activities.keys())
foods = {
    'Honduras': ['Baleadas', 'Sopa de Caracol', 'Tamales', 'Plátanos fritos'],
    'Italy': ['Pizza Margherita', 'Spaghetti alla carbonara', 'Tiramisù'],
    'France': ['Croque Monsieur', 'Ratatouille', 'Crêpes Suzette'],
    'United States': ['New York Cheesecake', 'Southern BBQ Ribs', 'Apple Pie'],
    'Japan': ['Sushi nigiri', 'Ramen tonkotsu', 'Tempura di gamberi'],
    'Kenya': ['Nyama Choma', 'Ugali con sukuma', 'Chapati'],
    'Canada': ['Poutine', 'Tourtière', 'Butter Tarts'],
    'Spain': ['Paella valenciana', 'Jamón ibérico', 'Churros con cioccolato'],
    'Greece': ['Moussaka', 'Souvlaki', 'Baklava'],
    'Indonesia': ['Nasi Goreng', 'Satay di pollo', 'Rendang'],
    'Iceland': ['Hákarl', 'Skyr con mirtilli', 'Pesce affumicato'],
    'Croatia': ['Peka di polpo', 'Ćevapi', 'Strukli'],
    'Cambodia': ['Fish Amok', 'Lok Lak', 'Num Banh Chok'],
    'South Africa': ['Bobotie', 'Biltong', 'Malva Pudding'],
    'New Zealand': ['Hangi', 'Pavlova', 'Agnello arrosto'],
    'Portugal': ['Bacalhau à Brás', 'Pastéis de Nata', 'Caldo Verde'],
    'Thailand': ['Pad Thai', 'Tom Yum Goong', 'Mango Sticky Rice'],
    'Peru': ['Ceviche', 'Lomo Saltado', 'Pisco Sour'],
    'Netherlands': ['Stroopwafel', 'Haring crudo', 'Erwtensoep'],
    'Mexico': ['Tacos al pastor', 'Mole poblano', 'Chiles en nogada'],
    'Switzerland': ['Fonduta di formaggio', 'Rösti', 'Cioccolata svizzera'],
    'Morocco': ['Tagine di agnello', 'Couscous con verdure', 'Harira'],
    'Czech Republic': ['Svíčková', 'Trdelník', 'Guláš'],
    'Australia': ['Meat Pie', 'Vegemite su toast', 'Lamingtons']
}
country_traits = {
    'Honduras': ['spiaggia', 'natura', 'cultura', 'cibo'],
    'Italy': ['città', 'cultura', 'cibo', 'relax'],
    'France': ['città', 'cultura', 'cibo', 'relax'],
    'United States': ['città', 'avventura', 'natura', 'cibo'],
    'Japan': ['città', 'cultura', 'cibo', 'natura'],
    'Kenya': ['natura', 'avventura', 'cultura'],
    'Canada': ['natura', 'montagna', 'avventura'],
    'Spain': ['spiaggia', 'città', 'cultura', 'cibo'],
    'Greece': ['spiaggia', 'cultura', 'relax', 'cibo'],
    'Indonesia': ['spiaggia', 'natura', 'avventura', 'cibo'],
    'Iceland': ['natura', 'avventura', 'relax'],
    'Croatia': ['spiaggia', 'cultura', 'cibo'],
    'Cambodia': ['cultura', 'natura', 'cibo'],
    'South Africa': ['natura', 'avventura', 'cibo'],
    'New Zealand': ['natura', 'avventura', 'montagna'],
    'Portugal': ['spiaggia', 'cultura', 'cibo'],
    'Thailand': ['spiaggia', 'cultura', 'cibo', 'avventura'],
    'Peru': ['natura', 'cultura', 'avventura', 'cibo'],
    'Netherlands': ['città', 'cultura', 'cibo'],
    'Mexico': ['spiaggia', 'cultura', 'cibo', 'avventura'],
    'Switzerland': ['montagna', 'relax', 'cibo'],
    'Morocco': ['cultura', 'natura', 'cibo'],
    'Czech Republic': ['città', 'cultura', 'cibo'],
    'Australia': ['spiaggia', 'natura', 'avventura']
}

intros = [
    "Preparati per un viaggio indimenticabile con Shapevia!",
    "Ho ideato un itinerario che ti lascerà senza parole!",
    "Ecco la tua avventura su misura, pronta a partire!"
]
day_starts = [
    "Giorno {day}: un’esperienza unica ti aspetta",
    "Il {day}° giorno: scopri qualcosa di speciale",
    "Day {day}: una giornata tutta da vivere"
]
transitions = [
    "Poi, parti alla volta di",
    "Il tuo viaggio continua verso",
    "Successiva tappa:"
]
outros = [
    "Ti piace? Possiamo partire quando vuoi!",
    "Cosa ne dici? È il tuo viaggio ideale?",
    "Pronto a fare le valigie con Shapevia?"
]
extras = [
    "Non perderti i colori del tramonto!",
    "Un momento perfetto per ricaricare le energie.",
    "Scatta una foto da ricordare!",
    "Lasciati sorprendere dai dettagli locali.",
    "Un’esperienza che non dimenticherai."
]

countries_cache = []
user_history = {}  # {user_id: {'interests': [], 'weights': {tag: peso}}}

async def fetch_countries():
    global countries_cache
    if not countries_cache:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://restcountries.com/v3.1/all') as response:
                if response.status == 200:
                    countries_cache = await response.json()
    return countries_cache

async def fetch_weather(city):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric', timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return f"{data['weather'][0]['description'].capitalize()}, {int(data['main']['temp'])}°C"
                return "Meteo non disponibile"
        except asyncio.TimeoutError:
            return "Meteo non disponibile (timeout)"

@app.get("/")
def read_root():
    return {"message": "Shapevia Travel Agent API - ML Avanzato con Meteo e Cibo"}

async def generate_destination(interests, budget, duration, user_id):
    countries = await fetch_countries()
    if not countries:
        return None
    
    country = random.choice(countries)
    city = country.get('capital', [''])[0] or country['name']['common']
    country_name = country['name']['common']
    valid_tags = country_traits.get(country_name, all_tags)
    dest_tags = random.sample(valid_tags, min(random.randint(1, 3), len(valid_tags)))
    if interests:
        dest_tags.append(random.choice(interests))
    if user_id in user_history and user_history[user_id]['interests']:
        past_interests = user_history[user_id]['interests']
        weights = user_history[user_id]['weights']
        weighted_tags = [tag for tag, w in weights.items() for _ in range(int(w * 10))]  # Peso influenza probabilità
        if weighted_tags:
            dest_tags.append(random.choice(weighted_tags))
    dest_tags = list(set(dest_tags))
    dest_activities = []
    for tag in dest_tags:
        if tag in base_activities:
            dest_activities.extend(random.sample(base_activities[tag], min(2, len(base_activities[tag]))))
    price = random.randint(200, min(1000, int(budget)))
    days = random.randint(3, min(10, duration or 7))
    weather = await fetch_weather(city)
    return {
        'destination': f"{city}, {country_name}",
        'price': price,
        'duration_days': days,
        'tags': dest_tags,
        'activities': list(set(dest_activities)),
        'country': country_name,
        'weather': weather
    }

@app.post("/recommend")
async def recommend(preferences: UserPreferences):
    budget = preferences.budget
    interests = [interest.lower() for interest in preferences.interests]
    duration = preferences.duration or 7
    user_id = preferences.user_id

    # Aggiorna la history dell'utente
    if user_id not in user_history:
        user_history[user_id] = {'interests': [], 'weights': {}}
    user_history[user_id]['interests'].extend(interests)
    user_history[user_id]['interests'] = list(set(user_history[user_id]['interests']))[:5]
    for interest in interests:
        user_history[user_id]['weights'][interest] = user_history[user_id]['weights'].get(interest, 0) + 0.2  # Incrementa peso

    tasks = [generate_destination(interests, budget, duration, user_id) for _ in range(20)]
    destinations = await asyncio.gather(*tasks)
    destinations = [d for d in destinations if d is not None]

    if not destinations:
        return {"recommendations": [], "plan": "Problema con i dati esterni. Riprova più tardi!"}

    tag_vectors = {tag: np.random.rand(10) for tag in all_tags}
    user_vector = np.zeros(10)
    for interest in interests + user_history[user_id]['interests']:
        if interest in tag_vectors:
            weight = user_history[user_id]['weights'].get(interest, 1.0)
            user_vector += tag_vectors[interest] * weight
    user_vector = user_vector / (len(interests + user_history[user_id]['interests']) or 1)

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
    used_extras = set()
    used_foods = set()

    for dest in filtered_data[:3]:  # Limita a 3 destinazioni
        if remaining_budget < dest['price'] or days_left < 1:
            break

        dest_days = min(random.randint(2, dest['duration_days']), days_left)
        transport = random.choice(transports)
        recommendations.append({
            "id": random.randint(1000, 9999),
            "destination": dest['destination'],
            "price": float(dest['price']),
            "duration_days": int(dest['duration_days']),
            "activities": dest['activities'],
            "weather": dest['weather'],
            "country": dest['country']
        })

        if len(recommendations) > 1:
            plan += f"{random.choice(transitions)} {dest['destination']} con {transport}.\n"
        else:
            plan += f"Arrivo a {dest['destination']} con {transport}.\n"

        for d in range(dest_days):
            activity = random.choice(dest['activities'])
            available_foods = [f for f in foods.get(dest['country'], ['Piatto tipico']) if f not in used_foods]
            food = random.choice(available_foods) if available_foods else "Piatto tipico"
            used_foods.add(food)
            available_extras = [e for e in extras if e not in used_extras]
            extra = random.choice(available_extras) if available_extras else ""
            if extra:
                used_extras.add(extra)
            plan += f"{random.choice(day_starts).format(day=day)}: {activity} a {dest['destination']}. Cena con {food}. Meteo: {dest['weather']}. {extra}\n"
            day += 1
            days_left -= 1

        remaining_budget -= dest['price']

    if days_left > 0 and recommendations:
        last_dest = recommendations[-1]['destination']
        last_country = recommendations[-1]['country']
        last_weather = recommendations[-1]['weather']
        while days_left > 0: