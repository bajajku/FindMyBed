from models.hospital import Hospital
from models.patient import Patient


BEDTYPE_INDEX = {"Intensive" : 0, "Intermediate" : 1, "BirthCenter" : 2, "Antepartum" : 3, "Postpartum" : 4}

def get_bed_index(bedType: str) -> int:
    return BEDTYPE_INDEX[bedType]

def add_patient(hospital: Hospital, patient: Patient) -> None:
    hospital.patients[patient.bedType].append(patient)
    hospital.available_beds[get_bed_index(patient.bedType)] -= 1

def admit_patient(hospital: Hospital, patient: Patient) -> bool:
    """Handles the admission of a patient to the hospital."""
    if patient.patientType == "Maternal":
        # Handle maternal patient admission
        if not hospital.nicu_required(patient) and hospital.get_occupancy_rate_per_patientType_per_bedType(patient):
            if not patient.del24HrPlus:
                patient.bedType = "BirthCenter"  # Assign bed type
            else:
                patient.bedType = "Antepartum"  # Assign different bed type

            add_patient(hospital, patient)
            patient.assignedHospital = hospital.name
            return True
    else:
        # Handle NICU patient admission
        if hospital.get_occupancy_rate_per_patientType_per_bedType(patient) and patient.nicu_needed:
            add_patient(hospital, patient)
            patient.assignedHospital = hospital.name
            return True

    return False
