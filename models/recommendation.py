from typing import List, Optional

import numpy as np
from transitions import Machine
from models.patient import Patient
from models.hospital import Hospital
from utils.constants import *
from utils.geographic import calculate_distance
import logging

class HospitalRecommendation:
    """
    A state machine for hospital recommendations based on patient needs and hospital availability.
    """
    
    states = [
        'input',
        'condition_check',
        'discharge_patients',
        'service_determination',
        'bed_type_check',
        'geographic_check',
        'transport_needs_check',
        'hospital_recommendation'
    ]

    def __init__(self, hospitals: List[Hospital]):
        """
        Initialize the recommendation system.
        
        Args:
            hospitals: List of Hospital objects to consider for recommendations
        """
        self.patient: Optional[Patient] = None
        self.hospitals = hospitals
        self.available_hospitals: List[Hospital] = []
        self.selected_hospital: Optional[Hospital] = None
        self.queue: List[Patient] = []
        
        # Initialize state machine
        self.machine = Machine(
            model=self,
            states=HospitalRecommendation.states,
            initial='input'
        )
        
        # Define transitions
        self.machine.add_transition(
            trigger='process_input',
            source='input',
            dest='condition_check',
            after='apply_restrictions'
        )

        # Define transitions
        self.machine.add_transition(
            trigger='check_conditions',
            source='condition_check',
            dest='service_determination',
            after=['home_hospital_check', 'determine_services']
        )

        self.machine.add_transition(
            trigger='determine_service',
            source='service_determination',
            dest='bed_type_check',
            after='filter_bed_type'
        )
        self.machine.add_transition(
            trigger='check_bed_type',
            source='bed_type_check',
            dest='geographic_check',
            after='filter_by_distance'
        )
        self.machine.add_transition(
            trigger='check_geographic_distance',
            source='geographic_check',
            dest='hospital_recommendation',
            after='recommend_hospital'
        )
        self.machine.add_transition(
            trigger='restart',
            source='hospital_recommendation',
            dest='input'
        )
    def apply_restrictions(self) -> None:
        """Filter hospitals based on service availability and occupancy rate."""
        condition2_services = ["Neurology", "Cardiology"]
        condition3_services = [ "General Surgery", "Genetic","Gastroenterology","Plastic Surgery","Respirology"]

        # Helper checks
        is_prematurity_ga_lt_26 = "Prematurity (GA<26 weeks)" in self.patient.specialNeeds
        has_condition2_services = any(service in self.patient.specialNeeds for service in condition2_services)
        has_condition3_services = any(service in self.patient.specialNeeds for service in condition3_services)


        # TODO: Fix this. This is a temporary fix to avoid the error.
        '''For now I have added hasattr check for postalCode, as patient doesn't have postalCode attribute.
        so this is just a temporary check to avoid the error. This will be updated once the patient class is updated.
        '''
        # Condition 1: Indigenous patients
        if hasattr(self.patient, "postalCode") and self.patient.postalCode == "J0M":
            self.available_hospitals = [
                hospital for hospital in self.hospitals if hospital.name == "CUSM"
            ]
            self.patient.condition = 1

        # Condition 2: Major anomaly AND cardiac OR neuro
        elif has_condition2_services:
            valid_hospitals = ["CUSM", "CHU-SJ", "CHUQ"]
            self.available_hospitals = [
                hospital for hospital in self.hospitals if hospital.name in valid_hospitals
            ]
            self.patient.condition = 2

        # Condition 3: Major anomaly BUT not condition 2 or prematurity
#        elif not has_condition2_services and not is_prematurity_ga_lt_26:
        elif has_condition3_services:
            valid_hospitals = ["CUSM", "CHU-SJ", "CHUQ", "CHUS"]
            self.available_hospitals = [
                hospital for hospital in self.hospitals if hospital.name in valid_hospitals
            ]
            self.patient.condition = 3

        # Condition 4: Prematurity (GA<26 weeks)
        elif is_prematurity_ga_lt_26:
            valid_hospitals = ["CUSM", "CHU-SJ", "HGJ", "CHUQ", "CHUS"]
            self.available_hospitals = [
                hospital for hospital in self.hospitals if hospital.name in valid_hospitals
            ]
            self.patient.condition = 4

        # Condition 5
        else:
            valid_hospitals = ["CUSM", "CHU-SJ", "HGJ", "CHUQ", "CHUS", "HMR"]
            self.available_hospitals = [
                hospital for hospital in self.hospitals if hospital.name in valid_hospitals
            ]
            self.patient.condition = 5
        print(f"Filtered hospitals based on restriction conditions : {[h.name for h in self.available_hospitals]}")


    def find_nearest_and_best_occupancy_hospitals(self) -> None:
        """
        Find the nearest hospital to the patient and update the patient's nearest hospital attribute.
        """
        if not self.available_hospitals:
            logging.warning("No available hospitals to determine the nearest or best occupancy hospital.")
            return
        # Sort available hospitals by distance
        self.available_hospitals.sort(
            key=lambda hospital: calculate_distance(
                hospital.geolocation,
                self.patient.gpsPos
            )
        )
        # Set the nearest hospital
        nearest_hospital = self.available_hospitals[0]
        self.patient.nearestHospital = nearest_hospital.name

        # Find the hospital with the best (lowest) occupancy rate
        best_occupancy_hospital = min(
            self.available_hospitals,
            key=lambda hospital: hospital.get_occupancy_rate(self.patient.bedType)
        )
        self.patient.bestOccupancyHospital = best_occupancy_hospital.name

    def discharge_all_patients(self, arrived_discharged: dict) -> None:
        """
        Discharge patients from all hospitals at a given arrival time.

        Args:
            arrived_discharged: Dictionary tracking patient movement
        """
        logging.info("Discharging patients from all hospitals...")

        for hospital in self.hospitals:
            hospital.discharge_patients(arrived_discharged)

    def home_hospital_check(self) -> None:
        """
        Adds Patient's Home Hospital in hospital's list if Applicable.
        """
        if not self.patient or not self.patient.homeHospital:
            return
        home_hospital = next((h for h in self.hospitals if h.name == self.patient.homeHospital), None)
        if home_hospital and home_hospital not in self.available_hospitals:
            self.available_hospitals.append(home_hospital)
        print(f"Patient's preferred hospital added to Available Hospital List: {self.patient.homeHospital}")

    def determine_services(self) -> None:
        """
        Filter hospitals based on service availability and occupancy rate.
        """
        if not self.patient:
            return

        self.available_hospitals = [
            hospital for hospital in self.available_hospitals 
            if hospital.can_admit_patient(self.patient) and 
               all(need in hospital.get_hospital_services() for need in self.patient.specialNeedType)
        ]
        self.find_nearest_and_best_occupancy_hospitals()     
        print(f"Filtered hospitals based on services and occupancy: {[h.name for h in self.available_hospitals]}")

    def filter_bed_type(self) -> None:
        """
        Filter hospitals based on bed type availability.
        """
        if not self.available_hospitals or not self.patient:
            return

        print(f"Filtering hospitals by bed type: {self.patient.bedType}")
        
        self.available_hospitals = [
            hospital for hospital in self.available_hospitals
            if hospital.get_capacity(self.patient.bedType) > 1
        ]

    def filter_by_distance(self) -> None:
        """
        Sort hospitals by distance to patient location.
        """
        if not self.available_hospitals or not self.patient:
            return

        print(f"Sorting hospitals by distance from patient at {self.patient.gpsPos}")
        
        self.available_hospitals.sort(
            key=lambda hospital: calculate_distance(
                hospital.geolocation,
                self.patient.gpsPos
            )
        )

        print(f"Sorted hospitals by distance: "
                    f"{[hospital.name for hospital in self.available_hospitals]}")

    def get_top_hospitals(self) -> List[Hospital]:
        """
        Get top 3 hospitals based on specified criteria and sorting logic.
        
        Returns:
            List[Hospital]: Up to 3 most suitable hospitals, sorted by priority
        """
        if not self.patient:
            return []
        if not self.available_hospitals:
            return []
        
        available_hospitals_copy = self.available_hospitals[:]
        
        if self.patient.homeHospital:
            home_hospital = next((h for h in available_hospitals_copy if h.name == self.patient.homeHospital), None)
            if home_hospital:
                preferred_hospitals = [home_hospital]
                available_hospitals_copy.remove(home_hospital)
                preferred_hospitals += available_hospitals_copy[:2]
                print(f"Patient's preferred hospital removed from Available Hospital List: {self.patient.homeHospital}")
            else:
                preferred_hospitals = available_hospitals_copy[:3]
            return preferred_hospitals
        preferred_hospitals = available_hospitals_copy[:3]

        # Return top 3 choices
        return preferred_hospitals

    def recommend_hospital(self) -> None:
        """
        Recommend and assign the most suitable hospital or queue the patient.
        """
        if not self.patient:
            return
        recommended_hospitals = self.get_top_hospitals()
        if not recommended_hospitals:
            self.queue.append(self.patient)
            logging.warning("No suitable hospitals found. Patient added to queue.")
            return
            
        # For simulation compatibility, try to assign to first recommended hospital
        self.selected_hospital = recommended_hospitals[0]
        success = self.selected_hospital.admit_patient(self.patient)
        
        if success:
            self.selected_hospital.assigned_patients += 1
            print(f"Patient assigned to {self.selected_hospital.name}")
        else:
            self.queue.append(self.patient)
            logging.warning("Admission failed. Patient added to queue.")


    '''
    This function is used to get the top hospital recommendations,
    for a given patient without admitting them.
    Serves as a helper function for the API endpoint.
    '''
    def get_hospital_recommendations(self, patient: Patient) -> List[Hospital]:
        """
        Retrieve top hospital recommendations for a given patient without admitting them.
        
        Args:
            patient: The patient object to process
        
        Returns:
            List[Hospital]: Top recommended hospitals for the patient
        """
        self.patient = patient
        print("\nGenerating hospital recommendations for the patient...\n")
        
        # Perform the recommendation steps up to geographic distance check
        self.process_input()
        self.check_conditions()
        self.determine_service()
        self.check_bed_type()
        self.check_geographic_distance()
        
        # Get the top hospital recommendations
        recommendations = self.get_top_hospitals()
        self.restart()

        print(f"Top hospital recommendations: {[h.name for h in recommendations]}")
        return recommendations
    
    '''
    This function is used to run the complete hospital recommendation process for a patient.
    It Admits the patient to the hospital if a suitable one is found, otherwise queues the patient.
    Queue management is not implemented in the current version.
    Serves as a helper function for the Simulation system.
    '''
    def run(self, patient: Patient) -> None:
        """
        Run the complete hospital recommendation process for a patient.
        
        Args:
            patient: Patient object to process
        """
        self.patient = patient
        print("\nProcessing new patient...\n")
        # Execute state machine transitions
        self.process_input()
        self.check_conditions()
        self.determine_service()
        self.check_bed_type()
        self.check_geographic_distance()
        self.restart()

    def get_queue_size(self) -> int:
        """
        Return the current size of the patient queue.
        
        Returns:
            int: The number of patients in the queue
        """
        return len(self.queue)

    def get_queue_statistics(self) -> dict:
        """
        Return statistics about the current queue.
        
        Returns:
            dict: A dictionary containing the total number of patients and counts for each bed type
        """
        if not self.queue:
            return {
                "total": 0,
                "intensive": 0,
                "intermediate": 0,
                "maternal": 0,
                "neonatal": 0
            }

        return {
            "total": len(self.queue),
            "intensive": sum(1 for p in self.queue if p.bedType == "Intensive"),
            "intermediate": sum(1 for p in self.queue if p.bedType == "Intermediate"),
            "maternal": sum(1 for p in self.queue if p.patientType == "Maternal"),
            "neonatal": sum(1 for p in self.queue if p.patientType == "Neonatal")
        }
        