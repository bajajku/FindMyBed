# animation.py
import pygame
from utils.constants import WHITE, BLUE, RED, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.constants import hospital_positions  # assuming this can be defined in your constants file

def initialize_screen():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hospital Patient Arrival Simulation")
    clock = pygame.time.Clock()
    return screen, clock

def draw_hospitals(screen, hospitals):
    for hospital in hospitals:
        x, y = hospital_positions[hospital.name]
        pygame.draw.rect(screen, BLUE, (x, y, 150, 50))
        font = pygame.font.Font(None, 24)

        #Hospital Name
        text = font.render(hospital.name, True, WHITE)
        screen.blit(text, (x + 5, y + 5))

        #Capacity
        capacity = hospital.get_total_capacity()
        capacity_text = font.render(capacity, True, WHITE)
        screen.blit(capacity_text, (x + 5, y + 30))  # Adjust y+30 to position it below the main text

    # Drawing Transport Centre
    x, y = hospital_positions[""]
    pygame.draw.rect(screen, BLUE, (x, y, 150, 50))
    font = pygame.font.Font(None, 24)
    text = font.render("Transport Centre", True, WHITE)
    screen.blit(text, (x + 5, y + 5))

def draw_patient(screen, patient, hospital_pos):
    if patient.arrived_at_hospital and not patient.discharged:
        offset_x = (patient.queue_position % 10) * 15
        offset_y = (patient.queue_position // 10) * 15
        x, y = hospital_pos[0] + offset_x + 5, hospital_pos[1] + offset_y + 60
        pygame.draw.circle(screen, RED, (x, y), 5)
    else:
        pygame.draw.circle(screen, RED, patient.aniGpsPos, 5)

def animate_patient_movement(patient, target_pos):
    if patient.aniGpsPos[0] < target_pos[0]:
        patient.aniGpsPos[0] += 1
    elif patient.aniGpsPos[0] > target_pos[0]:
        patient.aniGpsPos[0] -= 1
    if patient.aniGpsPos[1] < target_pos[1]:
        patient.aniGpsPos[1] += 1
    elif patient.aniGpsPos[1] > target_pos[1]:
        patient.aniGpsPos[1] -= 1

    if ((patient.aniGpsPos[0], patient.aniGpsPos[1]) == target_pos) and patient.arrived_at_hospital == False:
        patient.arrived_at_hospital = True  # Mark as arrived when at destination