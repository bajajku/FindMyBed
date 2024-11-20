from geopy.distance import distance as geopy_distance
import random
from typing import Tuple, List, Dict
from geopy.geocoders import Nominatim
import pgeocode
import pandas as pd

def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    return geopy_distance(coord1, coord2).kilometers

def generate_nearby_coords(base_coords: Tuple[float, float], 
                         min_distance_km: float = 5,
                         max_distance_km: float = 30) -> Tuple[float, float]:
    random_distance = random.uniform(min_distance_km, max_distance_km)
    random_bearing = random.uniform(0, 360)
    destination = geopy_distance(kilometers=random_distance).destination(base_coords, random_bearing)
    return (destination.latitude, destination.longitude)

def generate_patient_coords(hospitals: List[Dict]) -> Tuple[float, float]:
    hospital_weights = [hospital["percentage"] for hospital in hospitals]
    selected_hospital = random.choices(hospitals, weights=hospital_weights, k=1)[0]
    return generate_nearby_coords(selected_hospital["coords"])

def select_fsa_by_rate(births_by_fsa: pd.DataFrame) -> str:
    """Select an FSA based on a Poisson distribution with a lambda defined by the birth ratio."""
    # Select a random FSA based on Poisson-distributed patient counts
    selected_fsa_row = births_by_fsa.sample(weights=births_by_fsa['BirthRate']).iloc[0]
    return selected_fsa_row['Postal Code (first 3 digits)']



def fsa_to_coordinates(births_by_fsa: pd.DataFrame) -> Tuple[float, float]:
    geolocator = pgeocode.Nominatim('ca')
    
    while True:
        selected_fsa = select_fsa_by_rate(births_by_fsa)    
        location = geolocator.query_postal_code(selected_fsa)
        
        # Check if the coordinates are valid (not NaN)
        if pd.notna(location.latitude) and pd.notna(location.longitude):
            return selected_fsa, (location.latitude, location.longitude)
        
        print("Invalid coordinates returned; selecting a new FSA.")