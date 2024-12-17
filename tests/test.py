import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import app
client = TestClient(app)

class TestHospitalRecommendation:
    def test_transport_tp_01_maternal_transport_with_special_services(self):
        """
        Test case for maternal transport with special maternal services
        Scenario: Maternal transport with cardiac and surgical special needs
        """
        payload = {
            "patientType": "Maternal",
            "specialNeedType": ["Neurology"],
            "specialNeeds": ["Northern module"],
            "bedType": "Intensive",
            "gpsPos": [0, 0],  # Adjust with actual GPS coordinates within 20KM
            "transportNeedCnt": 2
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 200
        recommended_hospitals = response.json().get("recommended_hospitals", [])
        assert len(recommended_hospitals) > 0
        # Additional assertions can be added to validate hospital recommendations

    def test_transport_tp_02_neonatal_transport_no_special_services(self):
        """
        Test case for neonatal transport without special services
        Scenario: Neonatal transport with intermediate NICU beds
        """
        payload = {
            "patientType": "Neonatal",
            "specialNeedType": [],
            "specialNeeds": [],
            "bedType": "Intermediate",
            "gpsPos": [50, 50],  # Coordinates outside 20KM
            "transportNeedCnt": 1
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 200
        recommended_hospitals = response.json().get("recommended_hospitals", [])
        assert len(recommended_hospitals) > 0

    def test_transport_tp_03_maternal_transport_delivery_risk(self):
        """
        Test case for maternal transport with high delivery risk
        Scenario: Maternal transport with risk of delivery within 24 hours
        """
        payload = {
            "patientType": "Maternal",
            "specialNeedType": [],
            "specialNeeds": [],
            "bedType": "Intensive",
            "gpsPos": [0, 0],  # Adjust with actual GPS coordinates within 20KM
            "transportNeedCnt": 1,
            "del24HrPlus": True
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 200
        recommended_hospitals = response.json().get("recommended_hospitals", [])
        assert len(recommended_hospitals) > 0

    def test_transport_tp_04_neonatal_transport_special_services(self):
        """
        Test case for neonatal transport with special cardiac/neuro services
        Scenario: Neonatal transport with cardiac and neuro special needs
        """
        payload = {
            "patientType": "Neonatal",
            "specialNeedType": ["Neurology"],
            "specialNeeds": ["Northern module"],
            "bedType": "Intensive",
            "gpsPos": [50, 50],  # Coordinates outside 20KM
            "transportNeedCnt": 3
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 200
        recommended_hospitals = response.json().get("recommended_hospitals", [])
        assert len(recommended_hospitals) > 0

    def test_transport_tp_05_nicu_occupancy_check(self):
        """
        Test case for NICU occupancy check
        Scenario: Check NICU occupancy during admission
        """
        # Note: This might require mock data or a specific endpoint to simulate NICU radar
        payload = {
            "patientType": "Neonatal",
            "specialNeedType": [],
            "specialNeeds": [],
            "bedType": "Intensive",
            "gpsPos": [0, 0],
            "transportNeedCnt": 1
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 200
        recommended_hospitals = response.json().get("recommended_hospitals", [])
        assert len(recommended_hospitals) > 0

    def test_transport_tp_06_birthing_center_occupancy(self):
        """
        Test case for birthing center occupancy check
        Scenario: No transport needed, check birthing center availability
        """
        payload = {
            "patientType": "Maternal",
            "gpsPos": [43.70011, -79.4163],
            "transportNeedCnt": 0,
            "specialNeedType": ["Neurology"],
            "specialNeeds": [""],
            "del24HrPlus": False,
            "bedType": "Intensive",
            "homeHospital": "CUSM"
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 200
        recommended_hospitals = response.json().get("recommended_hospitals", [])
        assert len(recommended_hospitals) > 0

    def test_transport_tp_07_neonatal_intermediate_bed(self):
        """
        Test case for neonatal transport with intermediate NICU bed
        Scenario: Neonatal transport with intermediate bed within 20KM
        """
        payload = {
            "patientType": "Neonatal",
            "specialNeedType": [],
            "specialNeeds": [],
            "bedType": "Intermediate",
            "gpsPos": [0, 0],  # Adjust with actual GPS coordinates within 20KM
            "transportNeedCnt": 1
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 200
        recommended_hospitals = response.json().get("recommended_hospitals", [])
        assert len(recommended_hospitals) > 0

    def test_transport_tp_08_maternal_multiple_special_needs(self):
        """
        Test case for maternal transport with multiple special needs
        Scenario: Maternal transport with cardiac and fetal malformation, high delivery risk
        """
        payload = {
            "patientType": "Maternal",
            "gpsPos": [43.70011, -79.4163],
            "transportNeedCnt": 0,
            "specialNeedType": ["Neurology"],
            "specialNeeds": [""],
            "del24HrPlus": False,
            "bedType": "Intensive",
            "homeHospital": "CUSM"
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 200
        recommended_hospitals = response.json().get("recommended_hospitals", [])
        assert len(recommended_hospitals) > 0

    # TODO: Fix this test. It should return a validation error
    def test_transport_tp_09_invalid_patient_type(self):
        """
        Test case for invalid patient type
        Scenario: Attempt to use an invalid patient type
        """
        payload = {
            "patientType": "WeirdType",
            "specialNeedType": ["Cardiac", "Fetal malformation"],
            "specialNeeds": [],
            "bedType": "Intensive",
            "gpsPos": [0, 0],
            "transportNeedCnt": 3,
            "del24HrPlus": True
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 422  # Validation error expected

    def test_transport_tp_10_invalid_bed_type(self):
        """
        Test case for invalid bed type
        Scenario: Attempt to use an invalid bed type
        """
        payload = {
            "patientType": "Neonatal",
            "specialNeedType": [],
            "specialNeeds": [],
            "bedType": "Easy",
            "gpsPos": [0, 0],
            "transportNeedCnt": 1
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 422  # Validation error expected

    def test_transport_tp_11_missing_required_fields(self):
        """
        Test case for missing required fields
        Scenario: Attempt to submit request with missing required fields
        """
        payload = {
            "specialNeedType": [],
            "bedType": "Intensive",
            "gpsPos": [0, 0],
            "transportNeedCnt": 1
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 422  # Validation error expected

    def test_transport_tp_12_invalid_transport_need_count(self):
        """
        Test case for invalid transport need count (non-integer)
        Scenario: Attempt to use a float value for transportNeedCnt
        """
        payload = {
            "patientType": "Neonatal",
            "specialNeedType": ["Cardiac", "Neuro"],
            "specialNeeds": ["Northern module"],
            "bedType": "Intensive",
            "gpsPos": [0, 0],
            "transportNeedCnt": 2.8
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 422  # Validation error expected

    def test_transport_tp_13_invalid_patient_type_type(self):
        """
        Test case for invalid patient type data type
        Scenario: Attempt to use an integer for patientType
        """
        payload = {
            "patientType": 1,
            "specialNeedType": ["Cardiac", "Neuro"],
            "specialNeeds": ["Northern module"],
            "bedType": "Intensive",
            "gpsPos": [0, 0],
            "transportNeedCnt": 3
        }
        
        response = client.post("/recommendation/", json=payload)
        
        assert response.status_code == 422  # Validation error expected

# Optionally, add fixtures or setup/teardown methods as needed