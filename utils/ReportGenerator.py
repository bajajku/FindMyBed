import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches

import seaborn as sns
import pandas as pd
import numpy as np
from config import REPORT
from utils.constants import *

import scipy as sp
from scipy.stats import norm

class ReportGenerator:

    def __init__(self, results_df, patients_df, report_path, visualizer):
        self.assumptions = """
    Assumptions:

    - Probability Calculations: 
      Patient arrival and discharge probabilities are calculated by analyzing historical data patterns. These probabilities 
      are applied to generate patient flow, ensuring that patient distribution reflects typical trends.

    - Patient Allocation: 
      To align with real-world conditions, the probability of assigning a patient to a specific hospital is influenced by factors 
      such as the distance between hospitals and patients, occupancy rates (intensive and intermediate), and specific service 
      requirements (e.g., NICU needs).
    """
        self.hyperparameters = """
    Hyperparameters:

    - Simulation Duration: Two years
    - Arrival Rate: Based on historical averages per hospital for each time slot (9:00, 14:00, 21:00)
    - Discharge Rate: Based on historical patterns
    """
        self.header = "Assumptions and Hyperparameters"
        self.title = 'Hospital Occupancy Report'
        self.results_df = results_df
        self.patients_df = patients_df
        self.report_path = report_path
        self.visualizer = visualizer


    def generate_report_header(self,pdf):
        fig = plt.figure(figsize=(12, 8))
        plt.axis('off')

        # Define assumptions and hyperparameters
        assumptions_text = self.assumptions
        
        hyperparameters_text = self.hyperparameters
        # Header text
        header_text = self.header

        # Display header, assumptions, and hyperparameters in the plot
        plt.text(0.5, 0.95, header_text, ha='center', fontsize=14, fontweight='bold')
        plt.text(0.1, 0.8, assumptions_text, fontsize=10, va='top', wrap=True)
        plt.text(0.1, 0.4, hyperparameters_text, fontsize=10, va='top', wrap=True)

        # Save the figure to the PDF and close it
        pdf.savefig(fig)
        plt.close(fig)


    def create_table_of_contents(self, pdf):
        """
        Creates a table of contents page
        """
        fig = plt.figure(figsize=(12, 8))
        plt.axis('off')
        
        # Title
        plt.text(0.5, 0.95, self.title, 
                horizontalalignment='center', fontsize=16, fontweight='bold')
        
        # Table of Contents
        plt.text(0.1, 0.85, 'Table of Contents', fontsize=14, fontweight='bold')

        # Monthly Occupancy Rates Section
        plt.text(0.1, 0.75, '1. Monthly Occupancy Rates', fontsize=12)
        plt.text(0.15, 0.70, '- Intensive Occupancy Rate Distribution', fontsize=10)
        plt.text(0.15, 0.67, '- Intermediate Occupancy Rate Distribution', fontsize=10)
        
        # Yearly Occupancy Rates Section
        plt.text(0.1, 0.60, '2. Yearly Occupancy Rates', fontsize=12)
        plt.text(0.15, 0.55, '- Intensive Occupancy Rate Distribution', fontsize=10)
        plt.text(0.15, 0.52, '- Intermediate Occupancy Rate Distribution', fontsize=10)

        # Patient Distributions Section
        plt.text(0.1, 0.45, '3. Patient Distributions', fontsize=12)
        plt.text(0.15, 0.40, '- Yearly Patient Distribution', fontsize=10)
        plt.text(0.15, 0.37, '- Acceptance Probability for Nearby Patients', fontsize=10)
        plt.text(0.15, 0.34, '- Accepted Patients by Distance for Each Hospital', fontsize=10)
        plt.text(0.15, 0.31, '- Probability Distribution of Closest Distances (All Patients)', fontsize=10)
        plt.text(0.15, 0.28, '- Probability Distribution of Closest Distances (Not Admitted to the Closest Hospital)', fontsize=10)

        # NICU Patient Distributions Section
        plt.text(0.1, 0.20, '4. NICU Patient Distributions', fontsize=12)
        plt.text(0.15, 0.15, '- Yearly NICU Patient Distribution', fontsize=10)
        plt.text(0.15, 0.12, '- Acceptance Probability for NICU Patients', fontsize=10)
        plt.text(0.15, 0.09, '- Accepted NICU Patients by Distance for Each Hospital', fontsize=10)
        
        # Save the Table of Contents to the PDF
        pdf.savefig(fig)
        plt.close(fig)

    def add_section_header(self, title: str, pdf):
        """
        Adds a section header page
        """
        fig = plt.figure(figsize=(12, 8))
        plt.axis('off')
        plt.text(0.5, 0.5, title, 
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=16,
                fontweight='bold')
        pdf.savefig()
        plt.close()

    def create_pdf_report(self):
        """
        Creates a single PDF with table of contents and all plots
        """
        with PdfPages(self.report_path) as pdf:


            # Add table of contents
            self.create_table_of_contents(pdf)
            # Generate report header
            self.generate_report_header(pdf)

            # Monthly occupancy plots
            self.add_section_header("1. Monthly Occupancy Rates", pdf)
            self.visualizer.plot_monthly_occupancy_probability(self.results_df, 'Intensive Occupancy Rate', 'Monthly Probability Distribution Intensive',pdf)
            self.visualizer.plot_monthly_occupancy_probability(self.results_df,'Intermediate Occupancy Rate', 'Monthly Probability Distribution Intermediate', pdf)

            # Yearly occupancy plots
            self.add_section_header("2. Yearly Occupancy Rates", pdf)
            self.visualizer.plot_yearly_occupancy_probability(self.results_df,'Intensive Occupancy Rate', 'Yearly Probability Distribution Intensive', pdf)
            self.visualizer.plot_yearly_occupancy_probability(self.results_df,'Intermediate Occupancy Rate', 'Yearly Probability Distribution Intermediate', pdf)

            # Patient distributions
            self.add_section_header("3. Patient Distributions", pdf)
            self.visualizer.plot_yearly_patient_distribution(self.patients_df,"Yearly Patients Distribution", pdf)
            self.visualizer.plot_acceptance_probability(self.patients_df,"Acceptance Probability for Patients in the Vicinity", pdf)
            self.visualizer.accepted_patients_by_distance(self.patients_df,pdf)
            self.visualizer.probability_distribution_patients(self.patients_df,pdf)

            # NICU Patient distributions
            self.add_section_header("4. NICU Patient Distributions", pdf)
            self.visualizer.plot_yearly_patient_distribution_NICU(self.patients_df,"Yearly NICU Patients Distribution", pdf)
            self.visualizer.plot_acceptance_probability_NICU(self.patients_df,"Acceptance Probability for NICU Patients in the Vicinity", pdf)
            self.visualizer.accepted_patients_by_distance_NICU(self.patients_df,pdf)