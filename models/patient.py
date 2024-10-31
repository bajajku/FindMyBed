from dataclasses import dataclass
from typing import List, Tuple
from utils.constants import ARRIVAL_TIMES

@dataclass
class Patient:
    patientType: str
    gpsPos: Tuple[float, float]
    bedType: str
    del24HrPlus: bool
    transportNeedCnt: int
    specialNeedType: str
    specialNeeds: List[str]
    arrival_time: int
    assignedHospital: str = ""

    def get_arrival_time_index(self) -> int:
        return ARRIVAL_TIMES.index(self.arrival_time)
