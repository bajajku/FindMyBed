from models.hospital import Hospital
from models.patient import Patient

# Mapping of bed types to their corresponding index in hospital's available_beds array
BEDTYPE_INDEX = {"Intensive" : 0, "Intermediate" : 1, "BirthCenter" : 2, "Antepartum" : 3, "Postpartum" : 4}

def get_bed_index(bedType: str) -> int:
    """
    Get the index of a specific bed type in the hospital's available_beds array.

    Args:
        bedType (str): The type of bed (e.g., "Intensive", "Intermediate").

    Returns:
        int: The index corresponding to the given bed type.
    """
    return BEDTYPE_INDEX[bedType]

def add_patient(hospital: Hospital, patient: Patient) -> None:
    """
    Add a patient to a hospital's patient list and update the hospital's available beds.

    Args:
        hospital (Hospital): The hospital where the patient will be added.
        patient (Patient): The patient to be added.
    Process:
        Appends the patient to the hospital's list of patients for the given bed type.
        Decrements the count of available beds for the corresponding bed type.

    """
    hospital.patients[patient.bedType].append(patient)
    hospital.available_beds[get_bed_index(patient.bedType)] -= 1

def admit_patient(hospital: Hospital, patient: Patient) -> bool:
    """
    Handles the admission of a patient to the hospital.

    Args:
        hospital (Hospital): The hospital where the patient will be admitted.
        patient (Patient): The patient seeking admission.

    Returns:
        bool: True if the patient was successfully admitted, False otherwise.
    """
    if patient.patientType == "Maternal":
        # Handle maternal patient admission
        if hospital.get_occupancy_rate_per_patientType_per_bedType(patient):
            if not patient.del24HrPlus:
                patient.bedType = "BirthCenter"  # Assign bed type
            else:
                patient.bedType = "Antepartum"  # Assign different bed type

            add_patient(hospital, patient)
            patient.assignedHospital = hospital.name
            return True
    else:
        # Handle neonatal patient admission
        if hospital.get_occupancy_rate_per_patientType_per_bedType(patient):
            add_patient(hospital, patient)
            patient.assignedHospital = hospital.name
            return True

    return False
