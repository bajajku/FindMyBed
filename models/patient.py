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
    patientType: str
    gpsPos: Tuple[float, float]
    postalCode: str
    del24HrPlus: bool
    transportNeedCnt: int
    specialNeedType: str
    specialNeeds: List[str]
    arrival_time: int
    aniGpsPos: list
    discharged: bool
    arrived_at_hospital: bool
    queue_position: int
    bedType: str = ""
    assignedHospital: str = ""
    homeHospital: Optional[str] = None
    distanceToHospital : int = 0
    # To check what's the best option in terms of distance and occupancy rate 
    nearestHospital :str = ""
    bestOccupancyHospital: str = ""
    # Adding a new attribute to manage hospital restrictions for generating patient tables.
    condition: int = 0 

    def get_arrival_time_index(self) -> int:
        return ARRIVAL_TIMES.index(self.arrival_time)
