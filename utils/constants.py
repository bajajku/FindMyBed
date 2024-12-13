from typing import List
from datetime import  datetime

# Patient Types
PATIENT_TYPE: List[str] = ["Maternal", "Neonatal"]

# Special Needs Lists
MATERNAL_SPECIAL_NEEDS: List[str] = [
    "ICU admission",
    "Surgery",
    "Cardiac problems",
    "High-risk pregnancy",
    "Excessive blood loss",
    "Cardiac surgery",
    "General surgery",
    "Endocrinology",
    "Hematology",
    "Neuromuscular problems",
    "Other (explain)"
]

NEONATAL_SPECIAL_NEEDS: List[str] = [
    "Prematurity (GA<26 weeks)",
    "Prematurity (GA>26 weeks)",
    "Neurology",
    "Neurosurgery",
    "Cardiology",
    "Cardiac Surgery",
    "General Surgery",
    "Endocrinology",
    "Genetic",
    "Gastroenterology",
    "Plastic Surgery",
    "Respirology",
    "Hematology",
    "Nephrology",
    "ECMO",
    "ENT (ear-nose-throat)",
    "Urology",
    "Infectious diseases",
    "Ophthalmology",
    "Other (explain)"
]

# Bed Types
BED_TYPE: List[str] = ["Intensive", "Intermediate"]

# Time Constants
ARRIVAL_TIMES: List[int] = [9, 14, 21]

# Hospital Configuration
HOSPITALS_CONFIG = [
    {
        "name": "CHU-SJ",
        "coords": (45.5035, -73.6245),
        "percentage": 0.2202
    },
    {
        "name": "CHUQ",
        "coords": (46.7985, -71.2458),
        "percentage": 0.1905
    },
    {
        "name": "CHUS",
        "coords": (45.4472, -71.8706),
        "percentage": 0.1295
    },
    {
        "name": "CUSM",
        "coords": (45.4719, -73.6027),
        "percentage": 0.1943
    },
    {
        "name": "HGJ",
        "coords": (45.4978, -73.6285),
        "percentage": 0.1562
    },
    {
        "name": "HMR",
        "coords": (45.5741, -73.5595),
        "percentage": 0.1093
    }
]

# Define the simulator's start date
START_DATE = datetime.strptime("2023-01-01", "%Y-%m-%d")

#Animation
SCREEN_WIDTH, SCREEN_HEIGHT = 1320, 800
WHITE, BLUE, RED, GREEN = (255, 255, 255), (0,0,255), (255, 0, 0), (0,255,0)
AQUAMARINE = (102, 205, 170)

# Define hospital positions for visualization
hospital_positions = {
    "CHU-SJ": (10, 72),
    "CHUQ": (1050, 100),
    "CHUS": (10, 670),
    "CUSM": (1050, 550),
    "HGJ": (10, 340),
    "HMR": (10, 530),
    "": (1050,335)
}

# Define the simulator's start date
START_DATE = datetime.strptime("2023-01-01", "%Y-%m-%d")

ASSUMPTIONS = "Simulation assumes historical trends for patient arrivals and discharges."
HYPERPARAMETERS = {
    "Simulation Duration": "One year",
    "Arrival Rate": "Based on historical hourly averages per hospital",
    "Discharge Rate": "Based on historical patterns"
}

# Constants for button dimensions and colors
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40
BUTTON_COLOR = (0, 0, 255)
PAUSED_COLOR = (255, 0, 0)
PLAY_COLOR = (0, 255, 0)