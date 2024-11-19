import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from utils.constants import *


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
        plt.text(0.5, 0.97, 'Hospital Occupancy Report',
                 horizontalalignment='center', fontsize=16, fontweight='bold')
        
        # Table of Contents
        plt.text(0.1, 0.90, 'Table of Contents', fontsize=14, fontweight='bold')

        # Monthly Occupancy Rates Section
        plt.text(0.1, 0.85, '1. Monthly Occupancy Rates', fontsize=12)
        plt.text(0.15, 0.80, '- Intensive Occupancy Rate Distribution', fontsize=10)
        plt.text(0.15, 0.77, '- Intermediate Occupancy Rate Distribution', fontsize=10)

        # Yearly Occupancy Rates Section
        plt.text(0.1, 0.70, '2. Yearly Occupancy Rates', fontsize=12)
        plt.text(0.15, 0.65, '- Intensive Occupancy Rate Distribution', fontsize=10)
        plt.text(0.15, 0.62, '- Intermediate Occupancy Rate Distribution', fontsize=10)

        # Total Patient Distributions Section
        plt.text(0.1, 0.55, '3. Total Patient Distributions', fontsize=12)
        plt.text(0.15, 0.50, '- Yearly Total Patient Distribution', fontsize=10)
        plt.text(0.15, 0.47, '- Acceptance Probability for Total Patients', fontsize=10)
        plt.text(0.15, 0.44, '- Accepted Total Patients by Distance for Each Hospital', fontsize=10)
        plt.text(0.15, 0.41, '- Probability Distribution of Closest Distances (All Patients)', fontsize=10)
        plt.text(0.15, 0.38, '- Probability Distribution of Closest Distances (Not Admitted to Closest Hospital)',
                 fontsize=10)
        # Intensive Patient Distributions Section
        plt.text(0.1, 0.30, '4. Intensive Patient Distributions', fontsize=12)
        plt.text(0.15, 0.25, '- Yearly Intensive Patient Distribution', fontsize=10)
        plt.text(0.15, 0.22, '- Acceptance Probability for Intensive Patients', fontsize=10)
        plt.text(0.15, 0.19, '- Accepted Intensive Patients by Distance for Each Hospital', fontsize=10)
        # Intermediate Patient Distributions Section
        plt.text(0.1, 0.15, '5. Intermediate Patient Distributions', fontsize=12)
        plt.text(0.15, 0.10, '- Yearly Intermediate Patient Distribution', fontsize=10)
        plt.text(0.15, 0.07, '- Acceptance Probability for Intermediate Patients', fontsize=10)
        plt.text(0.15, 0.04, '- Accepted Intermediate Patients by Distance for Each Hospital', fontsize=10)
        
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

            # Total Patient distributions
            self.add_section_header("3. Total Patient Distributions", pdf)
            self.visualizer.plot_yearly_patient_distribution(self.patients_df, type="Total", pdf=pdf)
            self.visualizer.plot_acceptance_probability(self.patients_df, type="Total", pdf=pdf)
            self.visualizer.accepted_patients_by_distance(self.patients_df, type="Total", pdf=pdf)
            # self.visualizer.probability_distribution_patients(self.patients_df,pdf)

            # Intensive Patient distributions
            self.add_section_header("4. Intensive Patient Distributions", pdf)
            self.visualizer.plot_yearly_patient_distribution(self.patients_df, type="Intensive", pdf=pdf)
            self.visualizer.plot_acceptance_probability(self.patients_df, type="Intensive", pdf=pdf)
            self.visualizer.accepted_patients_by_distance(self.patients_df, type="Intensive", pdf=pdf)

            # Intermediate Patient distributions
            self.add_section_header("5. Intermediate Patient Distributions", pdf)
            self.visualizer.plot_yearly_patient_distribution(self.patients_df, type="Intermediate", pdf=pdf)
            self.visualizer.plot_acceptance_probability(self.patients_df, type="Intermediate", pdf=pdf)
            self.visualizer.accepted_patients_by_distance(self.patients_df, type="Intermediate", pdf=pdf)