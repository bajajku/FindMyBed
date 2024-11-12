import random
import math
import numpy as np
import pygame

from config import EXCEL_PATH
from models.patient import Patient
from models.recommendation import HospitalRecommendation
from utils.constants import *
from utils.data_loader import DataLoader
from utils.geographic import generate_patient_coords
from utils.animation import initialize_screen, draw_hospitals, draw_patient, animate_patient_movement

screen, clock = initialize_screen()
data_loader = DataLoader()
data_loader.load_data(excel_file=EXCEL_PATH)
HOSPITALS = data_loader.create_hospitals()

def simulate_hospital_system(num_days, excel):
    global total_patients # Declare total_patients as global within the function


    recommendation_system = HospitalRecommendation(HOSPITALS)
    results = []
    hospitalList = ["CHU-SJ", "CHUQ", "CHUS", "CUSM", "HGJ", "HMR"]
    total_patients = 0
    patients = []  # List to hold current patients

    for hospital in HOSPITALS:
        hospital_patient_list = hospital.prepopulate_patients()
        patients = patients + hospital_patient_list["Intensive"] + hospital_patient_list["Intermediate"]

    running = True
    day = 0  # Initialize day counter

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Loop through each day
        if day < num_days:
            print(f"\n{'='*20} Day {day + 1} {'='*20}")

            arrivedDischarged = {"CHU-SJ":[0,0,0,0], "CHUQ":[0,0,0,0], "CHUS":[0,0,0,0],
                               "CUSM":[0,0,0,0], "HGJ":[0,0,0,0], "HMR":[0,0,0,0]}

            # Loop through each arrival time (9, 14, 21)
            for hour in range(24):
                print(f"\n{'*'*10} Arrival Time {hour}:00 {'*'*10}")
                recommendation_system.discharge_all_patients(arrivedDischarged)

                # Generate a random number of patients for this arrival time
                num_patients = np.random.poisson(data_loader.get_average_admissions())
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
                        arrival_time=hour,
                        aniGpsPos=[600, 50],
                        discharged=False,
                        arrived_at_hospital=False,  # Track if the patient has reached the hospital
                        queue_position=0  # Initialize queue position
                    )
                    patients.append(patient)  # Add patient to the list
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
                # Clear the screen
                screen.fill(WHITE)

                # Draw hospitals
                draw_hospitals(screen, HOSPITALS)

                # Organize each patient in the queue
                for hospital_name in hospital_positions:
                    patients_at_hospital = [
                        p for p in patients if
                        p.assignedHospital == hospital_name and p.arrived_at_hospital and not p.discharged
                    ]
                    for i, patient in enumerate(patients_at_hospital):
                        patient.queue_position = i  # Assign queue position based on order of arrival

                # Move and draw each patient
                for patient in patients[:]:
                    if not patient.discharged:
                        target_hospital_pos = hospital_positions.get(patient.assignedHospital, (600, 50))
                        animate_patient_movement(patient, target_hospital_pos)

                        # Draw patient at the updated position
                        draw_patient(screen, patient, target_hospital_pos)

                    if patient.discharged:
                        patients.remove(patient)


                # Refresh display
                pygame.display.flip()
                clock.tick(60)


            # Record daily statistics
            for hospital in HOSPITALS:
                results.append({
                    "Day": day + 1,
                    "Hospital": hospital.name,
                    "Arrived Patients": arrivedDischarged[hospital.name][0],
                    "Discharged Patients": arrivedDischarged[hospital.name][1],
                    "Intensive Occupancy Rate": max(0, min(1, arrivedDischarged[hospital.name][2]/24)),
                    "Intermediate Occupancy Rate": max(0, min(1, arrivedDischarged[hospital.name][3]/24))
                })
            day += 1
        else:
            running = False
    # Pause screen after simulation ends
    paused = True
    font = pygame.font.Font(None, 36)
    pause_message = font.render("Simulation complete! Press any key to exit.", True, (0, 0, 0))
    screen.blit(pause_message, (SCREEN_WIDTH // 2 - pause_message.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()

    # Wait for user input to exit
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
            elif event.type == pygame.KEYDOWN:
                paused = False

    pygame.quit()
    print(total_patients)
    print(recommendation_system.get_queue_size())
    return results