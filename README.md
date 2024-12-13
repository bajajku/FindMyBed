
- [**Setup Guide: Build and Run-Time Environment**](#setup-guide-build-and-run-time-environment)
  - [**Step 1: Prerequisites**](#step-1-prerequisites)
  - [**Step 2: Clone the Repository**](#step-2-clone-the-repository)
  - [**Step 3: Set Up a Virtual Environment**](#step-3-set-up-a-virtual-environment)
    - [**For Linux/macOS:**](#for-linuxmacos)
    - [**For Windows:**](#for-windows)
  - [**Step 4: Install Required Libraries**](#step-4-install-required-libraries)
  - [**Step 5: Build and Run the Simulator**](#step-5-build-and-run-the-simulator)
    - [**To Build and Run the Application:**](#to-build-and-run-the-application)

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
   python3 -m venv env
   ```
2. Activate the virtual environment:
   ```bash
   source env/bin/activate
   ```

### **For Windows:**
1. Create the virtual environment:
   ```bash
   python -m venv env
   ```
2. Activate the virtual environment:
   ```bash
   env\Scripts\activate
   ```

---

## **Step 4: Install Required Libraries**

With the virtual environment activated, install all the necessary dependencies listed in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

## **Step 5: Build and Run the Simulator**

### **To Build and Run the Application:**

1. Ensure the virtual environment is active:
   - **For Linux/macOS:**
     ```bash
     source env/bin/activate
     ```
   - **For Windows:**
     ```bash
     env\Scripts\activate
     ```

2. Run the application:
   ```bash
   python main.py
   ```

---


