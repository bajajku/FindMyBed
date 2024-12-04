from dataclasses import dataclass
from typing import List, Tuple, Optional
from utils.constants import ARRIVAL_TIMES

@dataclass
class Patient:
    patientType: str
    gpsPos: Tuple[float, float]
    transportNeedCnt: int
    specialNeedType: List[str]
    specialNeeds: List[str]
    del24HrPlus: Optional[bool] = None
    bedType: str = ""
    homeHospital: Optional[str] = None

    # def get_arrival_time_index(self) -> int:
    #     return ARRIVAL_TIMES.index(self.arrival_time)
    
@dataclass
class SimulatedPatient:
    patientType: str
    gpsPos: Tuple[float, float]
    postalCode: str
    del24HrPlus: bool
    transportNeedCnt: int
    specialNeedType: str
    specialNeeds: List[str]
    arrival_time: int
    aniGpsPos: list  # Start position at the dispatcher
    discharged: bool
    arrived_at_hospital: bool  # Track if the patient has reached the hospital
    queue_position: int  # Initialize queue position
    nicu_needed: Optional[bool] = None
    bedType: str = ""
    assignedHospital: str = ""
    homeHospital: Optional[str] = None
    distanceToHospital : int = 0
    is_indigenous: bool = False
    nearestHospital :str = ""

    def get_arrival_time_index(self) -> int:
        return ARRIVAL_TIMES.index(self.arrival_time)
