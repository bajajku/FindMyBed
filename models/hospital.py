import random
from typing import List, Tuple
from models.patient import Patient
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
