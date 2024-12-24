import logging
import pandas as pd
import numpy as np
from models.patient import SimulatedPatient
import pandas as pd
import random
from utils.constants import NEONATAL_SPECIAL_NEEDS
from utils.geographic import  get_fsa_center



def get_patients(excel_file: str, sheet):
    # Load data from the specified sheet
    excel_data = pd.read_excel(excel_file, sheet_name=sheet)
    patients = []

    for _, row in excel_data.iterrows():
        bedType = row['Bed type']
        Condition1 = row['Condition 1']
        Condition2 = row['Condition 2']
        Condition3 = row['Condition 3']
        Condition4 = row['Condition 4']
        Condition5 = row['Condition 5']
        postalCode = row['PostalCode']
        firstSiteCode = row['firstSiteCode']
        if firstSiteCode == "JGH":
            firstSiteCode = "HGJ"
        elif firstSiteCode == "MUHC":
            firstSiteCode = "CUSM"
        elif firstSiteCode == "HSJ":
            firstSiteCode = "CHU-SJ"

        if pd.isna(postalCode):
            continue
        # Determine patient type
        patient_type = "Neonatal"

        special_needs = random.sample(NEONATAL_SPECIAL_NEEDS, random.randint(1, 1))
        try:
            # Try to get the GPS position using the postal code
            gpsPos = get_fsa_center(postalCode[:3])
        except Exception as e:
            # Handle the error (e.g., postal code not found)
            print(f"Error retrieving GPS for postal code {postalCode}: {e}")
            gpsPos = (0, 0)  # Default value if error occurs, or you can set another fallback
        
        # Determine condition
        if Condition1 != "No Match":
            condition = 1
        elif not pd.isna(Condition2):
            condition = 2
        elif not pd.isna(Condition3):
            condition = 3
        elif not pd.isna(Condition4):
            condition = 4
        else:
            condition = 5
        # Create a simulated patient instance
        # still need to set patientArrival, and patientAniGpsPos
        patient = SimulatedPatient(
            patientType=patient_type,
            gpsPos=gpsPos,
            transportNeedCnt=random.randint(0, 3),
            specialNeedType=special_needs,
            specialNeeds=special_needs,
            discharged=False,
            arrived_at_hospital=False,
            queue_position=0,
            postalCode=postalCode,
            bedType=bedType,
            condition=condition,
            firstSiteCode=firstSiteCode
        )
        print(f"Created patient: {patient}")
        print(f"Patient condition: {patient.condition}")
        print(f"Patient special needs: {patient.specialNeeds}")
        print(f"Patient bed type: {patient.bedType}")
        print(f"Patient postal code: {patient.postalCode}")
        

        
        patients.append(patient)

    return patients

sheets_to_load = ['2021-01-11 to 2021-12-31', '2022-10-01 to 2022-12-31', '2023-01-01 to 2023-12-31']

patients = get_patients("data/Patients_data3.xlsx", sheets_to_load[0])

print(patients[0])