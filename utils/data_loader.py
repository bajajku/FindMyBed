from itertools import count

import numpy as np
import pandas as pd
from typing import List, Tuple
import ast

from config import EXCEL_PATH
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
        self.admissions_per_hour = df['admissions_per_hour'].tolist()
        self.average_admissions = sum(self.admissions_per_hour)

        self.discharge_rates = self.parse_into_list_of_lists(df['Discharge rate'])
        discharge_rates_intensive = df['Discharge rate intensive'].tolist()
        discharge_rates_intermediate = df['Discharge rate intermediate'].tolist()

        # Scale down discharge rates for intensive and intermediate
        scaling_factor = 0.3
        self.discharge_rates_intensive = [
            (rate * scaling_factor) for rate in discharge_rates_intensive
        ]
        self.discharge_rates_intermediate = [
            (rate * scaling_factor) for rate in discharge_rates_intermediate
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
                discharge_rates_intensive=self.discharge_rates_intensive[i],
                discharge_rates_intermediate=self.discharge_rates_intermediate[i],
                total_capacity=self.total_capacity[i],
                total_capacity_intensive=self.total_capacity_intensive[i],
                total_capacity_intermediate=self.total_capacity_intermediate[i]
            ) for i in range(len(self.hospital_names))
        ]
        return hospitals

    def get_average_admissions(self):
        return self.average_admissions

    def calculate_birth_rates_by_fsa(self, excel_file: str) -> pd.DataFrame:
        """
        Loads and processes birth rate data by FSA (Forward Sortation Area) from Excel sheets.

        Args:
            excel_file (str): Path to the Excel file.

        Returns:
            pd.DataFrame: DataFrame containing FSA, total births, and birth ratios.
        """
        # Load and combine data from specified sheets
        sheets_to_load = ['All birth 2017', 'Year 2018', 'Year 2019', 'Year 2020', 'Year 2021', 'Year 2022',
                          'Year 2023']
        excel_data = pd.read_excel(excel_file, sheet_name=sheets_to_load)

        # Combine all sheets into a single DataFrame
        combined_data = pd.concat(excel_data.values(), ignore_index=True)

        # Step 1: Keep only relevant columns and drop rows with empty postal codes
        combined_data = combined_data[['Postal Code (first 3 digits)', 'Date of Birth (YY-MM)']].dropna(
            subset=['Postal Code (first 3 digits)'])

        # Step 2: Count the number of births per postal code
        births_by_fsa = combined_data['Postal Code (first 3 digits)'].value_counts().reset_index()
        births_by_fsa.columns = ['Postal Code (first 3 digits)', 'BirthCount']

        # Step 3: Calculate total population based on non-empty entries
        total_population = births_by_fsa.shape[0]  # Total number of non-empty rows

        # Step 4: Calculate birth rate per postal code
        births_by_fsa['BirthRate'] = (births_by_fsa['BirthCount'] / total_population)

        return births_by_fsa