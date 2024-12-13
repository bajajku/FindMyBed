import random
from typing import Tuple, List, Dict
from geopy.distance import distance as geopy_distance
import pandas as pd
from postalcodes_ca import postal_codes, fsa_codes

from utils.data_loader import DataLoader

import yaml

# Load the configuration from the YAML file.
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access the configuration values.
excel_path = config['EXCEL_PATH']

def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the geographic distance between two coordinates.

    Args:
        coord1 (Tuple[float, float]): The first coordinate (latitude, longitude).
        coord2 (Tuple[float, float]): The second coordinate (latitude, longitude).

    Returns:
        float: The distance in kilometers between the two coordinates.
    """
    return geopy_distance(coord1, coord2).kilometers

def select_fsa_by_rate(births_by_fsa: pd.DataFrame) -> str:
    """
    Select an FSA (Forward Sortation Area) based on birth rate probabilities.

    Args:
        births_by_fsa (pd.DataFrame): DataFrame containing FSA and BirthRate columns.

    Returns:
        str: The selected FSA code.
    """
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
    Generate a valid postal code for a given FSA and retrieve its coordinates.

    Args:
        births_by_fsa (pd.DataFrame): DataFrame containing FSA and BirthRate columns.

    Returns:
        Tuple[str, Tuple[float, float]]: The selected FSA and its coordinates (latitude, longitude).
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
    """
    Get the geographic center coordinates of a given FSA.

    Args:
        fsa_code (str): The FSA code.

    Returns:
        Tuple[float, float]: The latitude and longitude of the FSA center.
    """
    while True:
        # error happens only for the case when the fsa is J5N, put the manual output, will be edited
        if fsa_code=="J5N":
            return (45.764001, -73.811363)
        else:
            fsa_info = fsa_codes[fsa_code]
            if fsa_info:
                return float(fsa_info.latitude), float(fsa_info.longitude)

def get_hospital_coord(hospital_name: str)-> Tuple[float, float]:
    """
    Retrieve the geographic coordinates of a hospital by name.

    Args:
        hospital_name (str): The name of the hospital.

    Returns:
        Tuple[float, float]: The latitude and longitude of the hospital.
    """
    data_loader = DataLoader()
    data_loader.load_data(excel_file=excel_path)
    HOSPITALS = data_loader.create_hospitals()

    for hospital in HOSPITALS:
        if hospital.name == hospital_name:
            return hospital.geolocation

    return 0,0

def latlon_to_pixel(lat, lon, map_width, map_height, bounds):
    """
    Convert latitude and longitude into pixel coordinates for mapping purposes. 

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        map_width (int): The width of the map in pixels.
        map_height (int): The height of the map in pixels.
        bounds (Tuple[float, float, float, float]): The geographic bounds of the map (min_lat, max_lat, min_lon, max_lon).

    Returns:
        List[int]: Pixel coordinates [x, y].
    """
    min_lat, max_lat, min_lon, max_lon = bounds
    x = ((lon - min_lon) / (max_lon - min_lon) * map_width) + 340
    y = (max_lat - lat) / (max_lat - min_lat) * map_height + 22
    return [int(x), int(y)]