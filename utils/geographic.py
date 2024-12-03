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

def select_fsa_by_rate(births_by_fsa: pd.DataFrame) -> str:
    """Select an FSA based on a Poisson distribution with a lambda defined by the birth ratio."""
    # Select a random FSA based on Poisson-distributed patient counts
    selected_fsa_row = births_by_fsa.sample(weights=births_by_fsa['BirthRate']).iloc[0]
    return selected_fsa_row['FSA']

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

def latlon_to_pixel(lat, lon, map_width, map_height, bounds):
    min_lat, max_lat, min_lon, max_lon = bounds
    x = ((lon - min_lon) / (max_lon - min_lon) * map_width) + 340
    y = (max_lat - lat) / (max_lat - min_lat) * map_height + 22
    return [int(x), int(y)]