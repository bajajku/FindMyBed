from geopy.distance import distance as geopy_distance
import random
from typing import Tuple, List, Dict

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