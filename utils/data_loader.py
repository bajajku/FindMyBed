from itertools import count

import numpy as np
import pandas as pd
from typing import List, Tuple
import ast
from models.hospital import Hospital

class DataLoader:

    def __init__(self):
        self.arrival_rates = None
        self.hospital_names = None
        self.coordinates = None
        self.maternal_services = None
        self.neonatal_services = None
        self.beds_available = None
        self.discharge_rates = None
        self.discharge_rates_intensive = None 
        self.discharge_rates_intermediate = None
        self.total_capacity = None
        self.otal_capacity_intensive = None 
        self.total_capacity_intermediate = None

    @staticmethod
    def parse_into_list_of_lists(df_col: pd.Series) -> List[List[float]]:
        """
        Parses a Pandas Series column with stringified lists into a list of lists.
        Safely evaluates each string as a Python list using `ast.literal_eval`.

        Args:
            df_col (pd.Series): Series column with stringified lists.

        Returns:
            List[List[float]]: List of lists containing the parsed data.
        """
        parsed_list = []
        for i in df_col:
            try:
                _list = ast.literal_eval(i)
                parsed_list.append(_list)
            except (SyntaxError, ValueError):
                print(f"Could not parse occupancy rate string: {i}")
                parsed_list.append([])
        return parsed_list

    @staticmethod
    def parse_services(services_str: str) -> List[str]:
        """Splits a comma-separated string into a list of services."""
        return [service.strip() for service in services_str.split(',')]

    @staticmethod
    def parse_coordinates(coord_str: str) -> Tuple[float, float]:
        """Parses a comma-separated string into a tuple of floats representing coordinates."""
        return tuple(map(float, coord_str.split(',')))

    def load_data(self, excel_file: str) -> List[Hospital]:
        """
        Loads hospital data from an Excel file and creates a list of Hospital instances.

        Args:
            excel_file (str): Path to the Excel file containing hospital data.

        Returns:
            Loads data into the class
        """
        # Load data
        df = pd.read_excel(excel_file)

        # Apply transformations
        df['Hospital Coordinates'] = df['Hospital Coordinates'].apply(self.parse_coordinates)
        df['Maternal Services'] = df['Maternal Services'].apply(self.parse_services)
        df['Neonatal Services'] = df['Neonatal Services'].apply(self.parse_services)

        # Extract columns and transform data as needed
        self.hospital_names = df['Hospital Name'].tolist()
        self.coordinates = df['Hospital Coordinates'].tolist()
        self.maternal_services = df['Maternal Services'].tolist()
        self.neonatal_services = df['Neonatal Services'].tolist()
        self.beds_available = self.parse_into_list_of_lists(df['beds_available'])
        for i in range(len(self.beds_available)):
            for j in range(len(self.beds_available[i])):
                self.beds_available[i][j] = np.random.poisson(self.beds_available[i][j])
        self.total_capacity = df['total_capacity'].tolist()
        self.total_capacity_intensive = df['total_capacity_intensive'].tolist()
        self.total_capacity_intermediate = df['total_capacity_intermediate'].tolist()
        self.avg_beds_available_per_type_ = self.parse_into_list_of_lists(df['average_beds'])
        self.admissions_per_hour = df['admissions_per_hour'].tolist()
        self.average_admissions = sum(self.admissions_per_hour)

        self.discharge_rates = self.parse_into_list_of_lists(df['Discharge rate'])
        discharge_rates_intensive = self.parse_into_list_of_lists(df['Discharge rate intensive'])
        discharge_rates_intermediate = self.parse_into_list_of_lists(df['Discharge rate intermediate'])

        # Scale down discharge rates for intensive and intermediate
        scaling_factor = 0.3
        self.discharge_rates_intensive = [
            [rate * scaling_factor for rate in row] for row in discharge_rates_intensive
        ]
        self.discharge_rates_intermediate = [
            [rate * scaling_factor for rate in row] for row in discharge_rates_intermediate
        ]

        arrival_rates = self.parse_into_list_of_lists(df['Arrival rate'])
        self.arrival_rates = [sum(x) for x in arrival_rates]

    def create_hospitals(self):
        # Create Hospital objects
        hospitals = [
            Hospital(
                name=self.hospital_names[i],
                geolocation=self.coordinates[i],
                maternal_services=self.maternal_services[i],
                neonatal_services=self.neonatal_services[i],
                available_beds=self.beds_available[i],
                discharge_rates= sum(self.discharge_rates[i])/len(self.discharge_rates[i]),
                discharge_rates_intensive=(sum(self.discharge_rates_intensive[i])/len(self.discharge_rates_intensive[i]))/8,
                discharge_rates_intermediate=(sum(self.discharge_rates_intermediate[i])/len(self.discharge_rates_intermediate[i]))/8,
                total_capacity=self.total_capacity[i],
                total_capacity_intensive=self.total_capacity_intensive[i],
                total_capacity_intermediate=self.total_capacity_intermediate[i]
            ) for i in range(len(self.hospital_names))
        ]

        return hospitals

    def get_average_admissions(self):
        return self.average_admissions