import pandas as pd
import pickle

# Dati di esempio
data = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'destination': ['Spiaggia di Capri', 'Dolomiti', 'Roma', 'Firenze', 'Safari Kenya', 
                    'Parco Yosemite', 'Parigi', 'Costiera Amalfi', 'Tokyo', 'Santorini'],
    'price': [800, 1200, 600, 700, 1500, 900, 850, 950, 2000, 1100],
    'duration_days': [5, 7, 3, 4, 10, 6, 5, 4, 8, 7],
    'tags': [['spiaggia', 'relax'], ['montagna', 'avventura'], ['città', 'cultura'], 
             ['città', 'cultura'], ['avventura', 'natura'], ['natura', 'avventura'], 
             ['città', 'cultura'], ['spiaggia', 'relax'], ['città', 'cibo'], ['spiaggia', 'relax']]
}

# Crea un DataFrame
travel_data = pd.DataFrame(data)

# Salva in travel_data.pkl
with open('travel_data.pkl', 'wb') as f:
    pickle.dump(travel_data, f)

print("Dataset creato con successo!")