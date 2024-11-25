from geopy.distance import distance as geopy_distance
import random
from typing import Tuple, List, Dict
from geopy.geocoders import Nominatim
import pgeocode
import pandas as pd
import numpy as np

from config import EXCEL_PATH
from utils.data_loader import DataLoader

from postalcodes_ca import postal_codes, fsa_codes
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

def precompute_postal_codes() -> dict:
    """
    Precompute and cache all valid postal codes by FSA.
    Returns:
        dict: A dictionary where keys are FSAs and values are lists of full postal codes.
    """
    fsa_to_postal_codes = {}
    for code in postal_codes:
        fsa = code[:3]
        if fsa not in fsa_to_postal_codes:
            fsa_to_postal_codes[fsa] = []
        fsa_to_postal_codes[fsa].append(code)
    return fsa_to_postal_codes
# Precompute and store the dictionary globally for fast access
PRECOMPUTED_POSTAL_CODES = precompute_postal_codes()


def fsa_to_coordinates(births_by_fsa: pd.DataFrame) -> Tuple[str, Tuple[float, float]]:
    """
    Generate a valid postal code for a given FSA and retrieve its coordinates using postalcodes-ca.
    """

    while True:
        # Select an FSA based on birth rate
        selected_fsa = select_fsa_by_rate(births_by_fsa)

        # Retrieve all valid postal codes for the selected FSA
        valid_postal_codes = PRECOMPUTED_POSTAL_CODES.get(selected_fsa)
        if valid_postal_codes:  # Ensure the list is not empty
            # Select a random valid postal code
            full_postal_code = random.choice(valid_postal_codes)
            # Retrieve latitude and longitude
            postal_code_info = postal_codes.get(full_postal_code)
            if postal_code_info:  # Already validated during precomputation
                return selected_fsa, (postal_code_info.latitude, postal_code_info.longitude)

'''
def get_fsa_center(fsa_code: str) -> Tuple[float, float]:
    # Initialize geocode for Canadian postal codes
    geolocator = pgeocode.Nominatim("ca")

    while True:
        # Query the postal code
        location = geolocator.query_postal_code(fsa_code)

        # Check if location data is found and valid
        if location is not None and pd.notna(location.latitude) and pd.notna(location.longitude):
            return float(location.latitude), float(location.longitude)

        # If invalid, print message and retry
        print(f"No valid data found for FSA: {fsa_code}. Retrying...")
'''
def get_fsa_center(fsa_code: str) -> Tuple[float, float]:
    while True:
        # error happens only for the case when the fsa is J5N, put the manual output, will be edited
        if fsa_code=="J5N":
            return (45.764001, -73.811363)
        else:
            fsa_info = fsa_codes[fsa_code]
            if fsa_info:
                return float(fsa_info.latitude), float(fsa_info.longitude)

def get_hospital_coord(hospital_name: str)-> Tuple[float, float]:
    data_loader = DataLoader()
    data_loader.load_data(excel_file=EXCEL_PATH)
    HOSPITALS = data_loader.create_hospitals()

    for hospital in HOSPITALS:
        if hospital.name == hospital_name:
            return hospital.geolocation

    return 0,0