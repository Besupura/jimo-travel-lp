
"""
Creates mock data for testing the ETL pipeline.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

data = {
    'source': ['nln', 'okinawa_od', 'osm', 'google', 'osm'],
    'name': ['Shuri Castle', 'Churaumi Aquarium', 'Katsuren Castle Ruins', 'Cape Manzamo', 'Nakagusuku Castle Ruins'],
    'category': ['historic', 'aquarium', 'historic', 'natural', 'historic'],
    'address': ['1-2 Shurikinjocho, Naha, Okinawa 903-0815', '424 Ishikawa, Motobu, Okinawa 905-0206', 'Katsuren, Uruma, Okinawa', 'Onna, Kunigami District, Okinawa', 'Nakagusuku, Nakagami District, Okinawa'],
    'latitude': [26.2173, 26.6939, 26.3314, 26.5044, 26.2128],
    'longitude': [127.7190, 127.8781, 127.8775, 127.8459, 127.7927],
    'summary': ['Historic Ryukyu Kingdom castle', 'One of Japan\'s largest aquariums', 'UNESCO World Heritage castle ruins', 'Scenic cliff shaped like an elephant trunk', 'UNESCO World Heritage castle ruins'],
    'opening_hours': ['8:30-19:00', '8:30-18:30', '9:00-18:00', '24 hours', '9:00-18:00'],
    'popularity_histogram': ['Monday: 9:10,10:20,11:40,12:60,13:80,14:90,15:70,16:50,17:30', '', '', 'Saturday: 9:30,10:50,11:70,12:90,13:100,14:80,15:60,16:40', '']
}

df = pd.DataFrame(data)

OUTPUT_DIR = Path("data/interim")
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(OUTPUT_DIR / "05_popular_times_spots.csv", index=False)

print('Mock data created successfully.')
