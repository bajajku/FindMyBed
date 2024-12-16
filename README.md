- [**Setup Guide: Build and Run-Time Environment**](#setup-guide-build-and-run-time-environment)
  - [**Step 1: Prerequisites**](#step-1-prerequisites)
  - [**Step 2: Clone the Repository**](#step-2-clone-the-repository)
  - [**Step 3: Set Up a Virtual Environment**](#step-3-set-up-a-virtual-environment)
    - [**For Linux/macOS:**](#for-linuxmacos)
    - [**For Windows:**](#for-windows)
  - [**Step 4: Install Required Libraries**](#step-4-install-required-libraries)
  - [**Step 5: Build and Run Commands**](#step-5-build-and-run-commands)
    - [**For Simulator:**](#for-simulator)
    - [**For API:**](#for-api)
- [**Libraries Used**](#libraries-used)


# **Setup Guide: Build and Run-Time Environment**

This document provides detailed instructions for setting up the build and run-time environment for the project.

---

## **Step 1: Prerequisites**

Ensure the following are installed on your system:

- **Python 3.x** (recommended version: 3.8 or later)
- **Git**
- A terminal or command prompt 

---

## **Step 2: Clone the Repository**

1. Open your terminal or command prompt.
2. Clone the project repository using the following command:
   ```bash
   git clone https://github.com/bajajku/AI_DSA.git
   ```
3. Navigate to the project directory:
   ```bash
   cd AI_DSA
   ```

---

## **Step 3: Set Up a Virtual Environment**

A virtual environment is required to isolate dependencies and prevent conflicts with global packages.

### **For Linux/macOS:**
1. Create the virtual environment:
   ```bash
   python3 -m venv venv
   ```
2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

### **For Windows:**
1. Create the virtual environment:
   ```bash
   python -m venv env
   ```
2. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```

---

## **Step 4: Install Required Libraries**

With the virtual environment activated, install all the necessary dependencies listed in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

## **Step 5: Build and Run Commands**

### **For Simulator:**
   ```bash
   python main.py
   ```
### **For API:**
   ```bash
   uvicorn api:app --reload
   ```


---

# **Libraries Used**
Below is a list of libraries used in this project, along with their versions and specific purposes within the context of the project:

| Library           | Version   | Purpose                                                                                          |
|--------------------|-----------|--------------------------------------------------------------------------------------------------|
| **fastapi**        | 0.115.6   | To create RESTful APIs for hospital and patient data processing.                                |
| **geopy**          | 2.3.0     | To calculate distances between patient locations and hospitals for optimal assignment.          |
| **matplotlib**     | 3.10.0    | To visualize hospital occupancy rates and patient distributions over time.                      |
| **numpy**          | 2.2.0     | For numerical computations, such as calculating statistical metrics and handling large datasets.|
| **pandas**         | 2.2.3     | For managing and analyzing hospital records, patient data, and simulation results.              |
| **postalcodes_ca** | 0.0.9     | To validate and process Canadian postal codes.|
| **pydantic**       | 2.10.3    | To validate data models for patient and hospital attributes and ensure consistent API responses. |
| **pygame**         | 2.6.1     |To create animations that visually simulate patient transfers and hospital operations.
| **pytest**         | 8.3.3     |To implement unit tests.
| **PyYAML**         | 6.0.2     | To load configuration settings, such as occupancy thresholds, from YAML files.                 |
| **scipy**          | 1.14.1    | For fitting probability distributions to patient flow and hospital bed occupancy data.          |
| **tabulate**       | 0.9.0     | To display hospital capacity and patient assignment summaries in a tabular format.              |
| **transitions**    | 0.9.2     | To manage state transitions in hospital admission.
| **openpyxl**       | 3.1.5     | To read and write Excel files for exporting and analyzing hospital bed and patient statistics.   |

---