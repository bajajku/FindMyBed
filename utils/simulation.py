import random
import math
import numpy as np
from models.patient import Patient
from models.recommendation import HospitalRecommendation
from utils.constants import *
from utils.data_loader import DataLoader
from utils.geographic import generate_patient_coords

def simulate_hospital_system(num_days, excel):
    total_patients = 0 # Declare total_patients as global within the function

    data_loader = DataLoader()
    data_loader.load_data(excel_file=excel)

    HOSPITALS = data_loader.create_hospitals()
    recommendation_system = HospitalRecommendation(HOSPITALS)
    results = []
    hospitalList = ["CHU-SJ", "CHUQ", "CHUS", "CUSM", "HGJ", "HMR"]
    # Loop through each day
    for n in range(num_days):
        print(f"\n{'='*20} Day {n + 1} {'='*20}")

        arrivedDischarged = {"CHU-SJ":[0,0,0,0], "CHUQ":[0,0,0,0], "CHUS":[0,0,0,0], 
                           "CUSM":[0,0,0,0], "HGJ":[0,0,0,0], "HMR":[0,0,0,0]}
        
        # Loop through each arrival time (9, 14, 21)
        for arrival_time in ARRIVAL_TIMES:
            print(f"\n{'*'*10} Arrival Time {arrival_time}:00 {'*'*10}")
            recommendation_system.discharge_all_patients(arrival_time, arrivedDischarged)
            
            # Generate a random number of patients for this arrival time
            arrival_rate_index = ARRIVAL_TIMES.index(arrival_time)
            num_patients = np.random.poisson(data_loader.arrival_rates[arrival_rate_index])
            print(f"New patients arriving: {num_patients}")
            total_patients += num_patients

            # Store the occupancy rate per time slot for each hospital
            for hospital in HOSPITALS:
                occupancy_rates_intensive = max(0, min(1, hospital.get_occupancy_rate("Intensive")))
                occupancy_rates_intermediate = max(0, min(1, hospital.get_occupancy_rate("Intermediate")))

                # Accumulate occupancy rates for daily average calculation
                print(f"Hospital: {hospital.name}")
                print(f"  - Intensive Care Occupancy: {occupancy_rates_intensive:.2%}")
                print(f"  - Intermediate Care Occupancy: {occupancy_rates_intermediate:.2%}")
                
                arrivedDischarged[hospital.name][2] += occupancy_rates_intensive
                arrivedDischarged[hospital.name][3] += occupancy_rates_intermediate

            # Create and simulate each patient
            for i in range(num_patients):
                patient_type = random.choice(PATIENT_TYPE)
                gps_pos = generate_patient_coords(HOSPITALS_CONFIG)

                if patient_type == "Maternal":
                    num_special_needs = random.randint(1, 3)
                    special_needs = random.sample(MATERNAL_SPECIAL_NEEDS, num_special_needs)
                else:
                    num_special_needs = random.randint(1, 2)
                    special_needs = random.sample(NEONATAL_SPECIAL_NEEDS, num_special_needs)

                bed_type = random.choice(BED_TYPE)

                # Create a patient
                patient = Patient(
                    patientType=patient_type,
                    gpsPos=gps_pos,
                    bedType=bed_type,
                    del24HrPlus=random.choice([True, False]),
                    transportNeedCnt=random.randint(0, 3),
                    specialNeedType=",".join(special_needs),
                    specialNeeds=special_needs,
                    arrival_time=arrival_time
                )

                # Run the patient through the recommendation system
                print(f"\nProcessing Patient {i + 1}")
                recommendation_system.run(patient)
                
                # Print current hospital capacities
                for hospital in HOSPITALS:
                    print(f"Current capacity for {hospital.name}:")
                    print(f"  - Intensive Care: {math.floor(hospital.available_beds[0])}/{hospital.total_capacity_intensive}")
                    print(f"  - Intermediate Care: {math.floor(hospital.available_beds[1])}/{hospital.total_capacity_intermediate}")
                    print(f"  - Total Available: {math.floor(hospital.available_beds[0] + hospital.available_beds[1])}")

                if patient.assignedHospital != "":
                    arrivedDischarged[patient.assignedHospital][0] += 1

        # Record daily statistics
        for hospital in HOSPITALS:
            results.append({
                "Day": n + 1,
                "Hospital": hospital.name,
                "Arrived Patients": arrivedDischarged[hospital.name][0],
                "Discharged Patients": arrivedDischarged[hospital.name][1],
                "Intensive Occupancy Rate": max(0, min(1, arrivedDischarged[hospital.name][2]/3)),
                "Intermediate Occupancy Rate": max(0, min(1, arrivedDischarged[hospital.name][3]/3))
            })

    return results