import random
import math
import numpy as np
import pygame
from models.PausePlayButton import PausePlayButton
from models.hospital import Hospital
from models.patient import SimulatedPatient
from models.recommendation import HospitalRecommendation
from patient_data import get_patients
from utils.constants import *
from utils.data_loader import DataLoader
from utils.geographic import fsa_to_coordinates, calculate_distance, \
    latlon_to_pixel
from utils.animation import initialize_screen, draw_hospitals, draw_patient, animate_patient_movement, \
    draw_colormap_legend
import pandas as pd
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
import logging


# concerned with simulation
def discharge_all_patients(hospitals: list[Hospital], arrived_discharged: dict) -> None:
    """
    Discharge patients from all hospitals at a given arrival time.
    
    Args:
        arrival_time: Time of day for patient discharge
        arrived_discharged: Dictionary tracking patient movement
    """
    # time_index = ARRIVAL_TIMES.index(arrival_time)
    print("Discharging patients from all hospitals...")
    
    for hospital in hospitals:
        discharge_patients(hospital, arrived_discharged)


def discharge_all_patients_parallel(hospitals, arrived_discharged):
    with ThreadPoolExecutor() as executor:
        executor.map(lambda h: discharge_patients(h, arrived_discharged), hospitals)



def discharge_patients(hospital, arrivedDischarged):
    """ Discharge patients based on the discharge rate at the patient's arrival time """
    # Ensure the discharge rates are rounded to integers
    num_discharged_intensive = int(round(np.random.poisson(hospital.get_discharge_rate("Intensive"))))
    num_discharged_intermediate = int(round(np.random.poisson(hospital.get_discharge_rate("Intermediate"))))
    print(f"{num_discharged_intensive} {num_discharged_intermediate}")

    discharged_count = 0
    discharged_intensive = 0
    discharged_intermediate = 0

    # Process intensive care discharges
    for _ in range(min(num_discharged_intensive, len(hospital.patients["Intensive"]))):
        hospital.patients["Intensive"][0].discharged = True
        hospital.patients["Intensive"].pop(0)
        hospital.available_beds[0] += 1
        discharged_intensive += 1
        discharged_count += 1
        arrivedDischarged[hospital.name][1] += 1

    # Process intermediate care discharges
    for _ in range(min(num_discharged_intermediate, len(hospital.patients["Intermediate"]))):
        hospital.patients["Intermediate"][0].discharged = True
        hospital.patients["Intermediate"].pop(0)
        hospital.available_beds[1] += 1
        discharged_intermediate += 1
        discharged_count += 1
        arrivedDischarged[hospital.name][1] += 1

    print(
        f"{hospital.name}: Discharged intensive: {discharged_intensive} intermediate: {discharged_intermediate} total: {discharged_count} patients ")
    return discharged_count

def prepopulate_patients(hospital: Hospital) -> dict[str, list[SimulatedPatient]]:
    occupied_beds_intensive = round(hospital.total_capacity_intensive - hospital.available_beds[0])
    occupied_beds_intermediate = round(hospital.total_capacity_intermediate - hospital.available_beds[1])

    occupied_beds_intensive = max(0, occupied_beds_intensive)
    occupied_beds_intermediate = max(0, occupied_beds_intermediate)

    # Create dummy patients for both types of beds
    for bed_type, count in [("Intensive", occupied_beds_intensive),
                            ("Intermediate", occupied_beds_intermediate)]:
        for _ in range(count):
            patient = SimulatedPatient(
                    patientType=random.choice(PATIENT_TYPE),
                    gpsPos=hospital.geolocation,
                    postalCode="None",
                    bedType=bed_type,
                    # del24HrPlus=False,
                    transportNeedCnt=0,
                    specialNeedType=["None"],
                    specialNeeds=["None"],
                    arrival_time=random.choice(ARRIVAL_TIMES),
                    aniGpsPos=[600, 50],
                    arrived_at_hospital=True,  # Track if the patient has reached the hospital
                    queue_position=0,  # Initialize queue position
                    discharged=False,
                    assignedHospital=hospital.name,
                    distanceToHospital= random.randint(1, 100),
                    nearestHospital = hospital.name
                )
            hospital.patients[patient.bedType].append(patient)
    return hospital.patients

def load_data_loader(excel_path):
    if DATA_LOADER is None:
        DATA_LOADER = DataLoader()
        DATA_LOADER.load_data(excel_file=excel_path)
    return DATA_LOADER

screen, clock, map_surface, map_width, map_height = initialize_screen()
pause_play_button = PausePlayButton(1100, 10)
map_bounds = [44.0, 63.0, -79.0, -57.0]

def simulate_hospital_system(num_days, excel , excel_newdata):
    global total_patients # Declare total_patients as global within the function
    index = 0
    data_loader = DataLoader()
    data_loader.load_data(excel_file=excel)
    HOSPITALS = data_loader.create_hospitals()

    # TODO: Concatenate the sheets to load
    sheets_to_load = ['2021-01-11 to 2021-12-31', '2022-10-01 to 2022-12-31', '2023-01-01 to 2023-12-31']
    loaded_patients = []
    for sheet in sheets_to_load:
        loaded_patients.extend(get_patients("data/Patients_data3.xlsx", sheet))

# The 'patients' list now contains the combined results from all the sheets
    births_by_fsa = data_loader.calculate_birth_rates_by_fsa(excel_file=excel_newdata)
    recommendation_system = HospitalRecommendation(HOSPITALS)
    results = []
    total_patients = 0
    patients = []  # List to hold current patients
    patients_data = []

    for hospital in HOSPITALS:
        hospital_patient_list = prepopulate_patients(hospital)
        patients = patients + hospital_patient_list["Intensive"] + hospital_patient_list["Intermediate"]

    running = True
    paused = False
    day = 0  # Initialize day counter
    font = pygame.font.Font(None, 36) # Use a default font with size 36
    current_date = START_DATE

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_play_button.is_clicked(event.pos):  # Check if the button is clicked
                    paused = not paused
                    pause_play_button.toggle(screen)  # Toggle button state

        if paused:
            # Show paused message
            pause_message = font.render("Simulation Paused. Press Play to Resume.", True, (255, 0, 0))
            screen.blit(pause_message, (SCREEN_WIDTH // 2 - pause_message.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            clock.tick(10)  # Slow down the loop while paused
            continue  # Skip the simulation steps while paused

        # Loop through each day
        if day < num_days:
            current_date = START_DATE + timedelta(days=day)
            print(f"\n{'='*20} Day {day + 1} {'='*20}")

            arrivedDischarged = {"CHU-SJ":[0,0,0,0], "CHUQ":[0,0,0,0], "CHUS":[0,0,0,0],
                               "CUSM":[0,0,0,0], "HGJ":[0,0,0,0], "HMR":[0,0,0,0]}

            # Loop through each hour
            for hour in range(24):
                print(f"\n{'*'*10} Arrival Time {hour}:00 {'*'*10}")
                discharge_all_patients_parallel(HOSPITALS, arrivedDischarged)

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
                    #create patient
                    patient = create_patient(hour, loaded_patients[index])
                    index += 1
                    patients.append(patient)  # Add patient to the list
                    # Run the patient through the recommendation system
                    print(f"\nProcessing Patient {i + 1}")

                    process_patient(patient, recommendation_system, HOSPITALS, patients_data, current_date, arrivedDischarged)

                    # Print current hospital capacities
                    for hospital in HOSPITALS:
                        print(f"Current capacity for {hospital.name}:")
                        print(f"  - Intensive Care: {math.floor(hospital.available_beds[0])}/{hospital.total_capacity_intensive}")
                        print(f"  - Intermediate Care: {math.floor(hospital.available_beds[1])}/{hospital.total_capacity_intermediate}")
                        print(f"  - Total Available: {math.floor(hospital.available_beds[0] + hospital.available_beds[1])}")

                update_and_draw_simulation(screen, patients, hospital_positions, HOSPITALS, WHITE, day, current_date, font, map_surface)
                pause_play_button.draw(screen)
                # Refresh display
                pygame.display.flip()
                clock.tick(60)


            # Record daily statistics
            record_daily_statistics(day,current_date,HOSPITALS,arrivedDischarged, results)
            day += 1
        else:
            while running:
                all_patients_arrived = update_and_draw_simulation(screen, patients, hospital_positions, HOSPITALS, WHITE, day-1, current_date, font, map_surface)

                # Refresh display
                pygame.display.flip()
                clock.tick(60)

                # Check if all patients have arrived and set `running` to False if so
                if all_patients_arrived:
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
    print(f"Total Paitents:{total_patients}")
    print(f"Queue {recommendation_system.get_queue_size()}")
    print(f"Patietns who are assigned to the hospitals {total_patients- recommendation_system.get_queue_size()}")
    # Create a DataFrame from the results
    results_df = pd.DataFrame(results)
    patients_df = pd.DataFrame(patients_data)
    # # Save the results to an Excel file
    results_df.to_excel("output/simulation.xlsx", index=False)
    patients_df.to_excel("output/patients.xlsx", index=False)
    return results


def record_daily_statistics(day, current_date, hospitals, arrivedDischarged, results):
    for hospital in hospitals:
        results.append({
            "Day": day + 1,
            "Date": current_date.strftime("%Y-%m-%d"),
            "Month": current_date.month,
            "Hospital": hospital.name,
            "Arrived Patients": arrivedDischarged[hospital.name][0],
            "Discharged Patients": arrivedDischarged[hospital.name][1],
            "Intensive Occupancy Rate": arrivedDischarged[hospital.name][2] / 24,
            "Intermediate Occupancy Rate": arrivedDischarged[hospital.name][3] / 24,
            "Total Occupied" : (hospital.total_capacity_intensive - hospital.available_beds[0]) + (hospital.total_capacity_intermediate - hospital.available_beds[1]),
            "Total Capacity" : hospital.total_capacity
        })


def update_and_draw_simulation(screen, patients, hospital_positions, HOSPITALS, WHITE, day , current_date, font, map_surface):
    """
    Updates the state of the simulation, animates patient movement, and redraws the screen.

    Args:
        screen: The pygame screen object.
        patients: List of patient objects.
        hospital_positions: Dictionary mapping hospital names to positions.
        HOSPITALS: List of hospital objects.
        WHITE: Color code for clearing the screen.

    Returns:
        bool: Whether all patients have arrived or are discharged.
    """
    # Clear the screen
    screen.fill(WHITE)

    # Blit the pre-rendered map surface
    screen.blit(map_surface, (0, 0))

    # Draw the day counter
    day_counter_text = font.render(f"Day: {day + 1}, Date: {current_date.date()}", True, (0, 0, 0))  # Black text
    screen.blit(day_counter_text, (10, 10))  # Position at (10, 10) in the top-left corner

    # Draw hospitals
    draw_hospitals(screen, HOSPITALS)

    #Draw hospital positions
    for hospital in HOSPITALS:
        gpscoord = hospital.geolocation
        pxlcoor = latlon_to_pixel(gpscoord[0], gpscoord[1], map_width, map_height, map_bounds)
        pygame.draw.circle(screen, (0, 0, 255), (pxlcoor[0], pxlcoor[1]), 6)  # Red ellipse

    #Draw colormap legend
    draw_colormap_legend(screen, font, position=(50, 50))

    all_patients_arrived = True  # Assume all patients have arrived initially

    # Check if more than 50 patients are at the transport center and discharge them
    transport_center_patients = [p for p in patients if p.assignedHospital == "" and not p.discharged and p.arrived_at_hospital == True]
    if len(transport_center_patients) > 50:
        # Clear all patients at the transport center and reset their status
        for patient in transport_center_patients:
            patient.discharged = True

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

        # If the patient hasn't arrived or is not discharged, mark that not all patients have arrived
        if not patient.arrived_at_hospital and not patient.discharged:
            all_patients_arrived = False

        # Remove discharged patients from the list
        if patient.discharged:
            patients.remove(patient)

    return all_patients_arrived


# Patient Processing Logic
def create_patient(hour, patient):
    # patient_type = random.choice(PATIENT_TYPE)
    # postal_code, gps_pos = fsa_to_coordinates(births_by_fsa)

    # if patient_type == "Maternal":
    #     # Determine if delivery is within 24 hours
    #     del24HrPlus = random.choice([True, False])
    #     special_needs = random.sample(MATERNAL_SPECIAL_NEEDS, random.randint(1, 1))
    # else:
    #     del24HrPlus = False
    #     special_needs = random.sample(NEONATAL_SPECIAL_NEEDS, random.randint(1, 1))

    # patient = SimulatedPatient(
    #     patientType=patient_type,
    #     gpsPos=gps_pos,
    #     postalCode=postal_code,
    #     del24HrPlus=del24HrPlus,
    #     transportNeedCnt=random.randint(0, 3),
    #     specialNeedType=special_needs,
    #     specialNeeds=special_needs,
    #     arrival_time=hour,
    #     aniGpsPos= latlon_to_pixel(gps_pos[0], gps_pos[1], map_width, map_height, map_bounds),
    #     discharged=False,
    #     arrived_at_hospital=False,
    #     queue_position=0,
    #     # new attrobutes 
    #     DaysOldOnAdmission = random.randint(20, 40),
    #     GestationalAgeWeeks = random.randint(0, 10),
    #     minorCongAnomaly = bool(random.randint(0, 1)),
    #     majorCongAnomaly = bool(random.randint(0, 1)),
    #     cardiacCongAnomaly = bool(random.randint(0, 1)),
    #     neuroCongAnomaly = bool(random.randint(0, 1)),
    #     CDH = bool(random.randint(0, 1)),
    #     Gastroschisis = bool(random.randint(0, 1)),
    #     HIE = bool(random.randint(0, 1)),
    #     iNOFirstAdmDay1 = bool(random.randint(0, 1)),
    #     iNODuringStay= bool(random.randint(0, 1)),
    #     HighestRSuppOn1stAdmDay1 = bool(random.randint(0, 1))
    # )
    # # Log patient attributes in a readable format
    # log_patient_attributes(patient)
    # patient =     
    patient.arrival_time = hour
    patient.aniGpsPos = latlon_to_pixel(patient.gpsPos[0], patient.gpsPos[1], map_width, map_height, map_bounds)

    return patient

def log_patient_attributes(patient):
    logging.info("Patient Created:")
    logging.info(f"  Postal Code: {patient.postalCode}")
    logging.info(f"  Special Needs: {', '.join(patient.specialNeeds)}")
    logging.info(f"  Arrival Time: {patient.arrival_time}:00")
    logging.info(f"  GPS Position: {patient.gpsPos}")
    logging.info(f"  Patient Type: {patient.patientType}")
    logging.info(f"  Delivery within 24 Hours: {patient.del24HrPlus}")
    logging.info(f"  Transport Need Count: {patient.transportNeedCnt}")
    logging.info(f"  Animation GPS Position: {patient.aniGpsPos}")
    logging.info(f"  Discharged: {patient.discharged}")
    logging.info(f"  Arrived at Hospital: {patient.arrived_at_hospital}")
    logging.info(f"  Queue Position: {patient.queue_position}")

def process_patient(patient, recommendation_system, hospitals, patients_data, current_date, arrivedDischarged):
    recommendation_system.run(patient)
    if patient.assignedHospital:
        arrivedDischarged[f"{patient.assignedHospital}"][0] += 1
        for hospital in hospitals:
            if hospital.name == patient.nearestHospital:
                nearest_distance = calculate_distance(hospital.geolocation, patient.gpsPos)
            if hospital.name == patient.assignedHospital:
                assigned_distance = calculate_distance(hospital.geolocation, patient.gpsPos)

        patients_data.append({
            "Postal Code": patient.postalCode,
            "Type": patient.bedType,
            "Date": current_date.strftime("%Y-%m-%d"),
            "Month": current_date.month,
            "Nearest Hospital": patient.nearestHospital,
            "Nearest Distance": nearest_distance,
            "Assigned Hospital": patient.assignedHospital,
            "Assigned Distance": assigned_distance,
            "is it assigned to the nearest hospital": patient.nearestHospital == patient.assignedHospital,
            "Condition" : patient.condition,
            "Services" : patient.specialNeeds,
            "is it assigned to the best occupancy rate hospital": patient.bestOccupancyHospital == patient.assignedHospital,
            "is it assigned to the best option (both occupancy and distance)": (
                patient.nearestHospital == patient.assignedHospital and
                patient.bestOccupancyHospital == patient.assignedHospital
            ), 
            "Best Occupancy Hospital" : patient.bestOccupancyHospital
            

        })
