import pandas as pd
import pickle

data = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'destination': [
        'Positano, Italia', 'Chamonix, Francia', 'New York, USA', 
        'Kyoto, Giappone', 'Maasai Mara, Kenya', 'Banff, Canada', 
        'Barcellona, Spagna', 'Santorini, Grecia', 'Bali, Indonesia', 
        'Reykjavik, Islanda'
    ],
    'price': [950, 1300, 1800, 1600, 2000, 1100, 850, 1200, 900, 1400],
    'duration_days': [5, 7, 6, 8, 10, 7, 4, 5, 7, 6],
    'tags': [
        ['spiaggia', 'relax', 'cibo'], ['montagna', 'avventura', 'sci'], ['città', 'cultura', 'shopping'], 
        ['cultura', 'cibo', 'tempio'], ['avventura', 'natura', 'safari'], ['natura', 'montagna', 'escursioni'], 
        ['città', 'spiaggia', 'arte'], ['spiaggia', 'relax', 'tramonti'], ['spiaggia', 'natura', 'yoga'], 
        ['natura', 'avventura', 'aurora']
    ],
    'activities': [
        ['Gita in barca', 'Cena sul mare'], ['Sci alpino', 'Escursione Monte Bianco'], ['Tour Broadway', 'Shopping 5th Ave'], 
        ['Visita templi', 'Cerimonia del tè'], ['Safari jeep', 'Campo tendato'], ['Trekking', 'Canoa sul lago'], 
        ['Sagrada Familia', 'Spiaggia Barceloneta'], ['Tour Oia', 'Bagno termale'], ['Templi Uluwatu', 'Yoga'], 
        ['Tour Golden Circle', 'Caccia aurora']
    ]
}

travel_data = pd.DataFrame(data)
with open('travel_data.pkl', 'wb') as f:
    pickle.dump(travel_data, f)

print("Dataset aggiornato con attività!")