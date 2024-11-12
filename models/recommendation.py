from typing import List, Optional
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

    def discharge_all_patients(self, arrived_discharged: dict) -> None:
        """
        Discharge patients from all hospitals at a given arrival time.

        Args:
            arrived_discharged: Dictionary tracking patient movement
        """
        logging.info("Discharging patients from all hospitals...")

        for hospital in self.hospitals:
            hospital.discharge_patients(arrived_discharged)

    def patient_type_check(self) -> None:
        """
        Checks for patient type Maternal or Neonatal in order to recognize what lists to use:
        Based on nicuBedType (if NICU is required):
            -> For Intensive NICU: Use ocpyRateNicuIntensive and ocpyRateOverallLst.
            -> For Immediate NICU: Use ocpyRateNicuImmediate and ocpyRateOverallLst.
            -> For Maternal patients:
            -> If Neonatal services are required (e.g., the baby may need NICU care post-birth):
            -> Use ocpyRateObstetrics with either ocpyRateNicuIntensive or ocpyRateNicuImmediate as required, along with ocpyRateOverallLst.
            -> If only Obstetrics is needed: Use ocpyRateObstetrics alone.

        """


    def home_hospital_check(self) -> None:
        """Adds Patient's Home Hospital in hospital's list if Applicable."""
        if not self.patient or not self.patient.homeHospital:
            return
        if self.patient.homeHospital not in self.available_hospitals:
            self.available_hospitals.append(self.patient.homeHospital)
        logging.info(f"Patient's preferred hospital added to Available Hospital List: {self.patient.homeHospital}")

    def determine_services(self) -> None:
        """Filter hospitals based on service availability and occupancy rate."""
        if not self.patient:
            return

        logging.info(f"Determining services for {self.patient.patientType} "
                    f"patient with needs {self.patient.specialNeeds}")

        # Set occupancy threshold based on bed type
        occupancy_threshold = (INTENSIVE_OCCUPANCY_THRESHOLD 
                             if self.patient.bedType == 'Intensive' 
                             else INTERMEDIATE_OCCUPANCY_THRESHOLD)

        self.available_hospitals = [
            hospital for hospital in self.hospitals
            if (hospital.can_treat_patient(self.patient) and
                hospital.get_occupancy_rate(self.patient.bedType) < occupancy_threshold)
        ]

        logging.info(f"Available hospitals meeting criteria: "
                    f"{[hospital.name for hospital in self.available_hospitals]}")

    def filter_bed_type(self) -> None:
        """Filter hospitals based on bed type availability."""
        if not self.available_hospitals or not self.patient:
            return

        logging.info(f"Filtering hospitals by bed type: {self.patient.bedType}")
        
        self.available_hospitals = [
            hospital for hospital in self.available_hospitals
            if hospital.get_capacity(self.patient.bedType) > 1
        ]

    def filter_by_distance(self) -> None:
        """Sort hospitals by distance to patient location."""
        if not self.available_hospitals or not self.patient:
            return

        logging.info(f"Sorting hospitals by distance from patient at {self.patient.gpsPos}")
        
        self.available_hospitals.sort(
            key=lambda hospital: calculate_distance(
                hospital.geolocation,
                self.patient.gpsPos
            )
        )

        logging.info(f"Sorted hospitals by distance: "
                    f"{[hospital.name for hospital in self.available_hospitals]}")

    def get_top_hospitals(self) -> List[Hospital]:
        """
        Get top 3 hospitals based on specified criteria and sorting logic.
        Returns:
            List[Hospital]: Up to 3 most suitable hospitals, sorted by priority
        """
        if not self.patient:
            return []

        preferred_hospitals = []
        
        # 1. Initial Home Hospital Check
        if self.patient.homeHospital:
            home_hospital = self.patient.homeHospital
            if (home_hospital.can_treat_patient(self.patient) and 
                home_hospital.get_occupancy_rate_overall() < 90):
                preferred_hospitals.append(home_hospital)

        # 2 & 3. Evaluate Each Hospital based on services and occupancy
        for hospital in self.hospitals:
            if hospital in preferred_hospitals:
                continue
                
            # Check if hospital can provide required services
            if not hospital.can_treat_patient(self.patient):
                continue

            # Get applicable occupancy rates based on patient type and needs
            occupancy_rate = hospital.get_occupancy_rate_per_patientType_per_bedType(self.patient)
            if occupancy_rate is None or occupancy_rate >= 0.9:  # 90% threshold
                continue

            # If we reach here, hospital meets all criteria
            preferred_hospitals.append(hospital)

        # 4. Sort hospitals by distance
        preferred_hospitals.sort(
            key=lambda h: calculate_distance(h.geolocation, self.patient.gpsPos)
        )

        # 5. Return top 3 choices
        return preferred_hospitals[:3]

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

    def run(self, patient: Patient) -> None:
        """
        Run the complete hospital recommendation process for a patient.
        
        Args:
            patient: Patient object to process
        """
        self.patient = patient
        logging.info("\nProcessing new patient...\n")
        
        # Execute state machine transitions
        self.process_input()
        self.determine_service()
        self.check_bed_type()
        self.check_geographic_distance()
        self.restart()

    def get_queue_size(self) -> int:
        """Return the current size of the patient queue."""
        return len(self.queue)

    def get_queue_statistics(self) -> dict:
        """Return statistics about the current queue."""
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
