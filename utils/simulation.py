import random
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
    results=[]
    hospitalList = ["CHU-SJ", "CHUQ", "CHUS", "CUSM", "HGJ", "HMR"]
    # Loop through each day
    for n in range(num_days):
        print(f"\n--- Day {n + 1} ---")


        arrivedDischarged = {"CHU-SJ":[0,0,0,0], "CHUQ":[0,0,0,0], "CHUS":[0,0,0,0], "CUSM":[0,0,0,0], "HGJ":[0,0,0,0], "HMR":[0,0,0,0]}
        # Loop through each arrival time (9, 14, 21)
        for arrival_time in ARRIVAL_TIMES:
            print(f"\n--- Arrival Time {arrival_time}:00 ---")
            recommendation_system.discharge_all_patients(arrival_time, arrivedDischarged)
            # Generate a random number of patients for this arrival time
            arrival_rate_index = ARRIVAL_TIMES.index(arrival_time)
            num_patients = np.random.poisson(data_loader.arrival_rates[arrival_rate_index])
            print(f"Number of patients for arrival time {arrival_time}: {num_patients}")
            total_patients += num_patients

            # change 1030 - store the occupancy rate per time slot for each hospital
            for hospital in HOSPITALS:
                occupancy_rates_intensive = hospital.get_occupancy_rate("Intensive")
                occupancy_rates_intermediate = hospital.get_occupancy_rate("Intermediate")

                # Accumulate occupancy rates in arrivedDischarged for daily average calculation
                print(f"{hospital.name}, occupancy rate intensive: {occupancy_rates_intensive:.2f}, occupancy rate intermediate: {occupancy_rates_intermediate:.2f}")
                arrivedDischarged[hospital.name][2] += occupancy_rates_intensive
                arrivedDischarged[hospital.name][3] += occupancy_rates_intermediate

            # Create and simulate each patient
            for i in range(num_patients):
                patient_type = random.choice(PATIENT_TYPE)
                gps_pos = generate_patient_coords(HOSPITALS_CONFIG) #(random.uniform(45.4, 46.8), random.uniform(-73.7, -71.2))  # Random GPS coordinates

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
                    specialNeedType=",".join(special_needs),  # Store as a comma-separated string
                    specialNeeds=special_needs,  # Store as a list
                    arrival_time=arrival_time
                )

                # Run the patient through the recommendation system
                print(f"\n--- Patient {i + 1} ---")
                recommendation_system.run(patient)
                # time_index = patient.get_arrival_time_index()
                for hospital in HOSPITALS:
                    print(f"{hospital.name}, Intensive: {(hospital.available_beds[0])} / {hospital.total_capacity_intensive}, Intermediate: {(hospital.available_beds[1])} / {hospital.total_capacity_intermediate}, Total : {(hospital.available_beds[0]+hospital.available_beds[1])}")

                if patient.assignedHospital != "":
                    arrivedDischarged[f"{patient.assignedHospital}"][0]+=1
        # first tiral ( just get the occupancy rate per day )
        # second tiral ( get the occupancy rate per time slot and divide it by three to get the average per day  )
        for hospital in HOSPITALS:
            # # Calculate daily occupancy rates for each hospital
            # intensive_rate = hospital.get_occupancy_rate("Intensive")
            # intermediate_rate = hospital.get_occupancy_rate("Intermediate")

            results.append({
                "Day": n + 1,
                "Hospital": hospital.name,  # Use the name attribute of the Hospital object
                "Arrived Patients": arrivedDischarged[hospital.name][0],
                "Discharged Patients": arrivedDischarged[hospital.name][1],

                "Intensive Occupancy Rate": arrivedDischarged[hospital.name][2]/3,
                "Intermediate Occupancy Rate": arrivedDischarged[hospital.name][3]/3
            })
        # second tiral ( get the occupancy rate per time slot and divide it by three to get the average per day  )
    """
        for i in range(6):

          intensive_rate = hospitalList[i].get_occupancy_rate("Intensive")
          intermediate_rate = hospitalList[i].get_occupancy_rate("Intermediate")
          results.append({
              "Day": n+1,
              "Hospital": hospitalList[i],
              "Arrived Patients":arrivedDischarged[hospitalList[i]][0],
              "Discharged Patients":arrivedDischarged[hospitalList[i]][1],
              "Intensive Occupancy Rate": intensive_rate,
              "Intermediate Occupancy Rate": intermediate_rate
          })
    """
    # # Create a DataFrame from the results
    # results_df = pd.DataFrame(results)

    # # Save the results to an Excel file
    # #results_df.to_excel("/content/drive/MyDrive/Colab Notebooks/Korah_Dohee/output/patient_arrivals_simulation1.xlsx", index=False)
    # results_df.to_excel("patient_arrivals_simulation5.xlsx", index=False)
