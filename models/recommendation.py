from typing import List, Optional

import yaml
from transitions import Machine
from models.patient import Patient
from models.hospital import Hospital
from utils.constants import *
from utils.geographic import calculate_distance
import logging

logging.basicConfig(
    filename='logs/hospital_recommendation.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access the configuration value.
weight_of_distance = config['WEIGHT_OF_SORTING_BY_DISTANCE']

class HospitalRecommendation:
    """
    A state machine for hospital recommendations based on patient needs and hospital availability.
    """
    
    states = [
        'input',
        'condition_check',
        'bed_type_determination' , 
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
        self.machine.add_transition(
            trigger='check_conditions',
            source='condition_check',
            dest='bed_type_determination',
            after='decide_bed_type'
        )
        self.machine.add_transition(
            trigger='decide_bedtype',
            source='bed_type_determination',
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
            after='filter_by_distance_and_occupancy_rate'
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
        # Helper checks
        is_prematurity_ga_lt_26 = "Prematurity (GA<26 weeks)" in self.patient.specialNeeds

        # Condition 1: First Nations 
        if self.patient.postalCode == "J0M" or self.patient.postalCode[0] in ("X", "Y"):
            self.available_hospitals = [
                hospital for hospital in self.hospitals if hospital.name == "CUSM"
            ]
            self.patient.condition = 1

        # Condition 2: Major anomaly AND cardiac OR neuro
        elif (self.patient.majorCongAnomaly and (self.patient.neuroCongAnomaly or self.patient.cardiacCongAnomaly or self.patient.HIE)):
            valid_hospitals = ["CUSM", "CHU-SJ", "CHUQ"]
            self.available_hospitals = [
                hospital for hospital in self.hospitals if hospital.name in valid_hospitals
            ]
            self.patient.condition = 2

        # Condition 3: Major anomaly BUT not condition 2 or prematurity
        elif (self.patient.majorCongAnomaly and not (self.patient.cardiacCongAnomaly or self.patient.neuroCongAnomaly or self.patient.HIE or self.patient.CDH)):
            valid_hospitals = ["CUSM", "CHU-SJ", "CHUQ", "CHUS"]
            self.available_hospitals = [
                hospital for hospital in self.hospitals if hospital.name in valid_hospitals
            ]
            self.patient.condition = 3

        # Condition 4: Prematurity (GA<26 weeks)
        elif self.patient.GestationalAgeWeeks < 26:
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
        logging.info(f"Filtered hospitals based on restriction conditions : {[h.name for h in self.available_hospitals]}")

    def decide_bed_type(self) -> None:
        """Decide the bed types based on the attributes """

        # Condition 1: GA < 32 weeks and admitted < 2 days after birth => INTENSIVE
        if self.patient.GestationalAgeWeeks < 32 and self.patient.DaysOldOnAdmission < 2:
            self.bed_type = "Intensive"
        
        # Condition 2: If HIE or any major congenital anomaly => INTENSIVE
        elif self.patient.HIE or self.patient.majorCongAnomaly or self.patient.cardiacCongAnomaly or self.patient.neuroCongAnomaly:
            self.bed_type = "Intensive"
        
        # Condition 3: If iNO day 1 => INTENSIVE
        elif self.patient.iNOFirstAdmDay1:
            self.bed_type = "Intensive"
        
        # Condition 4: If respiratory support on day 1 is one of the specified values => INTENSIVE
        elif self.patient.HighestRSuppOn1stAdmDay1 in ["IPPV", "HFOV", "HFJT", "NIV", "CPAP", "High flow"]:
            self.bed_type = "Intensive"
        else:
            self.bed_type = "Intermediate"
        logging.info(f"Patient's bed type is  : {self.patient.bedType}")

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
        if self.available_hospitals:
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
        logging.info(f"Patient's preferred hospital added to Available Hospital List: {self.patient.homeHospital}")

    def determine_services(self) -> None:
        """
        Filter hospitals based on service availability and occupancy rate.
        """
        if not self.patient or self.patient.patientType not in PATIENT_TYPE:
            logging.error("Patient type not recognized.")
            return

        self.available_hospitals = [
            hospital for hospital in self.available_hospitals 
            if all(need in hospital.get_hospital_services() for need in self.patient.specialNeedType)
        ]
        #Assigning nearest hospital to patients who will be assigned to transport centre later on
        temp_sorted_hospitals = sorted(
            self.available_hospitals,
            key=lambda hospital: calculate_distance(
                hospital.geolocation,
                self.patient.gpsPos
            )
        )
        nearest_hospital = temp_sorted_hospitals[0]
        self.patient.nearestHospital = nearest_hospital.name
        logging.info(f"Filtered hospitals based on services and occupancy: {[h.name for h in self.available_hospitals]}")

    def filter_bed_type(self) -> None:
        """
        Filter hospitals based on bed type availability.
        """
        if not self.available_hospitals or not self.patient:
            return

        logging.info(f"Filtering hospitals by bed type: {self.patient.bedType}")
        
        self.available_hospitals = [
            hospital for hospital in self.available_hospitals
            if hospital.get_capacity(self.patient.bedType) > 1
        ]

    def filter_by_distance_and_occupancy_rate(self, weight_distance: float = weight_of_distance, weight_occupancy: float = 1 - weight_of_distance) -> None:
        """
        Filter hospitals considering both distance and occupancy rate,
        prioritizing based on a weighted score.

        Args:
            weight_distance (float): Weight for distance in the score calculation.
            weight_occupancy (float): Weight for occupancy rate in the score calculation.
        """
        if not self.available_hospitals or not self.patient:
            return

        logging.info(f"Sorting hospitals by distance and occupancy for patient at {self.patient.gpsPos}")

        #Sorting patients by occupancy rates, removing hospitals with higher occupancy than threshold value
        self.available_hospitals = [hospital for hospital in self.available_hospitals
                                    if hospital.can_admit_patient(self.patient)]
        self.find_nearest_and_best_occupancy_hospitals()

        # Calculate distances for all hospitals
        distances = [
            calculate_distance(hospital.geolocation, self.patient.gpsPos)
            for hospital in self.available_hospitals
        ]

        # Find min and max distances for normalization
        min_distance = min(distances)
        max_distance = max(distances)

        def calculate_hospital_score(hospital):
            # Normalize distance
            distance = calculate_distance(hospital.geolocation, self.patient.gpsPos)
            if max_distance != min_distance:  # Avoid division by zero
                normalized_distance = (distance - min_distance) / (max_distance - min_distance)
            else:
                normalized_distance = 0  # If all distances are the same, normalize to 0

            occupancy = hospital.get_occupancy_rate(self.patient.bedType)  # Lower occupancy preferred

            return weight_distance * normalized_distance + weight_occupancy * occupancy

        # Sort hospitals by the calculated score
        self.available_hospitals.sort(key=calculate_hospital_score)

        logging.info(f"anked hospitals by distance and occupancy: "
                    f"{[hospital.name for hospital in self.available_hospitals]}")

    def get_top_hospitals(self) -> List[Hospital]:
        """
        Get top 3 hospitals based on specified criteria and sorting logic.
        
        Returns:
            List[Hospital]: Up to 3 most suitable hospitals, sorted by priority
        """
        if not self.patient or self.patient.patientType not in PATIENT_TYPE:
            return ValueError("Patient type not recognized.")
        if not self.available_hospitals:
            return []
        
        available_hospitals_copy = self.available_hospitals[:]
        
        if self.patient.homeHospital:
            home_hospital = next((h for h in available_hospitals_copy if h.name == self.patient.homeHospital), None)
            if home_hospital:
                preferred_hospitals = [home_hospital]
                available_hospitals_copy.remove(home_hospital)
                preferred_hospitals += available_hospitals_copy[:2]
                logging.info(f"Patient's preferred hospital removed from Available Hospital List: {self.patient.homeHospital}")
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
            logging.info(f"Patient assigned to {self.selected_hospital.name}")
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
        logging.info("\nGenerating hospital recommendations for the patient...\n")
        
        # Perform the recommendation steps up to geographic distance check
        self.process_input()
        self.check_conditions()
        self.determine_service()
        self.check_bed_type()
        self.check_geographic_distance()
        
        # Get the top hospital recommendations
        recommendations = self.get_top_hospitals()
        self.restart()

        logging.info(f"Top hospital recommendations: {[h.name for h in recommendations]}")
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
        logging.info("Processing This patient...")
        # Execute state machine transitions
        self.process_input()
        self.check_conditions()
        self.decide_bedtype()
        self.determine_service()
        self.check_bed_type()
        self.check_geographic_distance()
        self.restart()
        logging.info("Patient processing complete.\n")

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
        