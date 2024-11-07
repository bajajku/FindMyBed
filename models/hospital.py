import random
from typing import List, Tuple
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
                 total_capacity_intermediate: int):
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
        self.prepopulate_patients()

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
            Calculates overall occupancy rate of the hospital, to check it is less than 90%
        """
        self.overall_occupancy_rate = (self.available_beds / self.total_capacity) * 100
        return self.overall_occupancy_rate
    
    def get_occupancy_rate(self, bedType: str) -> float:
        if bedType == "Intensive":
            return (self.total_capacity_intensive - self.available_beds[0])/self.total_capacity_intensive
        return (self.total_capacity_intermediate - self.available_beds[1])/self.total_capacity_intermediate

    def get_occupancy_rate_per_patientType_per_bedType(self, patient: Patient) -> float:
        if patient.patientType == "Neonatal":
            if patient.bedType == "Intensive":
                return # NICU_Intensive_Occupancy_Rate
            elif patient.bedType == "Intermmediate":
                return # NICU_Intermmediate_Occupancy_Rate
            
        elif patient.patientType == "Maternal":
            has_neonatal_needs = bool(set(patient.specialNeeds) & self.neonatal_services)
            if has_neonatal_needs:
                if patient.bedType == "Intensive":
                    return # Obsterics_Occupancy_rate + NICU_Intensive_Occupancy_Rate
                elif patient.bedType == "Intermmediate":
                    return # Obsterics_Occupancy_rate + NICU_Intermmediate_Occupancy_Rate
            else:
                return #  Obsterics only

    def get_capacity(self, bedType: str) -> int:
        return self.available_beds[0] if bedType == "Intensive" else self.available_beds[1]

    def get_discharge_rate(self, time_index: int, bedType: str) -> float:
        if bedType == "Intensive":
            return self.discharge_rates_intensive[time_index]
        return self.discharge_rates_intermediate[time_index]

    def admit_patient(self, patient: Patient) -> bool:
        bed_index = 0 if patient.bedType == "Intensive" else 1
        if self.available_beds[bed_index] > 0:
            self.available_beds[bed_index] -= 1
            self.patients[patient.bedType].append(patient)
            patient.assignedHospital = self.name
            return True
        return False
    
    def discharge_patients(self, time_index, arrivedDischarged):
        """ Discharge patients based on the discharge rate at the patient's arrival time """
        
        num_discharged_intensive = np.random.poisson(self.get_discharge_rate(time_index, "Intensive"))
        num_discharged_intermediate = np.random.poisson(self.get_discharge_rate(time_index, "Intermediate"))
        print(f"{num_discharged_intensive} {num_discharged_intermediate}")

        discharged_count = 0
        discharged_intensive = 0
        discharged_intermediate = 0

        # Process intensive care discharges
        for _ in range(min(num_discharged_intensive, len(self.patients["Intensive"]))):
            self.patients["Intensive"].pop()
            self.available_beds[0] += 1
            discharged_intensive += 1
            discharged_count += 1
            arrivedDischarged[self.name][1] += 1

        # Process intermediate care discharges
        for _ in range(min(num_discharged_intermediate, len(self.patients["Intermediate"]))):
            self.patients["Intermediate"].pop()
            self.available_beds[1] += 1
            discharged_intermediate += 1
            discharged_count += 1
            arrivedDischarged[self.name][1] += 1

        print(f"{self.name}: Discharged intensive: {discharged_intensive} intermediate: {discharged_intermediate} total: {discharged_count} patients at time {ARRIVAL_TIMES[time_index]}")
        return discharged_count

    def can_treat_patient(self, patient):
        if patient.patientType == 'Maternal':
            return bool(self.maternal_services & set(patient.specialNeeds))
        elif patient.patientType == 'Neonatal':
            return bool(self.neonatal_services & set(patient.specialNeeds))
        return False