import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
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
    """"
    # Weekly Section
    plt.text(0.1, 0.75, '1. Weekly Occupancy Rates', fontsize=12)
    plt.text(0.15, 0.70, '- CHU-SJ Weekly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.67, '- CHUQ Weekly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.64, '- CHUS Weekly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.61, '- CUSM Weekly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.58, '- HGJ Weekly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.55, '- HMR Weekly Occupancy (Intensive & Intermediate)', fontsize=10)
    
    # Monthly Section
    plt.text(0.1, 0.45, '2. Monthly Occupancy Rates', fontsize=12)
    plt.text(0.15, 0.40, '- CHU-SJ Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.37, '- CHUQ Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.34, '- CHUS Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.31, '- CUSM Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.28, '- HGJ Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.25, '- HMR Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    
    # Yearly Section
    plt.text(0.1, 0.15, '3. Yearly Occupancy Rates', fontsize=12)
    plt.text(0.15, 0.10, '- Yearly Average Intensive Occupancy Rates', fontsize=10)
    plt.text(0.15, 0.07, '- Yearly Average Intermediate Occupancy Rates', fontsize=10)
    """
    # Monthly Section
    plt.text(0.1, 0.75, '1. Monthly Occupancy Rates', fontsize=12)
    plt.text(0.15, 0.70, '- CHU-SJ Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.67, '- CHUQ Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.64, '- CHUS Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.61, '- CUSM Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.58, '- HGJ Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    plt.text(0.15, 0.55, '- HMR Monthly Occupancy (Intensive & Intermediate)', fontsize=10)
    
    # Yearly Section
    plt.text(0.1, 0.45, '2. Yearly Occupancy Rates', fontsize=12)
    plt.text(0.15, 0.40, '- Yearly Average Intensive Occupancy Rates', fontsize=10)
    plt.text(0.15, 0.37, '- Yearly Average Intermediate Occupancy Rates', fontsize=10)
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

def create_pdf_report(results_df: pd.DataFrame):
    """
    Creates a single PDF with table of contents and all plots
    """
    with PdfPages(REPORT) as pdf:


        # Add table of contents
        create_table_of_contents(pdf)
        # Generate report header
        generate_report_header(pdf, ASSUMPTIONS, HYPERPARAMETERS)
        # Weekly occupancy plots
        #add_section_header("1. Weekly Occupancy Rates", pdf)
        #plot_weekly_occupancy(results_df, pdf)
        
        # Monthly occupancy plots
        add_section_header("1. Monthly Occupancy Rates", pdf)
        plot_monthly_occupancy_probability(results_df, 'Intensive Occupancy Rate', 'Monthly Probability Distribution Intensive',pdf)
        plot_monthly_occupancy_probability(results_df, 'Intermediate Occupancy Rate', 'Monthly Probability Distribution Intermediate',pdf)

        
        # Yearly occupancy plots
        add_section_header("2. Yearly Occupancy Rates", pdf)
        plot_yearly_occupancy_probability(results_df, 'Intensive Occupancy Rate', 'Yearly Probability Distribution Intensive', pdf)
        plot_yearly_occupancy_probability(results_df, 'Intermediate Occupancy Rate', 'Yearly Probability Distribution Intermediate', pdf)

def plot_weekly_occupancy(results_df: pd.DataFrame, pdf: PdfPages):
    """
    Plots weekly occupancy rates and saves to PDF
    """
    # Data preparation
    results_df['Date'] = pd.to_datetime(results_df['Date'])
    results_df['Week'] = results_df['Date'].dt.isocalendar().week
    weekly_occupancy = results_df.groupby(['Hospital', 'Week']).agg({
        'Intensive Occupancy Rate': 'mean',
        'Intermediate Occupancy Rate': 'mean'
    }).reset_index()

    # Create plots for each hospital
    for hospital in weekly_occupancy['Hospital'].unique():
        hospital_data = weekly_occupancy[weekly_occupancy['Hospital'] == hospital]

        # Intensive unit plot
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Week', y='Intensive Occupancy Rate', data=hospital_data)
        plt.title(f'{hospital} Weekly Intensive Occupancy Rates')
        plt.xlabel('Week')
        plt.ylabel('Average Intensive Occupancy Rate')
        plt.xticks(ticks=range(0, max(hospital_data['Week']) + 1, 10))
        pdf.savefig()
        plt.close()

        # Intermediate unit plot
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Week', y='Intermediate Occupancy Rate', data=hospital_data)
        plt.title(f'{hospital} Weekly Intermediate Occupancy Rates')
        plt.xlabel('Week')
        plt.ylabel('Average Intermediate Occupancy Rate')
        plt.xticks(ticks=range(0, max(hospital_data['Week']) + 1, 10))
        pdf.savefig()
        plt.close()

def plot_monthly_occupancy(results_df: pd.DataFrame, pdf: PdfPages):
    """
    Plots monthly occupancy rates and saves to PDF
    """
    monthly_occupancy = results_df.groupby(['Hospital', 'Month']).agg({
        'Intensive Occupancy Rate': 'mean',
        'Intermediate Occupancy Rate': 'mean'
    }).reset_index()

    for hospital in monthly_occupancy['Hospital'].unique():
        hospital_data = monthly_occupancy[monthly_occupancy['Hospital'] == hospital]

        # Intensive unit plot
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Month', y='Intensive Occupancy Rate', data=hospital_data)
        plt.title(f'{hospital} Monthly Intensive Occupancy Rates')
        plt.xlabel('Month')
        plt.ylabel('Average Intensive Occupancy Rate')
        pdf.savefig()
        plt.close()

        # Intermediate unit plot
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Month', y='Intermediate Occupancy Rate', data=hospital_data)
        plt.title(f'{hospital} Monthly Intermediate Occupancy Rates')
        plt.xlabel('Month')
        plt.ylabel('Average Intermediate Occupancy Rate')
        pdf.savefig()
        plt.close()

def plot_monthly_occupancy_probability(results_df: pd.DataFrame, rate_type, title, pdf: PdfPages):
    x_values = np.linspace(0, 1, 100)  # Occupancy rates are between 0 and 1
    months = results_df['Month'].unique()

    for month in months:
        plt.figure(figsize=(12, 6))
        month_data = results_df[results_df['Month'] == month]
        hospitals = results_df['Hospital'].unique()

        for hospital in hospitals:
            hospital_data = month_data[month_data['Hospital'] == hospital][rate_type].dropna()
            if len(hospital_data) > 0:
                # Check if there's enough variation in the data
                if np.std(hospital_data) > 1e-10:  # Small threshold for numerical stability
                    mu, std = norm.fit(hospital_data)
                    pdf_values = norm.pdf(x_values, mu, std)
                    
                    pdf_sum = np.sum(pdf_values)
                    if pdf_sum > 0:
                        pdf_values = pdf_values / pdf_sum
                    
                    plt.plot(x_values, pdf_values, label=f'{hospital} (μ={mu:.2f}, σ={std:.2f})')
                else:
                    # For constant data, just plot a vertical line at the mean
                    mu = np.mean(hospital_data)
                    plt.axvline(x=mu, label=f'{hospital} (constant at {mu:.2f})')

        plt.title(f'{title} for Month {month}')
        plt.xlabel(rate_type.replace("_", " ").title())
        plt.ylabel('Probability')
        plt.xticks(np.linspace(0, 1, 11))  # X-axis ticks from 0 to 1 in 0.1 intervals
        plt.legend()

        pdf.savefig()
        plt.close()

def plot_yearly_occupancy(results_df: pd.DataFrame, pdf: PdfPages):
    """
    Plots yearly occupancy rates and saves to PDF
    """
    yearly_occupancy = results_df.groupby('Hospital').agg({
        'Intensive Occupancy Rate': 'mean',
        'Intermediate Occupancy Rate': 'mean'
    }).reset_index()

    # Intensive unit plot
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Hospital', y='Intensive Occupancy Rate', data=yearly_occupancy)
    plt.title('Yearly Average Intensive Occupancy Rates per Hospital')
    plt.xlabel('Hospital')
    plt.ylabel('Average Intensive Occupancy Rate')
    pdf.savefig()
    plt.close()

    # Intermediate unit plot
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Hospital', y='Intermediate Occupancy Rate', data=yearly_occupancy)
    plt.title('Yearly Average Intermediate Occupancy Rates per Hospital')
    plt.xlabel('Hospital')
    plt.ylabel('Average Intermediate Occupancy Rate')
    pdf.savefig()
    plt.close()


def plot_yearly_occupancy_probability(results_df: pd.DataFrame,rate_type, title, pdf: PdfPages):
  x_values = np.linspace(0, 1, 100)  # Occupancy rates are between 0 and 1
  plt.figure(figsize=(12, 6))
  hospitals = results_df['Hospital'].unique()
  for hospital in hospitals:
      hospital_data = results_df[results_df['Hospital'] == hospital][rate_type].dropna()
      if len(hospital_data) > 0:
          # Check if there's enough variation in the data
          if np.std(hospital_data) > 1e-10:  # Small threshold for numerical stability
              mu, std = norm.fit(hospital_data)
              pdf_values = norm.pdf(x_values, mu, std)
              
              pdf_sum = np.sum(pdf_values)
              if pdf_sum > 0:
                  pdf_values = pdf_values / pdf_sum
              
              plt.plot(x_values, pdf_values, label=f'{hospital} (μ={mu:.2f}, σ={std:.2f})')
          else:
              # For constant data, just plot a vertical line at the mean
              mu = np.mean(hospital_data)
              plt.axvline(x=mu, label=f'{hospital} (constant at {mu:.2f})')
    
  plt.title(title)
  plt.xlabel(rate_type.replace("_", " ").title())
  plt.ylabel('Probability Density')
  plt.xticks(np.linspace(0, 1, 11)) 
  plt.legend()
  pdf.savefig()
  plt.close()