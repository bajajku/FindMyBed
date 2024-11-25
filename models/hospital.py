import random
from typing import List, Tuple, Optional, Dict, Any
from models.patient import Patient
import numpy as np
from utils.constants import *

class Hospital:
    def __init__(self, name: str, geolocation: Tuple[float, float], 
                 maternal_services: List[str], neonatal_services: List[str],
                 available_beds: List[int],
                 discharge_rates_intensive: float,
                 discharge_rates_intermediate: float,
                 total_capacity: int, total_capacity_intensive: int,
                 total_capacity_intermediate: int,
                 birth_center_capacity: int = None,
                 transfer_percentage = None,
                 antepartum_capacity: int = None,
                 postpartum_capacity: int = None):
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
        self.transfer_percentage = transfer_percentage
        self.assigned_patients = 0
        self.total_capacity_intensive = total_capacity_intensive
        self.total_capacity_intermediate = total_capacity_intermediate
        self.overall_occupancy_rate = 0
        # self.prepopulate_patients()

        # Initialize maternal care beds
        self.birth_center_capacity = birth_center_capacity or 50
        self.antepartum_capacity = antepartum_capacity or 50
        self.postpartum_capacity = postpartum_capacity or 50


    # REQUIRED
    def get_occupancy_rate_overall(self) -> float:
        """
        Calculates overall occupancy rate of the hospital
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
        Calculate occupancy rate for a specific bed type
        """
        if bedType == "Intensive":
            return (self.total_capacity_intensive - self.available_beds[0]) / self.total_capacity_intensive
        elif bedType == "Intermediate":
            return (self.total_capacity_intermediate - self.available_beds[1]) / self.total_capacity_intermediate
        elif bedType == "BirthCenter":
            return (self.birth_center_capacity - self.available_beds[2]) / self.birth_center_capacity
        elif bedType == "Antepartum":
            return (self.antepartum_capacity - self.available_beds[3]) / self.antepartum_capacity
        elif bedType == "Postpartum":
            return (self.postpartum_capacity - self.available_beds[4]) / self.postpartum_capacity
        return 0.0
    
    # REQUIRED
    def nicu_required(self, patient: Patient) -> bool:
        """
        Check if a NICU bed is required for the patient
        """
        nicu_required = bool(set(patient.specialNeeds) & self.neonatal_services) or patient.patientType == "Neonatal"
        return nicu_required

    # REQUIRED
    def get_occupancy_rate_per_patientType_per_bedType(self, patient: Patient) -> bool:
        """
        Calculate specialized occupancy rates based on patient type and bed requirements.
        Returns appropriate occupancy rate or None if requirements can't be met.
        """
        CONDITION = 0.9
        if patient.patientType == "Neonatal":
            # For NICU cases
            if patient.bedType == "Intensive":
                return self.get_occupancy_rate("Intensive") < CONDITION
            elif patient.bedType == "Intermediate":
                return self.get_occupancy_rate("Intermediate") < CONDITION
            
        elif patient.patientType == "Maternal":
            has_neonatal_needs = self.nicu_required(patient)
            
            # Get obstetrics rate (with fallback)
            birthcenter_rate = self.get_occupancy_rate("BirthCenter")
            antepartum_rate = self.get_occupancy_rate("Antepartum")
            
            if has_neonatal_needs:
                # Need to consider both obstetrics and NICU rates
                if patient.bedType == "Intensive":
                    nicu_rate = self.get_occupancy_rate("Intensive")
                    return max(birthcenter_rate, antepartum_rate, nicu_rate) < CONDITION
                elif patient.bedType == "Intermediate":
                    nicu_rate = self.get_occupancy_rate("Intermediate")
                    return max(birthcenter_rate, antepartum_rate, nicu_rate) < CONDITION
            else:
                # Only need obstetrics rate
                return birthcenter_rate < CONDITION
            
        return False


    def get_capacity(self, bedType: str) -> int:
        return self.available_beds[0] if bedType == "Intensive" else self.available_beds[1]
    
    
    def get_discharge_rate(self, bedType: str) -> float:
        if bedType == "Intensive":
            return self.discharge_rates_intensive
        return self.discharge_rates_intermediate

        # REQUIRED
    def can_admit_patient(self, patient: Patient) -> bool:

        if self.get_occupancy_rate_per_patientType_per_bedType(patient=patient):
            return True
        return False

    def occupied_bed_summary(self):
        total_occupied = (self.total_capacity_intensive - self.available_beds[0]) + (self.total_capacity_intermediate - self.available_beds[1]) + (self.birth_center_capacity - self.available_beds[2]) + (self.antepartum_capacity - self.available_beds[3]) + (self.postpartum_capacity - self.available_beds[4])
        total_capacity = self.total_capacity_intensive + self.total_capacity_intermediate
        return f"{total_occupied}/{total_capacity} occupied"

    def admit_patient(self, patient: Patient) -> bool:
        bed_index = 0 if patient.bedType == "Intensive" else 1
        if self.available_beds[bed_index] > 0:
            self.available_beds[bed_index] -= 1
            self.patients[patient.bedType].append(patient)
            patient.assignedHospital = self.name
            return True
        return False