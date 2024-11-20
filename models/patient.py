from dataclasses import dataclass
from typing import List, Tuple, Optional
from utils.constants import ARRIVAL_TIMES

@dataclass
class Patient:
    patientType: str
    gpsPos: Tuple[float, float]
    transportNeedCnt: int
    specialNeedType: str
    specialNeeds: List[str]
    arrival_time: int
    del24HrPlus: Optional[bool] = None
    nicu_needed: Optional[bool] = None
    bedType: str = ""
    assignedHospital: str = ""
    homeHospital: Optional[str] = None

    def get_arrival_time_index(self) -> int:
        return ARRIVAL_TIMES.index(self.arrival_time)
