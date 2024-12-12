from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Tuple
from models.recommendation import HospitalRecommendation
from models.hospital import Hospital
from models.patient import Patient
from utils.data_loader import DataLoader
from config import EXCEL_PATH

app = FastAPI()

class PatientInput(BaseModel):
    """
    Pydantic model for patient input data required for hospital recommendations.

    Attributes:
        patientType (str): Type of patient (e.g., 'emergency', 'non-emergency')
        gpsPos (Tuple[float, float]): Patient's GPS coordinates (latitude, longitude)
        transportNeedCnt (int): Number of transport units needed
        specialNeedType (List[str]): Types of special needs required
        specialNeeds (List[str]): Specific special needs requirements
        del24HrPlus (Optional[bool]): Whether delivery is needed in 24+ hours
        bedType (str): Type of bed required (default: "")
        homeHospital (Optional[str]): Patient's preferred/home hospital
    """
    patientType: str
    gpsPos: Tuple[float, float]
    transportNeedCnt: int
    specialNeedType: List[str]
    specialNeeds: List[str]
    # arrival_time: int
    del24HrPlus: Optional[bool] = None
    bedType: str = ""
    homeHospital: Optional[str] = None

# Initialize the recommendation model
data_loader = DataLoader()
data_loader.load_data(excel_file=EXCEL_PATH)
HOSPITALS = data_loader.create_hospitals()

@app.post("/recommendation/")
async def recommendation(patient_input: PatientInput):
    """
    Generate hospital recommendations based on patient input.

    Args:
        patient_input (PatientInput): Patient information and requirements

    Returns:
        dict: Hospital recommendations with matching criteria

    Example:
        POST /recommendation/
        {
            "patientType": "Maternal",
            "gpsPos": [51.5074, -0.1278],
            "transportNeedCnt": 1,
            "specialNeedType": ["Neurology"],
            "specialNeeds": ["Northern module"],
            "del24HrPlus": False,
            "bedType": "Intensive",
            "homeHospital": "CUSM"
        }
    """
    # Get the patient's input and return a recommendation
    patient = Patient(
        patientType=patient_input.patientType,
        gpsPos=patient_input.gpsPos,
        transportNeedCnt=patient_input.transportNeedCnt,
        specialNeedType=patient_input.specialNeedType,
        specialNeeds=patient_input.specialNeeds,
        del24HrPlus=patient_input.del24HrPlus,
        bedType=patient_input.bedType,
        homeHospital=patient_input.homeHospital
    )
    recommendation = HospitalRecommendation(HOSPITALS)
    recommended_hospital = recommendation.get_hospital_recommendations(patient=patient)
    
    response = [{
        "hospital_name": hospital.name
    } for hospital in recommended_hospital
    ]

    return {"recommended_hospitals": response}