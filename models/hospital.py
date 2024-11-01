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
        self.maternal_services = maternal_services
        self.neonatal_services = neonatal_services
        self.available_beds = available_beds
        self.discharge_rates = discharge_rates
        self.discharge_rates_intensive = discharge_rates_intensive
        self.discharge_rates_intermediate = discharge_rates_intermediate
        self.patients = []
        self.total_capacity = total_capacity
        self.assigned_patients = 0
        self.total_capacity_intensive = total_capacity_intensive
        self.total_capacity_intermediate = total_capacity_intermediate
        self.prepopulate_patients()

    def prepopulate_patients(self) -> None:
        occupied_beds_intensive = round(self.total_capacity_intensive - self.available_beds[0])
        occupied_beds_intermediate = round(self.total_capacity_intermediate - self.available_beds[1])
        
        occupied_beds_intensive = max(0, occupied_beds_intensive)
        occupied_beds_intermediate = max(0, occupied_beds_intermediate)

        # Create dummy patients for both types of beds
        for bed_type, count in [("Intensive", occupied_beds_intensive), 
                              ("Intermediate", occupied_beds_intermediate)]:
            for _ in range(count):
                self.patients.append(
                    Patient(
                        patientType=random.choice(PATIENT_TYPE),
                        gpsPos=self.geolocation,
                        bedType=bed_type,
                        del24HrPlus=False,
                        transportNeedCnt=0,
                        specialNeedType="None",
                        specialNeeds=["None"],
                        arrival_time=random.choice(ARRIVAL_TIMES)
                    )
                )

    def get_occupancy_rate(self, bedType: str) -> float:
        if bedType == "Intensive":
            return (self.total_capacity_intensive - self.available_beds[0])/self.total_capacity_intensive
        return (self.total_capacity_intermediate - self.available_beds[1])/self.total_capacity_intermediate

    def get_capacity(self, bedType: str) -> int:
        return self.available_beds[0] if bedType == "Intensive" else self.available_beds[1]

    def get_discharge_rate(self, time_index: int, bedType: str) -> float:
        if bedType == "Intensive":
            return self.discharge_rates_intensive[time_index]
        return self.discharge_rates_intermediate[time_index]

    def admit_patient(self, patient: Patient) -> bool:
        if patient.bedType == "Intensive" and self.available_beds[0] > 0:
            self.available_beds[0] -= 1
            self.patients.append(patient)
            patient.assignedHospital = self.name
            return True
        elif patient.bedType == "Intermediate" and self.available_beds[1] > 0:
            self.available_beds[1] -= 1
            self.patients.append(patient)
            patient.assignedHospital = self.name
            return True
        return False
    
    def discharge_patients(self, time_index, arrivedDischarged):
        """ Discharge patients based on the discharge rate at the patient's arrival time """
 
        # Determine the number of patients to discharge for each bed type
        num_discharged_intensive = np.random.poisson(self.get_discharge_rate(time_index, "Intensive"))
        num_discharged_intermediate = np.random.poisson(self.get_discharge_rate(time_index, "Intermediate"))
        print(f"{num_discharged_intensive} {num_discharged_intermediate}")
 
        # Discharge intensive care patients
        discharged_count = 0
        discharged_count_intensive = 0
        discharged_count_intermediate = 0
        for _ in range(num_discharged_intensive):
            if not self.patients:  # Check if the patient list is empty
                break
            for i, patient in enumerate(self.patients):
                if patient.bedType == "Intensive":
                    self.patients.pop(i)
                    self.available_beds[0] += 1
                    arrivedDischarged[self.name][1] += 1
                    discharged_count += 1
                    discharged_count_intensive += 1
                    break  # Exit inner loop to find the next matching patient
 
        # Discharge intermediate care patients
        for _ in range(num_discharged_intermediate):
            if not self.patients:  # Check if the patient list is empty
                break
            for i, patient in enumerate(self.patients):
                if patient.bedType == "Intermediate":
                    self.patients.pop(i)
                    self.available_beds[1] += 1
                    arrivedDischarged[self.name][1] += 1
                    discharged_count += 1
                    discharged_count_intermediate += 1
                    break  # Exit inner loop to find the next matching patie
 
        # Print results for discharged patients
        print(f"{self.name}: Discharged intensive: {discharged_count_intensive} intermediate: {discharged_count_intermediate}  total: {discharged_count} patients at time {ARRIVAL_TIMES[time_index]}")
 
        return discharged_count  # Total discharged for both types
 
    def can_treat_patient(self, patient):
        if patient.patientType == 'Maternal':
            return any(special_need in self.maternal_services for special_need in patient.specialNeeds)
        elif patient.patientType == 'Neonatal':
            return any(special_need in self.neonatal_services for special_need in patient.specialNeeds)
        return False
