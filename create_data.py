import pandas as pd
import pickle

data = {
    'id': list(range(1, 21)),
    'destination': [
        'Positano, Italia', 'Chamonix, Francia', 'New York, USA', 'Kyoto, Giappone', 
        'Maasai Mara, Kenya', 'Banff, Canada', 'Barcellona, Spagna', 'Santorini, Grecia', 
        'Bali, Indonesia', 'Reykjavik, Islanda', 'Dubrovnik, Croazia', 'Siem Reap, Cambogia', 
        'Cape Town, Sudafrica', 'Queenstown, Nuova Zelanda', 'Lisbona, Portogallo', 
        'Phuket, Thailandia', 'Machu Picchu, Perù', 'Amsterdam, Olanda', 
        'Tulum, Messico', 'Zermatt, Svizzera'
    ],
    'price': [
        950, 1300, 1800, 1600, 2000, 1100, 850, 1200, 900, 1400, 
        800, 700, 1500, 1700, 750, 850, 1400, 900, 1000, 1600
    ],
    'duration_days': [
        5, 7, 6, 8, 10, 7, 4, 5, 7, 6, 
        4, 5, 7, 9, 4, 5, 7, 4, 6, 8
    ],
    'tags': [
        ['spiaggia', 'relax', 'cibo'], ['montagna', 'avventura', 'sci'], ['città', 'cultura', 'shopping'], 
        ['cultura', 'cibo', 'tempio'], ['avventura', 'natura', 'safari'], ['natura', 'montagna', 'escursioni'], 
        ['città', 'spiaggia', 'arte'], ['spiaggia', 'relax', 'tramonti'], ['spiaggia', 'natura', 'yoga'], 
        ['natura', 'avventura', 'aurora'], ['spiaggia', 'cultura', 'storia'], ['cultura', 'tempio', 'natura'], 
        ['città', 'natura', 'avventura'], ['avventura', 'montagna', 'natura'], ['città', 'cibo', 'cultura'], 
        ['spiaggia', 'relax', 'feste'], ['montagna', 'cultura', 'avventura'], ['città', 'cultura', 'canali'], 
        ['spiaggia', 'relax', 'rovine'], ['montagna', 'sci', 'relax']
    ],
    'activities': [
        ['Gita in barca', 'Cena sul mare', 'Shopping locali'], ['Sci alpino', 'Escursione Monte Bianco', 'Fonduta'], 
        ['Tour Broadway', 'Shopping 5th Ave', 'Vista Empire State'], ['Visita templi', 'Cerimonia del tè', 'Passeggiata nei giardini'], 
        ['Safari jeep', 'Campo tendato', 'Tramonto nella savana'], ['Trekking', 'Canoa sul lago', 'Bagno termale'], 
        ['Sagrada Familia', 'Spiaggia Barceloneta', 'Tapas tour'], ['Tour Oia', 'Bagno termale', 'Tramonto a Fira'], 
        ['Templi Uluwatu', 'Yoga', 'Mercato di Ubud'], ['Tour Golden Circle', 'Caccia aurora', 'Laguna Blu'], 
        ['Mura medievali', 'Kayak sul mare', 'Cena croata'], ['Angkor Wat', 'Mercato notturno', 'Villaggi galleggianti'], 
        ['Table Mountain', 'Safari breve', 'Vino a Stellenbosch'], ['Bungee jumping', 'Jet boat', 'Trekking'], 
        ['Tram 28', 'Pasteis de Nata', 'Belém Tower'], ['Snorkeling', 'Massaggio thai', 'Mercato galleggiante'], 
        ['Trekking Inca Trail', 'Visita rovine', 'Mercato Pisac'], ['Giro in bici', 'Canali', 'Museo Van Gogh'], 
        ['Rovine Maya', 'Cenote swimming', 'Spiaggia'], ['Sci sul Matterhorn', 'Cioccolata calda', 'Trekking']
    ]
}

travel_data = pd.DataFrame(data)
with open('travel_data.pkl', 'wb') as f:
    pickle.dump(travel_data, f)

print("Dataset espanso con successo!")