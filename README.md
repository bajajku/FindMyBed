- [**Setup Guide: Build and Run-Time Environment**](#setup-guide-build-and-run-time-environment)
  - [**Step 1: Configure `config.yaml`**](#step-1-configure-configyaml)
    - [**Configuration Parameters**](#configuration-parameters)
      - [**Simulation Parameters**](#simulation-parameters)
      - [**Input File Paths**](#input-file-paths)
      - [**Output File Paths**](#output-file-paths)
      - [**Hospital Occupancy Thresholds**](#hospital-occupancy-thresholds)
    - [**Steps to Set Up `config.yaml`**](#steps-to-set-up-configyaml)
  - [**Step 2: Prerequisites**](#step-2-prerequisites)
  - [**Step 3: Clone the Repository**](#step-3-clone-the-repository)
  - [**Step 4: Set Up a Virtual Environment**](#step-4-set-up-a-virtual-environment)
    - [**For Linux/macOS:**](#for-linuxmacos)
    - [**For Windows:**](#for-windows)
  - [**Step 5: Install Required Libraries**](#step-5-install-required-libraries)
  - [**Step 6: Build and Run Commands**](#step-6-build-and-run-commands)
    - [**For Simulator:**](#for-simulator)
    - [**For API:**](#for-api)
    - [**For API unit tests:**](#for-api-unit-tests)
- [**Libraries Used**](#libraries-used)





# **Setup Guide: Build and Run-Time Environment**

This document provides detailed instructions for setting up the build and run-time environment for the project.

---
## **Step 1: Configure `config.yaml`**

The `config.yaml` file is a configuration file for the simulator. It defines parameters for the simulation, paths to input and output files, and occupancy thresholds for hospitals. Below are the details and steps to set it up:


### **Configuration Parameters**

#### **Simulation Parameters**
- **`NUMBER_OF_DAYS`**: The number of days the simulation will run. Adjust this to match the duration required for the simulation.

#### **Input File Paths**
- **`EXCEL_PATH`**:  Path to the hospital data, including incoming rate, discharge rate, and capacity.
- **`EXCEL_PATH_NEWDATA`**: Path to the patient data, used to calculate the birth rate per FSA and generate patients based on this data.

#### **Output File Paths**
- **`REPORT`**: Path where the PDF report will be generated.
- **`TABLE`**: Path where the patient assignment tables will be saved in Excel format.

#### **Hospital Occupancy Thresholds**
- These thresholds are used to check the occupancy rate before assigning patients, ensuring hospitals do not exceed safe limits for patient care.
- **`INTENSIVE_OCCUPANCY_THRESHOLDS`**: Maximum occupancy rate allowed for intensive beds at each hospital. 
- **`INTERMEDIATE_OCCUPANCY_THRESHOLDS`**: Maximum occupancy rate allowed for intermediate beds at each hospital.

### **Steps to Set Up `config.yaml`**
1. Create a `config.yaml` file in the project root directory if it doesn’t already exist.
2. Copy the above example content into the file.
3. Update the paths (`EXCEL_PATH`, `EXCEL_PATH_NEWDATA`, `REPORT`, `TABLE`) to match the directory structure on your system.
4. Adjust the `NUMBER_OF_DAYS` value and occupancy thresholds as needed based on simulation requirements.


## **Step 2: Prerequisites**

Ensure the following are installed on your system:

- **Python 3.x** (recommended version: 3.10 or later to support the latest libraries)
- **Git**
- A terminal or command prompt 

---

## **Step 3: Clone the Repository**

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

## **Step 4: Set Up a Virtual Environment**

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
   python -m venv venv
   ```
2. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```

---

## **Step 5: Install Required Libraries**

With the virtual environment activated, install all the necessary dependencies listed in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

## **Step 6: Build and Run Commands**

### **For Simulator:**
   ```bash
   python main.py
   ```

### **For API:**
   ```bash
   uvicorn api:app --reload
   ```

### **For API unit tests:**
  ```bash
  python tests/test.py
 ```
---

# **Libraries Used**

Below is a list of libraries used in this project, along with their versions and specific purposes within the context of the project:

| Library           | Version   | Purpose                                                                                          |
|--------------------|-----------|--------------------------------------------------------------------------------------------------|
| **fastapi**        | 0.115.6   | To create RESTful APIs for hospital and patient data processing.              
| **uvicorn**        | 0.32.1    | To serve FastAPI applications. |
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
| **openpyxl**       | 3.1.5     | To read and write Excel files for exporting and analyzing hospital bed and patient statistics.   

---


