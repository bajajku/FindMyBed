from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Tuple, Literal
from models.recommendation import HospitalRecommendation
from models.patient import Patient
from utils.data_loader import DataLoader
import yaml
import os

# Load the configuration from the YAML file.
app = FastAPI()

try:
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
        excel_path = config.get('EXCEL_PATH')
        if not excel_path:
            raise ValueError("EXCEL_PATH not found in configuration.")
except Exception as e:
    raise RuntimeError(f"Failed to load configuration: {e}")

hospital_occupancy_configuration = {"CHU-SJ": {"Intensive": 0.95, "Intermediate": 0.95},
                                    "CHUQ": {"Intensive": 0.95, "Intermediate": 0.95},  
                                    "CHUS": {"Intensive": 0.95, "Intermediate": 0.95},
                                    "CUSM": {"Intensive": 0.95, "Intermediate": 0.95},
                                    "HGJ": {"Intensive": 0.95, "Intermediate": 0.95},
                                    "HMR": {"Intensive": 0.95, "Intermediate": 0.95}}
# Initialize the data loader and hospitals list.
data_loader = DataLoader()
try:
    data_loader.load_data(excel_file=excel_path, hospital_occupancy_configuration=hospital_occupancy_configuration)
    HOSPITALS = data_loader.create_hospitals()
except Exception as e:
    raise RuntimeError(f"Failed to initialize hospitals: {e}")

# Input model
class PatientInput(BaseModel):
    patientType: Literal["Maternal", "Neonatal"]  # Only these values are allowed
    gpsPos: Tuple[float, float]
    transportNeedCnt: int
    specialNeedType: List[str]
    specialNeeds: List[str]
    del24HrPlus: Optional[bool] = None
    bedType: str = ""
    homeHospital: Optional[str] = None


@app.post("/recommendation/")
async def recommendation(patient_input: PatientInput):
    """
    Generate hospital recommendations based on patient input.

    Args:
        patient_input (PatientInput): Patient information and requirements.

    Returns:
        dict: Recommended hospitals.
    """
    try:
        # Initialize Patient object
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

        # Generate recommendations
        recommendation_model = HospitalRecommendation(HOSPITALS)
        recommended_hospitals = recommendation_model.get_hospital_recommendations(patient=patient)

        # Prepare the response
        response = [{"hospital_name": hospital.name} for hospital in recommended_hospitals]

        return {"recommended_hospitals": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
