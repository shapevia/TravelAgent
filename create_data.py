import pandas as pd
import pickle

# Dati più realistici e dettagliati
data = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    'destination': [
        'Positano, Costiera Amalfitana', 'Chamonix, Alpi Francesi', 'New York City, USA', 
        'Kyoto, Giappone', 'Maasai Mara, Kenya', 'Banff National Park, Canada', 
        'Barcellona, Spagna', 'Santorini, Grecia', 'Bali, Indonesia', 
        'Reykjavik e Aurora Boreale, Islanda', 'Venezia, Italia', 'Cape Town, Sudafrica', 
        'Marrakech, Marocco', 'Queenstown, Nuova Zelanda', 'Lisbona, Portogallo'
    ],
    'price': [
        950, 1300, 1800, 1600, 2000, 1100, 850, 1200, 900, 
        1400, 700, 1500, 800, 1700, 750
    ],
    'duration_days': [
        5, 7, 6, 8, 10, 7, 4, 5, 7, 
        6, 3, 8, 5, 9, 4
    ],
    'tags': [
        ['spiaggia', 'relax', 'cibo'], ['montagna', 'avventura', 'natura'], ['città', 'cultura'], 
        ['cultura', 'cibo', 'relax'], ['avventura', 'natura', 'safari'], ['natura', 'montagna', 'relax'], 
        ['città', 'cultura', 'spiaggia'], ['spiaggia', 'relax', 'cultura'], ['spiaggia', 'natura', 'relax'], 
        ['natura', 'avventura', 'relax'], ['città', 'cultura'], ['città', 'natura', 'avventura'], 
        ['cultura', 'cibo'], ['avventura', 'montagna', 'natura'], ['città', 'cibo', 'cultura']
    ]
}

# Crea un DataFrame
travel_data = pd.DataFrame(data)

# Salva in travel_data.pkl
with open('travel_data.pkl', 'wb') as f:
    pickle.dump(travel_data, f)

print("Dataset aggiornato con successo!")