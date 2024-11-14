import random
from typing import List, Tuple, Optional, Dict, Any
from models.patient import Patient
import numpy as np
from utils.constants import *

class Hospital:
    def __init__(self, name: str, geolocation: Tuple[float, float], 
                 maternal_services: List[str], neonatal_services: List[str],
                 available_beds: List[int], discharge_rates: List[float],
                 discharge_rates_intensive: float,
                 discharge_rates_intermediate: float,
                 total_capacity: int, total_capacity_intensive: int,
                 total_capacity_intermediate: int,
                 obstetrics_capacity: int = None,
                 obstetrics_available_beds: int = None):
        self.name = name
        self.geolocation = geolocation
        self.maternal_services = set(maternal_services)  # Convert to set for O(1) lookups
        self.neonatal_services = set(neonatal_services) # Convert to set for O(1) lookups
        self.available_beds = available_beds
        self.discharge_rates = discharge_rates
        self.discharge_rates_intensive = discharge_rates_intensive
        self.discharge_rates_intermediate = discharge_rates_intermediate
        self.patients = {"Intensive": [], "Intermediate": [], "Obstetrics": []}
        self.total_capacity = total_capacity
        self.assigned_patients = 0
        self.total_capacity_intensive = total_capacity_intensive
        self.total_capacity_intermediate = total_capacity_intermediate
        self.overall_occupancy_rate = 0

        # Initialize obstetrics-specific attributes if provided
        if obstetrics_capacity is not None and obstetrics_available_beds is not None:
            self.obstetrics_capacity = obstetrics_capacity
            self.obstetrics_available_beds = obstetrics_available_beds

    def prepopulate_patients(self) -> dict[str, list[Any]]:
        occupied_beds_intensive = round(self.total_capacity_intensive - self.available_beds[0])
        occupied_beds_intermediate = round(self.total_capacity_intermediate - self.available_beds[1])

        occupied_beds_intensive = max(0, occupied_beds_intensive)
        occupied_beds_intermediate = max(0, occupied_beds_intermediate)

        # Create dummy patients for both types of beds
        for bed_type, count in [("Intensive", occupied_beds_intensive),
                                ("Intermediate", occupied_beds_intermediate)]:
            for _ in range(count):
                patient = Patient(
                        patientType=random.choice(PATIENT_TYPE),
                        gpsPos=self.geolocation,
                        postalCode="None",
                        bedType=bed_type,
                        del24HrPlus=False,
                        transportNeedCnt=0,
                        specialNeedType="None",
                        specialNeeds=["None"],
                        arrival_time=random.choice(ARRIVAL_TIMES),
                        aniGpsPos=[600, 50],
                        arrived_at_hospital=True,  # Track if the patient has reached the hospital
                        queue_position=0,  # Initialize queue position
                        discharged=False,
                        assignedHospital=self.name
                    )
                self.patients[patient.bedType].append(patient)
        return self.patients

    def get_occupancy_rate_overall(self) -> float:
        """
        Calculates overall occupancy rate of the hospital
        """
        total_occupied = (
            (self.total_capacity_intensive - self.available_beds[0]) +
            (self.total_capacity_intermediate - self.available_beds[1])
        )
        total_capacity = self.total_capacity_intensive + self.total_capacity_intermediate
        return (total_occupied / total_capacity) * 100
    
    def get_occupancy_rate(self, bedType: str) -> float:
        if bedType == "Intensive":
            return (self.total_capacity_intensive - self.available_beds[0])/self.total_capacity_intensive
        return (self.total_capacity_intermediate - self.available_beds[1])/self.total_capacity_intermediate

    def get_total_capacity(self):
        return f"{self.total_capacity - (self.available_beds[0] + self.available_beds[1])}/{self.total_capacity} occupied"

    def get_occupancy_rate_per_patientType_per_bedType(self, patient: Patient) -> Optional[float]:
        """
        Calculate specialized occupancy rates based on patient type and bed requirements.
        Returns appropriate occupancy rate or None if requirements can't be met.
        """
        if patient.patientType == "Neonatal":
            # For NICU cases
            if patient.bedType == "Intensive":
                return self.get_occupancy_rate("Intensive")
            elif patient.bedType == "Intermediate":
                return self.get_occupancy_rate("Intermediate")
            
        elif patient.patientType == "Maternal":
            has_neonatal_needs = bool(set(patient.specialNeeds) & self.neonatal_services)
            
            # Get obstetrics rate (with fallback)
            obstetrics_rate = (self.get_obstetrics_occupancy_rate() 
                              if hasattr(self, 'obstetrics_capacity') 
                              else self.get_occupancy_rate(patient.bedType))
            
            if has_neonatal_needs:
                # Need to consider both obstetrics and NICU rates
                if patient.bedType == "Intensive":
                    nicu_rate = self.get_occupancy_rate("Intensive")
                    return max(obstetrics_rate, nicu_rate)
                elif patient.bedType == "Intermediate":
                    nicu_rate = self.get_occupancy_rate("Intermediate")
                    return max(obstetrics_rate, nicu_rate)
            else:
                # Only need obstetrics rate
                return obstetrics_rate
            
        return None

    def get_obstetrics_occupancy_rate(self) -> float:
        """
        Calculate obstetrics-specific occupancy rate.
        This method should be implemented when obstetrics data becomes available.
        """
        if hasattr(self, 'obstetrics_capacity') and hasattr(self, 'obstetrics_available_beds'):
            return (self.obstetrics_capacity - self.obstetrics_available_beds) / self.obstetrics_capacity
        return None

    def get_capacity(self, bedType: str) -> int:
        return self.available_beds[0] if bedType == "Intensive" else self.available_beds[1]

    def get_discharge_rate(self, bedType: str) -> float:
        if bedType == "Intensive":
            return self.discharge_rates_intensive
        return self.discharge_rates_intermediate


    def admit_patient(self, patient: Patient) -> bool:
        bed_index = 0 if patient.bedType == "Intensive" else 1
        if self.available_beds[bed_index] > 0:
            self.available_beds[bed_index] -= 1
            self.patients[patient.bedType].append(patient)
            patient.assignedHospital = self.name
            return True
        return False

    def discharge_patients(self, arrivedDischarged):
        """ Discharge patients based on the discharge rate at the patient's arrival time """

        num_discharged_intensive = np.random.poisson(self.get_discharge_rate("Intensive"))
        num_discharged_intermediate = np.random.poisson(self.get_discharge_rate("Intermediate"))
        print(f"{num_discharged_intensive} {num_discharged_intermediate}")

        discharged_count = 0
        discharged_intensive = 0
        discharged_intermediate = 0

        # Process intensive care discharges
        for _ in range(min(num_discharged_intensive, len(self.patients["Intensive"]))):
            self.patients["Intensive"][0].discharged = True
            self.patients["Intensive"].pop(0)
            self.available_beds[0] += 1
            discharged_intensive += 1
            discharged_count += 1
            arrivedDischarged[self.name][1] += 1

        # Process intermediate care discharges
        for _ in range(min(num_discharged_intermediate, len(self.patients["Intermediate"]))):
            self.patients["Intermediate"][0].discharged = True
            self.patients["Intermediate"].pop(0)
            self.available_beds[1] += 1
            discharged_intermediate += 1
            discharged_count += 1
            arrivedDischarged[self.name][1] += 1

        print(
            f"{self.name}: Discharged intensive: {discharged_intensive} intermediate: {discharged_intermediate} total: {discharged_count} patients ")
        return discharged_count


    def can_treat_patient(self, patient):
        if patient.patientType == 'Maternal':
            return bool(self.maternal_services & set(patient.specialNeeds))
        elif patient.patientType == 'Neonatal':
            return bool(self.neonatal_services & set(patient.specialNeeds))
        return False