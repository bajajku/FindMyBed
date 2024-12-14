import numpy as np
import pandas as pd
from typing import List, Tuple
import ast
from models.hospital import Hospital
import random

class DataLoader:
    """
    A class to load, parse, and process data for hospitals and patients.

    Attributes:
        hospital_names (List[str]): List of hospital names.
        coordinates (List[Tuple[float, float]]): List of hospital geolocations as tuples of latitude and longitude.
        maternal_services (List[List[str]]): List of maternal services available at each hospital.
        neonatal_services (List[List[str]]): List of neonatal services available at each hospital.
        beds_available (List[List[int]]): List of available beds by bed type for each hospital.
        discharge_rates_intensive (List[float]): Discharge rates for intensive care beds.
        discharge_rates_intermediate (List[float]): Discharge rates for intermediate care beds.
        total_capacity (List[int]): Total bed capacity of each hospital.
        total_capacity_intensive (List[int]): Intensive care bed capacity of each hospital.
        total_capacity_intermediate (List[int]): Intermediate care bed capacity of each hospital.
        birth_rates_by_fsa (pd.DataFrame): Birth rate data categorized by Forward Sortation Area (FSA).
    """
    def __init__(self):
        """
        Initialize the DataLoader with empty attributes for hospital and patient data.
        """
        self.hospital_names = None
        self.coordinates = None
        self.maternal_services = None
        self.neonatal_services = None
        self.beds_available = None
        self.discharge_rates_intensive = None 
        self.discharge_rates_intermediate = None
        self.total_capacity = None
        self.total_capacity_intensive = None
        self.total_capacity_intermediate = None
        self.birth_rates_by_fsa = None
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
        """
        Splits a comma-separated string into a list of services.
        Args:
            services_str (str): Comma-separated string of services.

        Returns:
            List[str]: List of services.       
        """
        return [service.strip() for service in services_str.split(',')]

    @staticmethod
    def parse_coordinates(coord_str: str) -> Tuple[float, float]:
        """
        Parses a string representing geographic coordinates into a tuple of floats.

        Args:
            coord_str (str): Comma-separated string of coordinates.

        Returns:
            Tuple[float, float]: Latitude and longitude as floats.
        """
        return tuple(map(float, coord_str.split(',')))

    def load_data(self, excel_file: str) -> List[Hospital]:
        """
        Loads hospital data from an Excel file and creates a list of Hospital instances.

        Args:
            excel_file (str): Path to the Excel file containing hospital data.
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
        self.admissions_per_hour = df['admissions_transported_per_hour'].tolist()
        self.average_admissions = sum(self.admissions_per_hour)
        discharge_rates_intensive = df['Discharge rate intensive'].tolist()
        discharge_rates_intermediate = df['Discharge rate intermediate'].tolist()

        #extended the available beds list to accommodate other bed types
        for i in range(len(self.hospital_names)):
            self.beds_available[i].extend([50,50,50])
        # Scale down discharge rates for intensive and intermediate
        scaling_factor_intensive = 0.19
        scaling_factor_intermediate = 0.09
        self.discharge_rates_intensive = [
            (rate * scaling_factor_intensive) for rate in discharge_rates_intensive
        ]
        self.discharge_rates_intermediate = [
            (rate * scaling_factor_intermediate) for rate in discharge_rates_intermediate
        ]

        self.intensive_rate = df['Bed Type Rate Intensive'].sum()
        self.intermediate_rate = df['Bed Type Rate Intermediate'].sum()

    def create_hospitals(self):
        """
        Creates a list of Hospital instances using the loaded data.

        Returns:
            List[Hospital]: A list of initialized Hospital instances.
        """
        hospitals = [
            Hospital(
                name=self.hospital_names[i],
                geolocation=self.coordinates[i],
                maternal_services=self.maternal_services[i],
                neonatal_services=self.neonatal_services[i],
                available_beds=self.beds_available[i],
                discharge_rates_intensive=self.discharge_rates_intensive[i],
                discharge_rates_intermediate=self.discharge_rates_intermediate[i],
                total_capacity=self.total_capacity[i],
                total_capacity_intensive=self.total_capacity_intensive[i],
                total_capacity_intermediate=self.total_capacity_intermediate[i]
            ) for i in range(len(self.hospital_names))
        ]
        return hospitals

    def get_average_admissions(self):
        """
        Gets the average number of admissions per hour.

        Returns:
            float: Average admissions per hour.
        """
        return self.average_admissions

    # To reflect the ratio of intensive and intermediate bed types
    def assign_bed_type_poisson(self):
        """
        Assigns a bed type.

        Returns:
            str: Assigned bed type ("Intensive" or "Intermediate").
        """
        rand_num = random.random()
        if rand_num <= self.intensive_rate:
            return 'Intensive'
        else:
            return 'Intermediate'
        
    def calculate_birth_rates_by_fsa(self, excel_file: str) -> pd.DataFrame:
        """
        Loads and processes birth rate data by FSA (Forward Sortation Area) from Excel sheets.

        Args:
            excel_file (str): Path to the Excel file.

        Returns:
            pd.DataFrame: DataFrame containing FSA, total births, and birth ratios.
        """
        # Load and combine data from specified sheets
        sheets_to_load = ['2021-01-11 to 2021-12-31', '2022-10-01 to 2022-12-31', '2023-01-01 to 2023-12-31']
        excel_data = pd.read_excel(excel_file, sheet_name=sheets_to_load, header=1)

        # Combine all sheets into a single DataFrame
        combined_data = pd.concat(excel_data.values(), ignore_index=True)
        # Rename hospital codes in 'firstSiteCode'
        rename_map = {
            'MUHC': 'CUSM',
            'HSJ': 'CHU-SJ',
            'MRH': 'HMR',
            'JGH': 'HGJ'
        }
        # Rename the hospital codes in 'firstSiteCode'
        if 'firstSiteCode' in combined_data.columns:  # Check if the column exists
            combined_data['firstSiteCode'] = combined_data['firstSiteCode'].replace(rename_map)

        # Ensure 'NumberOfBirths' is numeric and handle any missing values
        combined_data['NumberOfBirths'] = pd.to_numeric(combined_data['NumberOfBirths'], errors='coerce').fillna(0)

        # Extract the FSA and calculate total births by FSA
        combined_data['FSA'] = combined_data['PostalCode'].str[:3]
        births_by_fsa = combined_data.groupby('FSA')['NumberOfBirths'].sum().reset_index()
        births_by_fsa.columns = ['FSA', 'TotalBirths']
        total_births = births_by_fsa['TotalBirths'].sum()
        births_by_fsa['BirthRate'] = births_by_fsa['TotalBirths'] / total_births

        return births_by_fsa