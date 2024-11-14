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


def generate_report_header(pdf, assumptions, hyperparameters):
    fig = plt.figure(figsize=(12, 8))
    plt.axis('off')
    
    # Header text
    header_text = "Assumptions and Hyperparameters\n\n"
    
    # Combine hyperparameters into a single string
    hyperparameters_text = ""
    for param, desc in hyperparameters.items():
        hyperparameters_text += f"\n{param}: {desc}"
    
    # Display header, assumptions, and hyperparameters in the plot
    plt.text(0.5, 0.9, header_text, horizontalalignment='center', fontsize=14, fontweight='bold')
    plt.text(0.5, 0.75, f"Assumptions: {assumptions}", horizontalalignment='center', fontsize=12, wrap=True)
    plt.text(0.5, 0.55, hyperparameters_text, horizontalalignment='center', fontsize=12, wrap=True)
    
    # Save the figure to the PDF and close it
    pdf.savefig(fig)
    plt.close(fig)


def create_table_of_contents(pdf: PdfPages):
    """
    Creates a table of contents page
    """
    fig = plt.figure(figsize=(12, 8))
    plt.axis('off')
    
    # Title
    plt.text(0.5, 0.95, 'Hospital Occupancy Report', 
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

def add_section_header(title: str, pdf: PdfPages):
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

def create_pdf_report(results_df: pd.DataFrame, patients_df: pd.DataFrame):
    """
    Creates a single PDF with table of contents and all plots
    """
    with PdfPages(REPORT) as pdf:


        # Add table of contents
        create_table_of_contents(pdf)
        # Generate report header
        generate_report_header(pdf, ASSUMPTIONS, HYPERPARAMETERS)

        # Monthly occupancy plots
        add_section_header("1. Monthly Occupancy Rates", pdf)
        plot_monthly_occupancy_probability(results_df, 'Intensive Occupancy Rate', 'Monthly Probability Distribution Intensive',pdf)
        plot_monthly_occupancy_probability(results_df, 'Intermediate Occupancy Rate', 'Monthly Probability Distribution Intermediate',pdf)

        # Yearly occupancy plots
        add_section_header("2. Yearly Occupancy Rates", pdf)
        plot_yearly_occupancy_probability(results_df, 'Intensive Occupancy Rate', 'Yearly Probability Distribution Intensive', pdf)
        plot_yearly_occupancy_probability(results_df, 'Intermediate Occupancy Rate', 'Yearly Probability Distribution Intermediate', pdf)

        # Patient distributions
        add_section_header("3. Patient Distributions", pdf)
        plot_yearly_patient_distribution(patients_df,"Yearly Patients Distribution",pdf)
        plot_acceptance_probability(patients_df,"Acceptance Probability for Patients in the Vicinity",pdf)
        accepted_patients_by_distance(patients_df, pdf)
        probability_distribution_patients(patients_df, pdf)
        # NICU Patient distributions
        add_section_header("4. NICU Patient Distributions", pdf)
        plot_yearly_patient_distribution_NICU(patients_df, "Yearly NICU Patients Distribution", pdf)
        plot_acceptance_probability_NICU(patients_df, "Acceptance Probability for NICU Patients in the Vicinity", pdf)
        accepted_patients_by_distance_NICU(patients_df, pdf)

def generate_statistics_table(hospitals_data, pdf: PdfPages, title):

    # Create a new figure for the table
    plt.figure(figsize=(12, 6))
    plt.axis('off')  # Hide axes

    # Define column labels
    column_labels = ['Hospital Name', 'Average', 'Standard Deviation']

    # Add the table to the figure
    table = plt.table(cellText=hospitals_data, colLabels=column_labels, loc='center', cellLoc='center', colLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    # Set title
    plt.title(title, fontsize=14)

    # Save the table page to the PDF
    pdf.savefig()
    plt.close()

def plot_monthly_occupancy_probability(results_df: pd.DataFrame, rate_type, title, pdf: PdfPages):
    # Ensure 'Date' column is in datetime format to extract the month
    results_df['Date'] = pd.to_datetime(results_df['Date'])
    results_df['Year'] = results_df['Date'].dt.year

    # Define x-values for occupancy rates, which are expected to be between 0 and 1
    x_values = np.linspace(0, 1, 100)
    unique_months = sorted(results_df['Month'].unique())  # Get unique months in sorted order

    for month in unique_months:
        plt.figure(figsize=(12, 6))
        
        # Filter data for the specific month across all years
        month_data = results_df[results_df['Month'] == month]
        hospitals = month_data['Hospital'].unique()

        table_data = []
        for hospital in hospitals:
            # Calculate the average occupancy rate for each year for this hospital and month
            hospital_monthly_data = month_data[month_data['Hospital'] == hospital].groupby('Year')[rate_type].mean().dropna()
            
            # Check if there is enough data to fit a distribution (at least 2 data points)
            if len(hospital_monthly_data) > 1:
                # Fit a normal distribution to the average monthly occupancy data across years
                mu, std = norm.fit(hospital_monthly_data)

                # Calculate PDF values
                pdf_values = norm.pdf(x_values, mu, std)

                # Normalize PDF values only if the sum is non-zero
                pdf_sum = np.sum(pdf_values)
                if pdf_sum > 0:
                    pdf_values /= pdf_sum  # Normalize
                else:
                    pdf_values = np.zeros_like(pdf_values)  # Avoid division by zero

                # Plot the normalized PDF
                plt.plot(x_values, pdf_values, label=f'{hospital} (μ={mu:.2f}, σ={std:.2f})')
                table_data.append([hospital, f'{mu:.2f}', f'{std:.2f}'])

        # Title and labels
        plt.title(f'{title} for Month {month:02d}')
        plt.xlabel(rate_type.replace("_", " ").title())
        plt.ylabel('Probability Density')
        plt.xticks(np.linspace(0, 1, 21))
        plt.legend()
        
        # Save each plot in the PDF
        pdf.savefig()
        plt.close()
        # Add the table as a separate page if there is data
        if table_data:
            table_title = f'{title} - Statistics Table for Month {month:02d}'
            generate_statistics_table(table_data, pdf, table_title)

def plot_yearly_occupancy_probability(results_df: pd.DataFrame,rate_type, title, pdf: PdfPages):
    # Ensure 'Date' column is in datetime format to extract the year
    results_df['Date'] = pd.to_datetime(results_df['Date'])
    results_df['Year'] = results_df['Date'].dt.year
    
    # Define x-values for the occupancy rate, which is expected to be between 0 and 1
    x_values = np.linspace(0, 1, 100)
    plt.figure(figsize=(12, 6))
    
    # Get unique hospitals for plotting
    hospitals = results_df['Hospital'].unique()

    # Store data for the table
    table_data = []

    for hospital in hospitals:
        # Group by year to get yearly data for each hospital
        yearly_data = results_df[results_df['Hospital'] == hospital].groupby('Year')[rate_type].mean().dropna()
        
        # Check if there's enough data to fit a distribution (at least 2 data points)
        if len(yearly_data) > 1:
            # Fit a normal distribution to the yearly occupancy rates
            mu, std = norm.fit(yearly_data)
            
            # Calculate PDF values
            pdf_values = norm.pdf(x_values, mu, std)
            
            # Normalize PDF values so that the area under the curve sums to 1
            pdf_values /= np.sum(pdf_values)
            
            # Plot the normalized PDF for each hospital
            plt.plot(x_values, pdf_values, label=f'{hospital} (μ={mu:.2f}, σ={std:.2f})')

            # Add hospital's name, average, and standard deviation to the table data
            table_data.append([hospital, f'{mu:.2f}', f'{std:.2f}'])   
    plt.title(title)
    plt.xlabel(rate_type.replace("_", " ").title())
    plt.ylabel('Probability Density')
    plt.xticks(np.linspace(0, 1, 21))
    plt.legend()
    pdf.savefig()
    plt.close()
    # Add the table as a separate page if there is data
    if table_data:
        table_title = f'{title} - Statistics Table for the Year'
        generate_statistics_table(table_data, pdf, table_title)

  #patient distribution
def plot_yearly_patient_distribution(patients_df: pd.DataFrame, title, pdf: PdfPages):
    # Ensure 'Date' column is in datetime format to extract the year
    patients_df['Date'] = pd.to_datetime(patients_df['Date'])
    patients_df['Year'] = patients_df['Date'].dt.year

    # Calculate total accepted patients per hospital, averaged over all years
    total_accepted = patients_df.groupby(['Year', 'Assigned Hospital']).size().reset_index(name='Total Accepted Patients')
    avg_total_accepted = total_accepted.groupby('Assigned Hospital')['Total Accepted Patients'].mean().reset_index()

    # Calculate accepted patients from vicinity (nearest hospital), averaged over all years
    accepted_from_vicinity = patients_df[patients_df['is it assigned to the nearest hospital'] == True]
    accepted_from_vicinity = accepted_from_vicinity.groupby(['Year', 'Nearest Hospital']).size().reset_index(name='Accepted from Vicinity')
    avg_accepted_from_vicinity = accepted_from_vicinity.groupby('Nearest Hospital')['Accepted from Vicinity'].mean().reset_index()

    # Calculate patients accepted in a hospital where they were not the nearest, averaged over all years
    accepted_elsewhere_closest = patients_df[patients_df['is it assigned to the nearest hospital'] == False]
    accepted_elsewhere_closest = accepted_elsewhere_closest.groupby(['Year', 'Assigned Hospital']).size().reset_index(name='Accepted From Elsewhere')
    avg_accepted_elsewhere_closest = accepted_elsewhere_closest.groupby('Assigned Hospital')['Accepted From Elsewhere'].mean().reset_index()

    # Calculate patients closest to a hospital but admitted elsewhere, averaged over all years
    closest_admitted_elsewhere = patients_df[patients_df['is it assigned to the nearest hospital'] == False]
    closest_admitted_elsewhere = closest_admitted_elsewhere.groupby(['Year', 'Nearest Hospital']).size().reset_index(name='Closest but Admitted Elsewhere')
    avg_closest_admitted_elsewhere = closest_admitted_elsewhere.groupby('Nearest Hospital')['Closest but Admitted Elsewhere'].mean().reset_index()

    # Merge all average dataframes on respective keys
    avg_distribution = avg_total_accepted.merge(avg_accepted_from_vicinity, left_on='Assigned Hospital', right_on='Nearest Hospital', how='left')
    avg_distribution = avg_distribution.merge(avg_accepted_elsewhere_closest, on='Assigned Hospital', how='left')
    avg_distribution = avg_distribution.merge(avg_closest_admitted_elsewhere, left_on='Assigned Hospital', right_on='Nearest Hospital', how='left')

    # Drop the extra 'Nearest Hospital' columns from the merge
    avg_distribution = avg_distribution.drop(columns=['Nearest Hospital_x', 'Nearest Hospital_y'])

    # Fill NaN values with 0
    avg_distribution = avg_distribution.fillna(0)

    # Plot the graph
    fig, ax = plt.subplots(figsize=(12, 6))

    # Set the width of the bars
    bar_width = 0.2
    index = range(len(avg_distribution))

    # Plot each type of patient distribution
    ax.bar(index, avg_distribution['Total Accepted Patients'], bar_width, label='Total Accepted Patients')
    ax.bar([i + bar_width for i in index], avg_distribution['Accepted from Vicinity'], bar_width, label='Accepted from Vicinity')
    ax.bar([i + 2 * bar_width for i in index], avg_distribution['Accepted From Elsewhere'], bar_width, label='Accepted From Elsewhere')
    ax.bar([i + 3 * bar_width for i in index], avg_distribution['Closest but Admitted Elsewhere'], bar_width, label='Closest but Admitted Elsewhere')

    # Add total number at the top of each bar
    for idx, row in avg_distribution.iterrows():
        ax.text(idx, row['Total Accepted Patients'], int(row['Total Accepted Patients']), ha='center', va='bottom')
        ax.text(idx + bar_width, row['Accepted from Vicinity'], int(row['Accepted from Vicinity']), ha='center', va='bottom')
        ax.text(idx + 2 * bar_width, row['Accepted From Elsewhere'], int(row['Accepted From Elsewhere']), ha='center', va='bottom')
        ax.text(idx + 3 * bar_width, row['Closest but Admitted Elsewhere'], int(row['Closest but Admitted Elsewhere']), ha='center', va='bottom')

    # Add labels and title
    ax.set_xlabel('Hospital')
    ax.set_ylabel('Number of Patients')
    ax.set_title(title)
    ax.set_xticks([i + 1.5 * bar_width for i in index])
    ax.set_xticklabels(avg_distribution['Assigned Hospital'], rotation=45)
    ax.legend()

    # Display the plot
    plt.tight_layout()
    pdf.savefig()
    plt.close()

def plot_yearly_patient_distribution_NICU(patients_df: pd.DataFrame, title, pdf: PdfPages):
    # Ensure 'Date' column is in datetime format to extract the year
    patients_df['Date'] = pd.to_datetime(patients_df['Date'])
    patients_df['Year'] = patients_df['Date'].dt.year
    patients_df = patients_df[patients_df['NICU'] == True]
    # Calculate total accepted patients per hospital, averaged over all years
    total_accepted = patients_df.groupby(['Year', 'Assigned Hospital']).size().reset_index(name='Total Accepted Patients')
    avg_total_accepted = total_accepted.groupby('Assigned Hospital')['Total Accepted Patients'].mean().reset_index()
    # Calculate accepted patients from vicinity (nearest hospital), averaged over all years
    accepted_from_vicinity = patients_df[patients_df['is it assigned to the nearest hospital'] == True]
    accepted_from_vicinity = accepted_from_vicinity.groupby(['Year', 'Nearest Hospital']).size().reset_index(name='Accepted from Vicinity')
    avg_accepted_from_vicinity = accepted_from_vicinity.groupby('Nearest Hospital')['Accepted from Vicinity'].mean().reset_index()

    # Calculate patients accepted in a hospital where they were not the nearest, averaged over all years
    accepted_elsewhere_closest = patients_df[patients_df['is it assigned to the nearest hospital'] == False]
    accepted_elsewhere_closest = accepted_elsewhere_closest.groupby(['Year', 'Assigned Hospital']).size().reset_index(name='Accepted From Elsewhere')
    avg_accepted_elsewhere_closest = accepted_elsewhere_closest.groupby('Assigned Hospital')['Accepted From Elsewhere'].mean().reset_index()

    # Calculate patients closest to a hospital but admitted elsewhere, averaged over all years
    closest_admitted_elsewhere = patients_df[patients_df['is it assigned to the nearest hospital'] == False]
    closest_admitted_elsewhere = closest_admitted_elsewhere.groupby(['Year', 'Nearest Hospital']).size().reset_index(name='Closest but Admitted Elsewhere')
    avg_closest_admitted_elsewhere = closest_admitted_elsewhere.groupby('Nearest Hospital')['Closest but Admitted Elsewhere'].mean().reset_index()

    # Merge all average dataframes on respective keys
    avg_distribution = avg_total_accepted.merge(avg_accepted_from_vicinity, left_on='Assigned Hospital', right_on='Nearest Hospital', how='left')
    avg_distribution = avg_distribution.merge(avg_accepted_elsewhere_closest, on='Assigned Hospital', how='left')
    avg_distribution = avg_distribution.merge(avg_closest_admitted_elsewhere, left_on='Assigned Hospital', right_on='Nearest Hospital', how='left')

    # Drop the extra 'Nearest Hospital' columns from the merge
    avg_distribution = avg_distribution.drop(columns=['Nearest Hospital_x', 'Nearest Hospital_y'])

    # Fill NaN values with 0
    avg_distribution = avg_distribution.fillna(0)

    # Plot the graph
    fig, ax = plt.subplots(figsize=(12, 6))

    # Set the width of the bars
    bar_width = 0.2
    index = range(len(avg_distribution))

    # Plot each type of patient distribution
    ax.bar(index, avg_distribution['Total Accepted Patients'], bar_width, label='Total Accepted Patients')
    ax.bar([i + bar_width for i in index], avg_distribution['Accepted from Vicinity'], bar_width, label='Accepted from Vicinity')
    ax.bar([i + 2 * bar_width for i in index], avg_distribution['Accepted From Elsewhere'], bar_width, label='Accepted From Elsewhere')
    ax.bar([i + 3 * bar_width for i in index], avg_distribution['Closest but Admitted Elsewhere'], bar_width, label='Closest but Admitted Elsewhere')

    # Add total number at the top of each bar
    for idx, row in avg_distribution.iterrows():
        ax.text(idx, row['Total Accepted Patients'], int(row['Total Accepted Patients']), ha='center', va='bottom')
        ax.text(idx + bar_width, row['Accepted from Vicinity'], int(row['Accepted from Vicinity']), ha='center', va='bottom')
        ax.text(idx + 2 * bar_width, row['Accepted From Elsewhere'], int(row['Accepted From Elsewhere']), ha='center', va='bottom')
        ax.text(idx + 3 * bar_width, row['Closest but Admitted Elsewhere'], int(row['Closest but Admitted Elsewhere']), ha='center', va='bottom')

    # Add labels and title
    ax.set_xlabel('Hospital')
    ax.set_ylabel('Number of Patients')
    ax.set_title(title)
    ax.set_xticks([i + 1.5 * bar_width for i in index])
    ax.set_xticklabels(avg_distribution['Assigned Hospital'], rotation=45)
    ax.legend()

    # Display the plot
    plt.tight_layout()
    pdf.savefig()
    plt.close()

# The probability chart which shows if a patient is in a vicinity of a hospital, what are chances of acceptance by the hospital.
def plot_acceptance_probability(patients_df: pd.DataFrame, title, pdf: PdfPages):
    # Ensure 'Date' column is in datetime format to extract the year
    patients_df['Date'] = pd.to_datetime(patients_df['Date'])
    patients_df['Year'] = patients_df['Date'].dt.year

    # Calculate total patients in the vicinity for each hospital, averaged over all years
    patients_in_vicinity = patients_df.groupby(['Year', 'Assigned Hospital']).size().reset_index(name='Total Patients in Vicinity')
    avg_patients_in_vicinity = patients_in_vicinity.groupby('Assigned Hospital')['Total Patients in Vicinity'].mean().reset_index()

    # Calculate accepted patients from vicinity (nearest hospital), averaged over all years
    accepted_from_vicinity = patients_df[patients_df['is it assigned to the nearest hospital'] == True]
    accepted_from_vicinity = accepted_from_vicinity.groupby(['Year', 'Assigned Hospital']).size().reset_index(name='Accepted from Vicinity')
    avg_accepted_from_vicinity = accepted_from_vicinity.groupby('Assigned Hospital')['Accepted from Vicinity'].mean().reset_index()

    # Merge to get total patients in vicinity and accepted patients from vicinity
    vicinity_distribution = avg_patients_in_vicinity.merge(avg_accepted_from_vicinity, on='Assigned Hospital', how='left')
    
    # Fill NaN values with 0
    vicinity_distribution = vicinity_distribution.fillna(0)
    
    # Calculate probability of acceptance for each hospital
    vicinity_distribution['Acceptance Probability'] = vicinity_distribution['Accepted from Vicinity'] / vicinity_distribution['Total Patients in Vicinity']

    # Plot the probability chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(vicinity_distribution['Assigned Hospital'], vicinity_distribution['Acceptance Probability'], color='skyblue', label='Acceptance Probability')

    # Add probability at the top of each bar
    for idx, row in vicinity_distribution.iterrows():
        ax.text(idx, row['Acceptance Probability'], f"{row['Acceptance Probability']:.2f}", ha='center', va='bottom')

    # Add labels and title
    ax.set_xlabel('Hospital')
    ax.set_ylabel('Probability of Acceptance')
    ax.set_title(title)
    ax.set_ylim(0, 1)  # Limit y-axis to [0, 1] for probability
    ax.legend()

    plt.tight_layout()
    pdf.savefig()
    plt.close()
# The probability chart which shows if a NICU patient is in a vicinity of a hospital, what are chances of acceptance by the hospital.
def plot_acceptance_probability_NICU(patients_df: pd.DataFrame, title, pdf: PdfPages):
    # Ensure 'Date' column is in datetime format to extract the year
    patients_df['Date'] = pd.to_datetime(patients_df['Date'])
    patients_df['Year'] = patients_df['Date'].dt.year
    patients_df = patients_df[patients_df['NICU'] == True]
    # Calculate total patients in the vicinity for each hospital, averaged over all years
    patients_in_vicinity = patients_df.groupby(['Year', 'Assigned Hospital']).size().reset_index(name='Total Patients in Vicinity')
    avg_patients_in_vicinity = patients_in_vicinity.groupby('Assigned Hospital')['Total Patients in Vicinity'].mean().reset_index()

    # Calculate accepted patients from vicinity (nearest hospital), averaged over all years
    accepted_from_vicinity = patients_df[patients_df['is it assigned to the nearest hospital'] == True]
    accepted_from_vicinity = accepted_from_vicinity.groupby(['Year', 'Assigned Hospital']).size().reset_index(name='Accepted from Vicinity')
    avg_accepted_from_vicinity = accepted_from_vicinity.groupby('Assigned Hospital')['Accepted from Vicinity'].mean().reset_index()

    # Merge to get total patients in vicinity and accepted patients from vicinity
    vicinity_distribution = avg_patients_in_vicinity.merge(avg_accepted_from_vicinity, on='Assigned Hospital', how='left')
    
    # Fill NaN values with 0
    vicinity_distribution = vicinity_distribution.fillna(0)
    
    # Calculate probability of acceptance for each hospital
    vicinity_distribution['Acceptance Probability'] = vicinity_distribution['Accepted from Vicinity'] / vicinity_distribution['Total Patients in Vicinity']

    # Plot the probability chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(vicinity_distribution['Assigned Hospital'], vicinity_distribution['Acceptance Probability'], color='skyblue', label='Acceptance Probability')

    # Add probability at the top of each bar
    for idx, row in vicinity_distribution.iterrows():
        ax.text(idx, row['Acceptance Probability'], f"{row['Acceptance Probability']:.2f}", ha='center', va='bottom')

    # Add labels and title
    ax.set_xlabel('Hospital')
    ax.set_ylabel('Probability of Acceptance')
    ax.set_title(title)
    ax.set_ylim(0, 1)  # Limit y-axis to [0, 1] for probability
    ax.legend()

    plt.tight_layout()
    pdf.savefig()
    plt.close()

# Another chart per hospital that shows the percentage of accepted patients by distance.
def accepted_patients_by_distance(results_df: pd.DataFrame, pdf: PdfPages):
    # Convert the Date column to datetime format
    results_df['Date'] = pd.to_datetime(results_df['Date'])
    # manually restrict it for now 
    results_df = results_df[results_df['Assigned Distance'] < 1000]
    # Group distances into bins of 10 km increments
    results_df = results_df.copy()
    results_df['Distance Bin'] = (results_df['Assigned Distance'] // 10) * 10
    # Get the list of unique hospitals for creating individual charts
    hospitals = results_df['Nearest Hospital'].unique()

    for hospital in hospitals:
        # Filter the data for the specific hospital
        hospital_data = results_df[results_df['Assigned Hospital'] == hospital]
        
        # Total number of accepted patients at this hospital
        total_patients = len(hospital_data)
        
        # Calculate the percentage of patients in each distance bin
        distance_counts = hospital_data.groupby('Distance Bin').size()
        distance_percentages = (distance_counts / total_patients) * 100
        
        # Prepare color list for each bin
        colors = []
        for bin in distance_percentages.index:
            # Check if patients in this bin were assigned to the nearest hospital
            is_nearest = hospital_data[hospital_data['Distance Bin'] == bin]['is it assigned to the nearest hospital'].any()
            if is_nearest:
                colors.append('green')  # Green if closest
            else:
                colors.append('red')    # Red if not closest

        # Plot the bar chart for this hospital
        plt.figure(figsize=(12, 6))
        plt.bar(distance_percentages.index, distance_percentages, color=colors, width=8)
        plt.title(f"Percentage of Accepted Patients by Distance for {hospital}")
        plt.xlabel("Distance from Hospital (km)")
        plt.ylabel("Percentage of Patients")

        # Create legend patches 
        closest_patch = mpatches.Patch(color='green', label='Accepted from Vicinity of the hospital')
        not_closest_patch = mpatches.Patch(color='red', label='Accepted from Vicinity of other hospitals')
        
        # Add legend to the plot
        plt.legend(handles=[closest_patch, not_closest_patch])
               
        # Rotate x-axis labels for readability
        plt.xticks(rotation=45)
        
        # Set x-ticks to show fewer labels if there are many bins
        #if len(distance_percentages.index) > 10:
        plt.xticks(distance_percentages.index[::2])  # Show every other bin
        
        # Save the plot to the PDF
        pdf.savefig()
        plt.close()

# Separate the NICU patients 

# Another chart per hospital that shows the percentage of accepted NICU patients by distance.
def accepted_patients_by_distance_NICU(results_df: pd.DataFrame, pdf: PdfPages):
    # Convert the Date column to datetime format
    results_df['Date'] = pd.to_datetime(results_df['Date'])
    results_df = results_df[results_df['Assigned Distance'] <= 1000]

    # Filter for NICU patients 
    results_df = results_df[results_df['NICU'] == True]

    # Group distances into bins of 10 km increments
    results_df = results_df.copy()
    results_df['Distance Bin'] = (results_df['Assigned Distance'] // 10) * 10

    # Get the list of unique hospitals for creating individual charts
    hospitals = results_df['Nearest Hospital'].unique()

    for hospital in hospitals:
        # Filter the data for the specific hospital
        hospital_data = results_df[results_df['Assigned Hospital'] == hospital]
        
        # Total number of accepted patients at this hospital
        total_patients = len(hospital_data)
        
        # Calculate the percentage of patients in each distance bin
        distance_counts = hospital_data.groupby('Distance Bin').size()
        distance_percentages = (distance_counts / total_patients) * 100
        
        # Prepare color list for each bin
        colors = []
        for bin in distance_percentages.index:
            # Check if patients in this bin were assigned to the nearest hospital
            is_nearest = hospital_data[hospital_data['Distance Bin'] == bin]['is it assigned to the nearest hospital'].any()
            if is_nearest:
                colors.append('green')  # Green if closest
            else:
                colors.append('red')    # Red if not closest

        # Plot the bar chart for this hospital
        plt.figure(figsize=(12, 6))
        plt.bar(distance_percentages.index, distance_percentages, color=colors, width=8)
        plt.title(f"Percentage of Accepted NICU Patients by Distance for {hospital}")
        plt.xlabel("Distance from Hospital (km)")
        plt.ylabel("Percentage of Patients")

        # Create legend patches 
        closest_patch = mpatches.Patch(color='green', label='Accepted from Vicinity of the hospital')
        not_closest_patch = mpatches.Patch(color='red', label='Accepted from Vicinity of other hospitals')
        
        # Add legend to the plot
        plt.legend(handles=[closest_patch, not_closest_patch])

        # Rotate x-axis labels for readability
        plt.xticks(rotation=45)
        # Set x-ticks to show fewer labels if there are many bins
        #plt.xticks(distance_percentages.index[::2])  # Show every other bin     
        plt.xticks(distance_percentages.index)  # Show every bin with 45-degree rotation for readability  
        # Save the plot to the PDF
        pdf.savefig()
        plt.close()

def probability_distribution_patients(results_df: pd.DataFrame, pdf: PdfPages):
    # Plot 1: Probability distribution for patients closest to each hospital (regardless of admission)
    results_df['Date'] = pd.to_datetime(results_df['Date'])
    
    # Extract year from Date column
    results_df['Year'] = results_df['Date'].dt.year

    # Calculate total patient count per hospital for each year
    yearly_counts = results_df.groupby(['Year', 'Nearest Hospital']).size().reset_index(name='Yearly Patient Count')
    # Define x-values for the patient count range based on observed data
    x_values = np.linspace(0, yearly_counts['Yearly Patient Count'].max() + 10 , 100)
    
    plt.figure(figsize=(12, 6))
    
    # Get unique hospitals for plotting
    hospitals = yearly_counts['Nearest Hospital'].unique()

    # Store data for the table
    table_data = []

    for hospital in hospitals:
        # Filter yearly count data for the current hospital
        hospital_data = yearly_counts[yearly_counts['Nearest Hospital'] == hospital]['Yearly Patient Count']
        
        # Check if there's sufficient data to fit a distribution (at least 2 data points)
        if len(hospital_data) > 1:
            # Fit a normal distribution to the yearly patient counts
            mu, std = norm.fit(hospital_data)
            
            # Calculate PDF values
            pdf_values = norm.pdf(x_values, mu, std)
            
            # Normalize PDF values so that the area under the curve sums to 1
            pdf_values /= np.sum(pdf_values)
            
            # Plot the normalized PDF
            plt.plot(x_values, pdf_values, label=f'{hospital} (μ={mu:.2f}, σ={std:.2f})')
                # Add hospital's name, average, and standard deviation to the table data
            table_data.append([hospital, f'{mu:.2f}', f'{std:.2f}'])
    plt.title("Probability Distribution of Closest Distances for Each Hospital (Regardless of Admission)")
    plt.xlabel("Number of Patients per Year")
    plt.ylabel("Probability Density")
    plt.legend()
    pdf.savefig()
    plt.close()
    # Add the table as a separate page if there is data
    if table_data:
        table_title = f'Probability Distribution of Closest Distances for Each Hospital (Regardless of Admission)'
        generate_statistics_table(table_data, pdf, table_title)

    # Plot 2: Probability distribution for the number of patients closest to each hospital but admitted elsewhere
    results_df['Date'] = pd.to_datetime(results_df['Date'])
    
    # Extract year from Date column
    results_df['Year'] = results_df['Date'].dt.year
    
    # Filter for patients not assigned to the nearest hospital
    filtered_data = results_df[results_df['is it assigned to the nearest hospital'] == False]
    
    # Calculate total patient count per hospital for each year
    yearly_counts = filtered_data.groupby(['Year', 'Nearest Hospital']).size().reset_index(name='Yearly Patient Count')
    # Define x-values for the patient count range based on observed data
    x_values = np.linspace(0, yearly_counts['Yearly Patient Count'].max() + 10, 100)
    
    plt.figure(figsize=(12, 6))
    
    # Get unique hospitals for plotting
    hospitals = yearly_counts['Nearest Hospital'].unique()

    # Store data for the table
    table_data = []

    for hospital in hospitals:
        # Filter yearly count data for the current hospital
        hospital_data = yearly_counts[yearly_counts['Nearest Hospital'] == hospital]['Yearly Patient Count']
        
        # Check if there's sufficient data to fit a distribution (at least 2 data points)
        if len(hospital_data) > 1:
            # Fit a normal distribution to the yearly patient counts
            mu, std = norm.fit(hospital_data)
            
            # Calculate PDF values
            pdf_values = norm.pdf(x_values, mu, std)
            
            # Normalize PDF values so that the area under the curve sums to 1
            pdf_values /= np.sum(pdf_values)
            
            # Plot the normalized PDF
            plt.plot(x_values, pdf_values, label=f'{hospital} (μ={mu:.2f}, σ={std:.2f})')

            # Add hospital's name, average, and standard deviation to the table data
            table_data.append([hospital, f'{mu:.2f}', f'{std:.2f}'])  
    plt.title("Probability Distribution of Patients Closest to Each Hospital but Admitted Elsewhere")
    plt.xlabel("Number of Patients per Year")
    plt.ylabel("Probability Density")
    plt.legend()
    pdf.savefig()
    plt.close()

    # Add the table as a separate page if there is data
    if table_data:
        table_title = f'Probability Distribution of Closest Distances for Each Hospital (Regardless of Admission)'
        generate_statistics_table(table_data, pdf, table_title)