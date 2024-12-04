# animation.py
import math

import pygame

from config import EXCEL_PATH
from models.recommendation import HospitalRecommendation
from utils.constants import WHITE, BLUE, RED, SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, AQUAMARINE
from utils.constants import hospital_positions  # assuming this can be defined in your constants file
from utils.data_loader import DataLoader
from matplotlib import cm
import numpy as np
import matplotlib.pyplot as plt

# Initialize the colormap
cmap = cm.get_cmap('viridis')
gradient_steps = 256  # Number of discrete steps in the gradient
gradient_table = []

# Precompute the gradient as a lookup table
for i in range(gradient_steps):
    normalized_value = 1 - (i / (gradient_steps - 1))  # Range from 0 to 1
    r, g, b, _ = cmap(normalized_value)  # RGBA values
    gradient_table.append((int(r * 255), int(g * 255), int(b * 255)))

data_loader = DataLoader()
data_loader.load_data(excel_file=EXCEL_PATH)
HOSPITALS = data_loader.create_hospitals()
hospital_dict = {hospital.name: hospital for hospital in HOSPITALS}

#load patient icon
patient_icon1 = pygame.image.load("icons/patient.png")
patient_icon1 = pygame.transform.scale(patient_icon1, (20, 20))

patient_icon2 = pygame.image.load("icons/patient2.png")
patient_icon2 = pygame.transform.scale(patient_icon2, (20, 20))

def initialize_screen():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hospital Patient Arrival Simulation")
    clock = pygame.time.Clock()

    # Load the Quebec map
    map_image = pygame.image.load("icons/quebec-map.gif").convert()
    image_width, image_height = map_image.get_width(), map_image.get_height()

    # Calculate the scaling factor to fit the image inside 0the screen
    width_scale = SCREEN_WIDTH / image_width
    height_scale = SCREEN_HEIGHT / image_height
    scale_factor = min(width_scale, height_scale)  # Choose the smaller factor to fit within the screen

    # Scale the image
    new_width = int(image_width * scale_factor)
    new_height = int(image_height * scale_factor)
    map_image = pygame.transform.scale(map_image, (new_width, new_height))

    # Create a static surface for the map
    map_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    map_surface.fill((255, 255, 255))  # Optional: Fill with a background color (e.g., white)

    # Center the scaled map image on the screen
    map_surface.blit(map_image,
                     ((SCREEN_WIDTH - new_width) // 2,  # Center horizontally
                      (SCREEN_HEIGHT - new_height) // 2))  # Center vertically

    # Convert the patient icon after initializing the display
    global patient_icon1, patient_icon2
    patient_icon1 = patient_icon1.convert_alpha()
    patient_icon2 = patient_icon2.convert_alpha()

    return screen, clock , map_surface, map_image.get_width(), map_image.get_height()

def draw_hospitals(screen, hospitals):
    for hospital in hospitals:
        x, y = hospital_positions[hospital.name]
        pygame.draw.rect(screen, AQUAMARINE, (x, y, 255, 50))

        # Draw the border around the hospital
        border_thickness = 3  # Thickness of the border
        height = 50 + ((math.ceil(hospital.total_capacity / 10)) * 25 )
        pygame.draw.rect(screen, AQUAMARINE, (x, y, 255, height), border_thickness)

        font = pygame.font.Font(None, 24)

        #Hospital Name
        text = font.render(hospital.name, True, WHITE)
        screen.blit(text, (x + 5, y + 5))

        #Capacity
        capacity, percentage = hospital.occupied_bed_summary()

        capacity_text = font.render(capacity, True, WHITE)
        screen.blit(capacity_text, (x + 5, y + 30))  # Adjust y+30 to position it below the main text

        # Draw the percentage
        percentage_text = font.render(percentage, True, WHITE)
        screen.blit(percentage_text, (x + 130, y + 30))

    # Drawing Transport Centre
    x, y = hospital_positions[""]
    pygame.draw.rect(screen, AQUAMARINE, (x, y, 150, 50))

    # Draw the border around the hospital
    border_thickness = 3  # Thickness of the border
    pygame.draw.rect(screen, AQUAMARINE, (x, y, 255, 175), border_thickness)

    font = pygame.font.Font(None, 24)
    text = font.render("Transport Centre", True, WHITE)
    screen.blit(text, (x + 5, y + 5))


def get_precomputed_color(value):
    """
    Get color from precomputed gradient table based on a normalized value.
    :param value: Normalized value between 0.0 and 1.0.
    :return: (R, G, B) tuple.
    """
    # Ensure value is clamped between 0 and 1
    value = max(0, min(value, 1))
    # Map to the closest index in the gradient table
    index = int(value * (gradient_steps - 1))
    return gradient_table[index]

#Change patient icon color based on the gradient
def tint_icon_additive(icon, color):
    tinted_icon = icon.copy()
    tint_surface = pygame.Surface(icon.get_size(), flags=pygame.SRCALPHA)
    tint_surface.fill(color + (0,))  # Add alpha if needed
    tinted_icon.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted_icon

def draw_patient(screen, patient, hospital_pos):
    if patient.nearestHospital == patient.assignedHospital:
        patient_icon = patient_icon2
    else:
        patient_icon = patient_icon1

    if patient.assignedHospital != "":
        hospital = hospital_dict.get(patient.assignedHospital)
        distance = patient.distanceToHospital
        # Define a max distance for the gradient
        max_distance = 100

        # Normalize the distance to a 0-1 range
        normalized_distance = min(distance / max_distance, 1.0)

        color = get_precomputed_color(normalized_distance)
    else:
        color = GREEN

    if patient.arrived_at_hospital and not patient.discharged:
        offset_x = (patient.queue_position % 10) * 25
        offset_y = (patient.queue_position // 10) * 25
        x, y = hospital_pos[0] + offset_x + 15, hospital_pos[1] + offset_y + 60

        tinted_icon = tint_icon_additive(patient_icon, color)
        screen.blit(tinted_icon, (x - patient_icon.get_width() // 2, y - patient_icon.get_height() // 2))
    else:
        x, y = patient.aniGpsPos
        tinted_icon = tint_icon_additive(patient_icon, color)
        screen.blit(tinted_icon, (x - patient_icon.get_width() // 2, y - patient_icon.get_height() // 2))

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


def create_viridis_colormap():
    """
    Creates an inverted viridis colormap gradient.

    Returns:
        np.ndarray: A numpy array with the inverted colormap gradient.
    """
    gradient = np.linspace(0, 1, 256)  # Create 256 levels for the gradient
    viridis_colormap = plt.cm.viridis(gradient)  # Apply the viridis colormap to the gradient

    # Reverse the colormap array to invert the colors
    viridis_colormap = viridis_colormap[::-1]

    # Remove alpha channel (optional), keeping RGB channels
    viridis_colormap = viridis_colormap[:, :3]

    return viridis_colormap



def draw_colormap_legend(screen, font, position):
    """
    Draws an inverted Viridis colormap legend on the screen, with color and labels.

    Args:
        screen: The pygame screen object.
        font: The pygame font object to use for text.
        position: Tuple (x, y) for the top-left corner of the legend.
    """
    # Create the inverted viridis colormap
    viridis_colormap = create_viridis_colormap()

    x, y = position
    colormap_width = 256  # Width corresponding to the 256 color levels
    colormap_height = 30  # Height of the colormap legend

    # Position the colormap at the bottom-right corner
    colormap_x = screen.get_width() - colormap_width - 100  # 10-pixel padding from right
    colormap_y = screen.get_height() - colormap_height - 10  # 10-pixel padding from bottom

    # Create a blank surface to hold the horizontal gradient
    colormap_surface = pygame.Surface((colormap_width, colormap_height))

    # Fill the surface with the gradient (left to right)
    for i in range(colormap_width):
        # Get the color from the inverted colormap based on the x position
        color = viridis_colormap[i]  # Color corresponding to the current position in the inverted colormap
        pygame.draw.line(colormap_surface, color * 255, (i, 0), (i, colormap_height))

    # Draw the colormap on the screen
    screen.blit(colormap_surface, (colormap_x, colormap_y))

    # Optionally, add labels to indicate the value range (0 to 1 for colormap)
    label_start = font.render('0 km', True, (0, 0, 0))
    label_end = font.render('100 km', True, (0, 0, 0))

    # Position the labels
    screen.blit(label_start, (colormap_x - 60, colormap_y))
    screen.blit(label_end, (colormap_x + colormap_width - label_end.get_width() + 85, colormap_y))
