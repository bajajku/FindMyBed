from dataclasses import dataclass
from typing import List, Tuple, Optional
from utils.constants import ARRIVAL_TIMES

'''
   Separated Patient from SimulatedPatient, as to serve different purposes
   Promotion of code reusability and readability, 
   and Single Responsibility Principle (SRP)
'''
@dataclass
class Patient:
    """
    Represents a patient with their basic information and medical needs.

    Attributes:
        patientType (str): Type/category of the patient
        gpsPos (Tuple[float, float]): Geographic coordinates of patient location
        transportNeedCnt (int): Number of transport needs/requirements
        specialNeedType (List[str]): Types of special needs
        specialNeeds (List[str]): Specific special needs details
        del24HrPlus (Optional[bool]): If delivery is 24+ hours, defaults to None
        bedType (str): Type of bed required, defaults to empty string
        homeHospital (Optional[str]): Patient's home hospital, defaults to None
    """
    patientType: str
    gpsPos: Tuple[float, float]
    transportNeedCnt: int
    specialNeedType: List[str]
    specialNeeds: List[str]
    del24HrPlus: Optional[bool] = None
    bedType: str = ""
    homeHospital: Optional[str] = None

@dataclass
class SimulatedPatient:
    """
    Represents a patient in the simulation system with additional tracking attributes.

    Attributes:
        patientType (str): Type/category of the patient
        gpsPos (Tuple[float, float]): Geographic coordinates of patient location
        postalCode (str): Postal code of patient location
        del24HrPlus (bool): If delivery is 24+ hours
        transportNeedCnt (int): Number of transport needs/requirements
        specialNeedType (str): Type of special need
        specialNeeds (List[str]): List of specific special needs
        arrival_time (int): Patient's arrival time
        aniGpsPos (list): Initial position at the dispatcher
        discharged (bool): Whether patient has been discharged
        arrived_at_hospital (bool): Whether patient has reached the hospital
        queue_position (int): Patient's position in queue
        bedType (str): Type of bed required, defaults to empty string
    """
    # We set these up
    patientType: str
    # del24HrPlus: bool
    transportNeedCnt: int
    specialNeedType: str
    specialNeeds: List[str]
    
    discharged: bool
    arrived_at_hospital: bool
    queue_position: int
    assignedHospital: str = ""
    homeHospital: Optional[str] = None
    distanceToHospital : int = 0
    aniGpsPos: list = None
    arrival_time: int = 0


    #From the excel sheet
    gpsPos: Tuple[float, float] = (0,0)
    postalCode: str = ""
    bedType: str = ""
    condition: int = 0

    # we will decide these based on algorithm
    nearestHospital :str = ""
    bestOccupancyHospital: str = ""


    def get_arrival_time_index(self) -> int:
        return ARRIVAL_TIMES.index(self.arrival_time)
    
    # def decide_bed_type(self) -> None:
    #     """Decide the bed types based on the attributes """

    #     # Condition 1: GA < 32 weeks and admitted < 2 days after birth => INTENSIVE
    #     if self.patient.GestationalAgeWeeks < 32 and self.patient.DaysOldOnAdmission < 2:
    #         self.patient.bedType = "Intensive"
        
    #     # Condition 2: If HIE or any major congenital anomaly => INTENSIVE
    #     elif self.patient.HIE or self.patient.majorCongAnomaly or self.patient.cardiacCongAnomaly or self.patient.neuroCongAnomaly:
    #         self.patient.bedType = "Intensive"
        
    #     # Condition 3: If iNO day 1 => INTENSIVE
    #     elif self.patient.iNOFirstAdmDay1:
    #         self.patient.bedType = "Intensive"
        
    #     # Condition 4: If respiratory support on day 1 is one of the specified values => INTENSIVE
    #     elif self.patient.HighestRSuppOn1stAdmDay1 in ["IPPV", "HFOV", "HFJT", "NIV", "CPAP", "High flow"]:
    #         self.patient.bedType = "Intensive"
    #     else:
    #         self.patient.bedType = "Intermediate"
    
    # def decide_condition(self) -> None:
    #     """Filter hospitals based on service availability and occupancy rate."""
    #     # Condition 1: First Nations 
    #     if self.patient.postalCode[:3] == "J0M" or self.patient.postalCode[0] in ("X", "Y"):
    #         self.patient.condition = 1

    #     # Condition 2: Major anomaly AND cardiac OR neuro
    #     elif (self.patient.majorCongAnomaly and (self.patient.neuroCongAnomaly or self.patient.cardiacCongAnomaly or self.patient.HIE)):
    #         self.patient.condition = 2

    #     # Condition 3: Major anomaly BUT not condition 2 or prematurity
    #     elif (self.patient.majorCongAnomaly and not (self.patient.cardiacCongAnomaly or self.patient.neuroCongAnomaly or self.patient.HIE or self.patient.CDH)):
    #         self.patient.condition = 3

    #     # Condition 4: Prematurity (GA<26 weeks)
    #     elif self.patient.GestationalAgeWeeks < 26:
    #         self.patient.condition = 4

    #     # Condition 5
    #     else:
    #         self.patient.condition = 5