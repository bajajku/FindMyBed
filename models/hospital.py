
from typing import List, Tuple, Dict, Any
from models.patient import Patient
from utils.constants import *
import yaml

# Load YAML file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access the dictionary
intensive_threshold = config['INTENSIVE_OCCUPANCY_THRESHOLDS']
intermediate_threshold = config['INTERMEDIATE_OCCUPANCY_THRESHOLDS']



class Hospital:
    """
    Represents a hospital with various bed types, services, and patient admission logic.

    Attributes:
        name (str): The name of the hospital.
        geolocation (Tuple[float, float]): Latitude and longitude of the hospital.
        maternal_services (set): List of maternal care services provided.
        neonatal_services (set): List of neonatal care services provided.
        available_beds (List[int]):  List of available bed counts for various types.
        discharge_rates_intensive (float): Discharge rate for intensive care beds.
        discharge_rates_intermediate (float): Discharge rate for intermediate care beds.
        total_capacity (int): Total capacity of the hospital.
        total_capacity_intensive (int): Total capacity for intensive care beds.
        total_capacity_intermediate (int): Total capacity for intermediate care beds.
        birth_center_capacity (int): Capacity for birth center beds.
        antepartum_capacity (int): Capacity for antepartum beds.
        postpartum_capacity (int): Capacity for postpartum beds.
    """
    def __init__(self, name: str, geolocation: Tuple[float, float], 
                 maternal_services: List[str], neonatal_services: List[str],
                 available_beds: List[int],
                 discharge_rates_intensive: float,
                 discharge_rates_intermediate: float,
                 total_capacity: int, total_capacity_intensive: int,
                 total_capacity_intermediate: int,
                 birth_center_capacity: int = None,
                 antepartum_capacity: int = None,
                 postpartum_capacity: int = None,
                 hospital_occupancy_configuration: Dict[str, float] = None):
        self.name = name
        self.geolocation = geolocation
        self.maternal_services = set(maternal_services)  # Convert to set for O(1) lookups
        self.neonatal_services = set(neonatal_services) # Convert to set for O(1) lookups
        self.available_beds = available_beds # [intensive, intermediate, birthcenter, antepartum, postpartum]
        self.discharge_rates_intensive = discharge_rates_intensive
        self.discharge_rates_intermediate = discharge_rates_intermediate
        self.patients = {
            "Intensive": [], 
            "Intermediate": [], 
            "BirthCenter": [],
            "Antepartum": [],
            "Postpartum": []
        }
        self.total_capacity = total_capacity
        self.assigned_patients = 0
        self.total_capacity_intensive = total_capacity_intensive
        self.total_capacity_intermediate = total_capacity_intermediate
        self.overall_occupancy_rate = 0
        # self.prepopulate_patients()

        # Initialize maternal care beds
        self.birth_center_capacity = birth_center_capacity or 50
        self.antepartum_capacity = antepartum_capacity or 50
        self.postpartum_capacity = postpartum_capacity or 50
        self.hospital_occupancy_configuration = hospital_occupancy_configuration or {}

        self.BEDTYPE_INDEX = {"Intensive" : 0, "Intermediate" : 1, "BirthCenter" : 2, "Antepartum" : 3, "Postpartum" : 4}

    def get_hospital_services(self) -> List[str]:
        """
        Retrieves all services offered by the hospital.

        Returns:
            List[str]: Combined list of maternal and neonatal services.
        """      
        return list(self.maternal_services.union(self.neonatal_services))

    # REQUIRED
    def get_occupancy_rate_overall(self) -> float:
        """
        Calculates overall occupancy rate of the hospital
        Returns:
            float: Overall occupancy rate.
        """
        total_occupied = (
            (self.total_capacity_intensive - self.available_beds[0]) +
            (self.total_capacity_intermediate - self.available_beds[1]) +
            (self.birth_center_capacity - self.available_beds[2]) +
            (self.antepartum_capacity - self.available_beds[3]) +
            (self.postpartum_capacity - self.available_beds[4])

        )
        total_capacity = self.total_capacity_intensive + self.total_capacity_intermediate + self.birth_center_capacity + self.antepartum_capacity
        return (total_occupied / total_capacity)
    
    # REQUIRED
    def get_occupancy_rate(self, bedType: str) -> float:
        """
        Calculates the occupancy rate for a specific bed type.

        Args:
            bedType (str): The type of bed (e.g., "Intensive", "Intermediate").

        Returns:
            float: Occupancy rate for the specified bed type.
        """
        if bedType == "Intensive":
            return (self.total_capacity_intensive - self.available_beds[0]) / self.total_capacity_intensive
        elif bedType == "Intermediate":
            return (self.total_capacity_intermediate - self.available_beds[1]) / self.total_capacity_intermediate
        
        '''
        This part is for maternal care beds:

        elif bedType == "BirthCenter":
            return (self.birth_center_capacity - self.available_beds[2]) / self.birth_center_capacity
        elif bedType == "Antepartum":
            return (self.antepartum_capacity - self.available_beds[3]) / self.antepartum_capacity
        elif bedType == "Postpartum":
            return (self.postpartum_capacity - self.available_beds[4]) / self.postpartum_capacity
        '''
        return 0.0

    # REQUIRED
    def get_occupancy_rate_per_patientType_per_bedType(self, patient: Patient) -> bool:
        """
        Checks if occupancy rate thresholds allow admission for a specific patient type.

        Args:
            patient (Patient): The Patient instance.

        Returns:
            bool: Boolean indicating if admission is feasible.
        """
        CONDITION = 0.9
        if patient.patientType == "Neonatal":
            if patient.bedType == "Intensive":
                return self.get_occupancy_rate("Intensive") < self.hospital_occupancy_configuration.get("Intensive", 0.95)
            elif patient.bedType == "Intermediate":
                return self.get_occupancy_rate("Intermediate") < self.hospital_occupancy_configuration.get("Intermediate", 0.95)
        elif patient.patientType == "Maternal":
            # Get obstetrics rate (with fallback)
            birthcenter_rate = self.get_occupancy_rate("BirthCenter")
            antepartum_rate = self.get_occupancy_rate("Antepartum")
            # Need to consider both obstetrics and NICU rates
            if patient.bedType == "Intensive":
                nicu_rate = self.get_occupancy_rate("Intensive")
                return max(birthcenter_rate, antepartum_rate, nicu_rate) < self.hospital_occupancy_configuration.get("Intensive", 0.95)  
            elif patient.bedType == "Intermediate":
                nicu_rate = self.get_occupancy_rate("Intermediate")
                return max(birthcenter_rate, antepartum_rate, nicu_rate) < self.hospital_occupancy_configuration.get("Intermediate", 0.95)
            else:
                # Only need obstetrics rate
                return birthcenter_rate < CONDITION
        return False

    def get_capacity(self, bedType: str) -> int:
        """
        Gets the number of available beds for a given bed type.

        Args:
            bedType (str): Type of bed (e.g., "Intensive").

        Returns:
            int: Integer count of available beds.
        """
        return self.available_beds[0] if bedType == "Intensive" else self.available_beds[1]
    
    def get_discharge_rate(self, bedType: str) -> float:
        """
        Retrieves the discharge rate for a given bed type.

        Args:
            bedType (str): Type of bed (e.g., "Intensive").

        Returns:
            float: Float representing the discharge rate.
        """
        if bedType == "Intensive":
            return self.discharge_rates_intensive
        return self.discharge_rates_intermediate

        # REQUIRED
    def can_admit_patient(self, patient: Patient) -> bool:
        """
        Determines if the hospital can admit a patient based on their type and bed requirements.

        Args:
            patient (Patient): The Patient instance.

        Returns:
            bool: Boolean indicating if the patient can be admitted.
        """
        return self.get_occupancy_rate_per_patientType_per_bedType(patient=patient)

    def occupied_bed_summary(self):
        """
        Provides a summary of occupied beds and the occupancy percentage.

        Returns:
            Tuple[str, str]: Tuple containing a string summary of total occupied beds and percentage.
        """
        total_occupied = (self.total_capacity_intensive - self.available_beds[0]) + (self.total_capacity_intermediate - self.available_beds[1]) + (self.birth_center_capacity - self.available_beds[2]) + (self.antepartum_capacity - self.available_beds[3]) + (self.postpartum_capacity - self.available_beds[4])
        total_capacity = self.total_capacity_intensive + self.total_capacity_intermediate
        # Calculate overall occupancy percentage
        percentage = total_occupied / total_capacity
        # Return summary
        return f"{total_occupied}/{total_capacity} Occupied ", f"{percentage:.2f} %"

    # TODO: This method should be improved to handle different bed types
    def admit_patient(self, patient: Patient) -> bool:
        """
        Admits a patient to an appropriate bed if available.

        Args:
            patient (Patient): The Patient instance.

        Returns:
            bool: Boolean indicating if the patient was successfully admitted.
        """
        bed_index = 0 if patient.bedType == "Intensive" else 1
        if self.available_beds[bed_index] > 0:
            self.available_beds[bed_index] -= 1
            self.patients[patient.bedType].append(patient)
            patient.assignedHospital = self.name

            from utils.geographic import calculate_distance
            patient.distanceToHospital = calculate_distance(self.geolocation, patient.gpsPos)
            return True
        return False
