import random
from typing import List, Tuple, Optional
from models.patient import Patient
import numpy as np
from utils.constants import *

class Hospital:
    def __init__(self, name: str, geolocation: Tuple[float, float], 
                 maternal_services: List[str], neonatal_services: List[str],
                 available_beds: List[int], discharge_rates: List[float],
                 discharge_rates_intensive: List[float],
                 discharge_rates_intermediate: List[float],
                 total_capacity: int, total_capacity_intensive: int,
                 total_capacity_intermediate: int,
                 birth_center_capacity: int = None,
                 antepartum_capacity: int = None,
                 postpartum_capacity: int = None):
        self.name = name
        self.geolocation = geolocation
        self.maternal_services = set(maternal_services)  # Convert to set for O(1) lookups
        self.neonatal_services = set(neonatal_services) # Convert to set for O(1) lookups
        self.available_beds = available_beds # [intensive, intermediate, birthcenter, antepartum, postpartum]
        self.discharge_rates = discharge_rates
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
        self.prepopulate_patients()

        # Initialize maternal care beds
        self.birth_center_capacity = birth_center_capacity or 50
        self.antepartum_capacity = antepartum_capacity or 50
        self.postpartum_capacity = postpartum_capacity or 50
        # self.birth_center_available = birth_center_capacity or 30
        # self.antepartum_available = antepartum_capacity or 30
        # self.postpartum_available = postpartum_capacity or 30

    def prepopulate_patients(self) -> None:
        occupied_beds_intensive = max(0, round(self.total_capacity_intensive - self.available_beds[0]))
        occupied_beds_intermediate = max(0, round(self.total_capacity_intermediate - self.available_beds[1]))

        # Create dummy patients for each bed type
        for bed_type, count in [("Intensive", occupied_beds_intensive), 
                              ("Intermediate", occupied_beds_intermediate)]:
            for _ in range(count):
                dummy_patient = Patient(
                    patientType=random.choice(PATIENT_TYPE),
                    gpsPos=self.geolocation,
                    bedType=bed_type,
                    del24HrPlus=False,
                    transportNeedCnt=0,
                    specialNeedType="None",
                    specialNeeds=["None"],
                    arrival_time=random.choice(ARRIVAL_TIMES)
                )
                self.patients[bed_type].append(dummy_patient)

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
    
    def nicu_required(self, patient: Patient) -> bool:
        """
        Check if a NICU bed is required for the patient
        """
        nicu_required = bool(set(patient.specialNeeds) & self.neonatal_services) or patient.patientType == "Neonatal"
        return nicu_required

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

    def get_discharge_rate(self, time_index: int, bedType: str) -> float:
        if bedType == "Intensive":
            return self.discharge_rates_intensive[time_index]
        return self.discharge_rates_intermediate[time_index]

    def can_admit_patient(self, patient: Patient) -> bool:

        if self.get_occupancy_rate_per_patientType_per_bedType(patient=patient):
            return True
        return False

    # this function should be in simulation.py, as Hospital class should only handle patient admissions and discharges.
    def admit_patient(self, patient: Patient) -> bool:
        if patient.patientType == "Maternal":
            # Handle maternal patient admission
            # might need to check if nicu_needed is true and if it then decrease nicu beds too.
            if not self.nicu_required(patient) and self.get_occupancy_rate_per_patientType_per_bedType(patient=patient) and not(patient.del24HrPlus) :
                self.available_beds[2] -= 1
                self.patients["BirthCenter"].append(patient)
                patient.assignedHospital = self.name
                return True
            elif not self.nicu_required(patient) and self.get_occupancy_rate_per_patientType_per_bedType(patient=patient) and patient.del24HrPlus:
                self.available_beds[3] -= 1
                self.patients["Antepartum"].append(patient)
                patient.assignedHospital = self.name
                return True
            
        else:
            # Handle NICU patient admission
            bed_index = 0 if patient.bedType == "Intensive" else 1
            if self.get_occupancy_rate_per_patientType_per_bedType(patient=patient) and patient.nicu_needed:
                self.available_beds[bed_index] -= 1
                self.patients[patient.bedType].append(patient)
                patient.assignedHospital = self.name
                return True
        return False
    
    # this function should be in simulation.py, as Hospital class should only handle patient admissions and discharges.
    def discharge_patients(self, time_index, arrivedDischarged):
        discharged_count = 0
        
        # NICU discharges
        num_discharged_intensive = np.random.poisson(self.get_discharge_rate(time_index, "Intensive"))
        num_discharged_intermediate = np.random.poisson(self.get_discharge_rate(time_index, "Intermediate"))
        
        # Maternal discharges (using similar rates for now)
        num_discharged_birthcenter = np.random.poisson(self.discharge_rates[time_index] * 0.3)
        num_discharged_antepartum = np.random.poisson(self.discharge_rates[time_index] * 0.3)
        num_discharged_postpartum = np.random.poisson(self.discharge_rates[time_index] * 0.3)
        
        # Process NICU discharges
        for bed_type, num_discharge, bed_index in [
            ("Intensive", num_discharged_intensive, 0),
            ("Intermediate", num_discharged_intermediate, 1)
        ]:
            for _ in range(min(num_discharge, len(self.patients[bed_type]))):
                self.patients[bed_type].pop()
                self.available_beds[bed_index] += 1
                discharged_count += 1
                arrivedDischarged[self.name][1] += 1
        
        # Process maternal discharges
        for bed_type, num_discharge, bed_index in [
            ("BirthCenter", num_discharged_birthcenter, 2),
            ("Antepartum", num_discharged_antepartum, 3),
            ("Postpartum", num_discharged_postpartum, 4)
        ]:
            for _ in range(min(num_discharge, len(self.patients[bed_type]))):
                self.patients[bed_type].pop()
                self.available_beds[bed_index] += 1
                discharged_count += 1
                arrivedDischarged[self.name][1] += 1
        
        print(f"{self.name}: Discharged {discharged_count} patients at time {ARRIVAL_TIMES[time_index]}")
        return discharged_count

