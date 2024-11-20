import random
import math
from time import sleep
import numpy as np
from models.hospital import Hospital
from models.patient import Patient
from models.recommendation import HospitalRecommendation
from utils.constants import *
from utils.data_loader import DataLoader
from utils.geographic import generate_patient_coords
from utils.admission import admit_patient

# concerned with simulation
def discharge_all_patients(hospitals: list[Hospital], arrival_time: int, arrived_discharged: dict) -> None:
    """
    Discharge patients from all hospitals at a given arrival time.
    
    Args:
        arrival_time: Time of day for patient discharge
        arrived_discharged: Dictionary tracking patient movement
    """
    time_index = ARRIVAL_TIMES.index(arrival_time)
    print("Discharging patients from all hospitals...")
    
    for hospital in hospitals:
        discharge_patients(hospital, time_index, arrived_discharged)


# this function should be in simulation.py, as Hospital class should only handle patient admissions and discharges.
def discharge_patients(hospital: Hospital, time_index, arrivedDischarged):
    discharged_count = 0
    
    # NICU discharges
    num_discharged_intensive = np.random.poisson(hospital.get_discharge_rate(time_index, "Intensive"))
    num_discharged_intermediate = np.random.poisson(hospital.get_discharge_rate(time_index, "Intermediate"))
    
    # Maternal discharges (using similar rates for now)
    num_discharged_birthcenter = np.random.poisson(hospital.discharge_rates[time_index] * 0.3)
    num_discharged_antepartum = np.random.poisson(hospital.discharge_rates[time_index] * 0.3)
    num_discharged_postpartum = np.random.poisson(hospital.discharge_rates[time_index] * 0.3)
    
    # Process NICU discharges
    for bed_type, num_discharge, bed_index in [
        ("Intensive", num_discharged_intensive, 0),
        ("Intermediate", num_discharged_intermediate, 1)
    ]:
        for _ in range(min(num_discharge, len(hospital.patients[bed_type]))):
            hospital.patients[bed_type].pop()
            hospital.available_beds[bed_index] += 1
            discharged_count += 1
            arrivedDischarged[hospital.name][1] += 1
    
    # Process maternal discharges
    for bed_type, num_discharge, bed_index in [
        ("BirthCenter", num_discharged_birthcenter, 2),
        ("Antepartum", num_discharged_antepartum, 3),
        ("Postpartum", num_discharged_postpartum, 4)
    ]:
        for _ in range(min(num_discharge, len(hospital.patients[bed_type]))):
            hospital.patients[bed_type].pop()
            hospital.available_beds[bed_index] += 1
            discharged_count += 1
            arrivedDischarged[hospital.name][1] += 1
    
    print(f"{hospital.name}: Discharged {discharged_count} patients at time {ARRIVAL_TIMES[time_index]}")
    return discharged_count

def prepopulate_patients(hospital: Hospital) -> None:
    occupied_beds_intensive = max(0, round(hospital.total_capacity_intensive - hospital.available_beds[0]))
    occupied_beds_intermediate = max(0, round(hospital.total_capacity_intermediate - hospital.available_beds[1]))

    # Create dummy patients for each bed type
    for bed_type, count in [("Intensive", occupied_beds_intensive), 
                            ("Intermediate", occupied_beds_intermediate)]:
        for _ in range(count):
            dummy_patient = Patient(
                patientType=random.choice(PATIENT_TYPE),
                gpsPos=hospital.geolocation,
                bedType=bed_type,
                del24HrPlus=False,
                transportNeedCnt=0,
                specialNeedType="None",
                specialNeeds=["None"],
                arrival_time=random.choice(ARRIVAL_TIMES)
            )
            hospital.patients[bed_type].append(dummy_patient)



def simulate_hospital_system(num_days, excel):
    total_patients = 0 # Declare total_patients as global within the function

    data_loader = DataLoader()
    data_loader.load_data(excel_file=excel)

    HOSPITALS = data_loader.create_hospitals()
    for hospital in HOSPITALS:
        prepopulate_patients(hospital)
    recommendation_system = HospitalRecommendation(HOSPITALS)
    results = []
    hospitalList = ["CHU-SJ", "CHUQ", "CHUS", "CUSM", "HGJ", "HMR"]
    # Loop through each day
    for n in range(num_days):
        print(f"\n{'='*20} Day {n + 1} {'='*20}")

        arrivedDischarged = {
            hospital: [0, 0, 0, 0,  # Existing counts
                      0, 0, 0]      # Birth center, antepartum, postpartum occupancy
            for hospital in hospitalList
        }
        
        # Loop through each arrival time (9, 14, 21)
        for arrival_time in ARRIVAL_TIMES:
            print(f"\n{'*'*10} Arrival Time {arrival_time}:00 {'*'*10}")
            discharge_all_patients(HOSPITALS, arrival_time, arrivedDischarged)
            
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
                    # Determine if delivery is within 24 hours
                    del24HrPlus = random.choice([True, False])
                    
                    # Probability that baby will need NICU care (adjust these probabilities as needed)
                    nicu_needed = random.random() < 0.15  # 15% chance of NICU need
                    
                    if nicu_needed:
                        # Add both maternal and neonatal needs
                        maternal_needs = random.sample(MATERNAL_SPECIAL_NEEDS, random.randint(1, 2))
                        neonatal_needs = random.sample(NEONATAL_SPECIAL_NEEDS, random.randint(1, 2))
                        special_needs = maternal_needs + neonatal_needs
                    else:
                        # Only maternal needs
                        num_special_needs = random.randint(1, 2)
                        special_needs = random.sample(MATERNAL_SPECIAL_NEEDS, num_special_needs)

                    # Create maternal patient
                    patient = Patient(
                        patientType="Maternal",
                        gpsPos=gps_pos,
                        bedType="BirthCenter" if not del24HrPlus else "Antepartum",
                        del24HrPlus=del24HrPlus,
                        transportNeedCnt=random.randint(0, 3),
                        specialNeedType=",".join(special_needs),
                        specialNeeds=special_needs,
                        nicu_needed=nicu_needed,  # Add this field to Patient class
                        arrival_time=arrival_time
                    )
                    
                else:
                    special_needs = random.sample(NEONATAL_SPECIAL_NEEDS, random.randint(1, 2))
                    patient = Patient(
                        patientType="Neonatal",
                        gpsPos=gps_pos,
                        bedType=random.choice(["Intensive", "Intermediate"]),
                        del24HrPlus=None,
                        transportNeedCnt=random.randint(0, 3),
                        specialNeedType=",".join(special_needs),
                        specialNeeds=special_needs,
                        nicu_needed=True,  # Add this field to Patient class
                        arrival_time=arrival_time
                    )

                # Run the patient through the recommendation system
                print(f"\nProcessing Patient {i + 1}")
                recommendation_system.run(patient)

                
                # Print current hospital capacities
                for hospital in HOSPITALS:
                    print(f"Current capacity for {hospital.name}:")
                    print(f"  - Intensive Care: {hospital.get_occupancy_rate('Intensive'):.2%}")
                    print(f"  - Intermediate Care: {hospital.get_occupancy_rate('Intermediate'):.2%}")
                    print(f"  - Birth Center: {hospital.get_occupancy_rate('BirthCenter'):.2%}")
                    print(f"  - Antepartum: {hospital.get_occupancy_rate('Antepartum'):.2%}")
                    print(f"  - Postpartum: {hospital.get_occupancy_rate('Postpartum'):.2%}")
                    print(f"  - Total Available: {hospital.get_occupancy_rate_overall():.2%}")

                if patient.assignedHospital != "":
                    arrivedDischarged[patient.assignedHospital][0] += 1
                

        

        # Record daily statistics
        for hospital in HOSPITALS:
            print(f"Patient distribution for {hospital.name}:")
            for bed_type in hospital.patients:
                print(f"  - {bed_type}: {len(hospital.patients[bed_type])}")
            results.append({
                "Day": n + 1,
                "Hospital": hospital.name,
                "Arrived Patients": arrivedDischarged[hospital.name][0],
                "Discharged Patients": arrivedDischarged[hospital.name][1],
                "Intensive Occupancy Rate": max(0, min(1, arrivedDischarged[hospital.name][2]/3)),
                "Intermediate Occupancy Rate": max(0, min(1, arrivedDischarged[hospital.name][3]/3))
            })
        

    return results