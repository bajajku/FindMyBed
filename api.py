from fastapi import FastAPI
from utils.data_loader import DataLoader
from config import EXCEL_PATH
from models.patient import Patient
from models.hospital import Hospital
from models.recommendation import HospitalRecommendation
from pydantic import BaseModel
from typing import List, Tuple, Optional

app = FastAPI()

data_loader = DataLoader()
data_loader.load_data(excel_file=EXCEL_PATH)
HOSPITALS = data_loader.create_hospitals()

# Define Pydantic model for Patient
class PatientInput(BaseModel):
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
    distanceToHospital: int = 0

@app.post("/recommendation/")
def recommend_hospitals(patient_input: PatientInput):
    """
    Recommend hospitals based on patient needs and hospital availability.
    """
    patient = Patient(
        patientType=patient_input.patientType,
        gpsPos=patient_input.gpsPos,
        transportNeedCnt=patient_input.transportNeedCnt,
        specialNeedType=patient_input.specialNeedType,
        specialNeeds=patient_input.specialNeeds,
        arrival_time=patient_input.arrival_time,
        del24HrPlus=patient_input.del24HrPlus,
        nicu_needed=patient_input.nicu_needed,
        bedType=patient_input.bedType,
        assignedHospital=patient_input.assignedHospital,
        homeHospital=patient_input.homeHospital,
        distanceToHospital=patient_input.distanceToHospital,
    )
    recommendation = HospitalRecommendation(hospitals=HOSPITALS)
    recommended_hospitals = recommendation.get_hospital_recommendations(patient)
    # Prepare the response
    response = [
        {
            "hospital_name": hospital.name
        }
        for hospital in recommended_hospitals
    ]

    return {"recommended_hospitals": response}

