import pandas as pd
import numpy as np
from models.patient import SimulatedPatient
import pandas as pd
import random


def get_patients(excel_file: str):
    # Load and combine data from specified sheets
    sheets_to_load = ['2021-01-11 to 2021-12-31', '2022-10-01 to 2022-12-31', '2023-01-01 to 2023-12-31']
    excel_data = pd.read_excel(excel_file, sheet_name=sheets_to_load, header=1)

    # Combine all sheets into a single DataFrame
    combined_data = pd.concat(excel_data.values(), ignore_index=True)

    # List to store patient objects
    patients = []

    # Loop through each row in the DataFrame
    for _, row in combined_data.iterrows():
        # Create a SimulatedPatient instance for each row
        patient = SimulatedPatient(
            patientType="Neonatal",
            postalCode=row['PostalCode'],
            discharged=False,
            arrived_at_hospital=False,
            queue_position=0,
            arrival_time= 0, # should be changed 
            aniGpsPos=[0,1,2], # should be changed
            # new attributes 
            DaysOldOnAdmission=row['Days old on admission'] ,
            GestationalAgeWeeks=row['Gestational AgeWeeks'],
            minorCongAnomaly=row['minorCongAnomaly'],
            majorCongAnomaly=row['majorCongAnomaly'],
            cardiacCongAnomaly=row['cardiacCongAnomaly'],
            neuroCongAnomaly=row['neuroCongAnomaly'],
            CDH=row['CDH'],
            Gastroschisis=row['Gastroschisis'],
            HIE=row['HIE'],
            iNOFirstAdmDay1=row['iNOFirstAdmDay1'],
            iNODuringStay=row['iNODuringStay'],
            HighestRSuppOn1stAdmDay1= row['HighestRSuppOn1stAdmDay1']
        )
        
        # Append the patient to the list
        patients.append(patient)

    # Return the list of patients
    return patients

patients = get_patients('data/For Nick-Nov19-FindMyBed-transportData 2021 to 2023-Bed Type-hospital options.xlsx')
print(len(patients))