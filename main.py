from config import *
from utils.simulation import simulate_hospital_system
from utils.helpers import print_hospital_data
from utils.visualization import create_pdf_report
import pandas as pd


def main():
    
    results = simulate_hospital_system(num_days=NUMBER_OF_DAYS, excel=EXCEL_PATH,excel_newdata=EXCEL_PATH_NEWDATA)
    print_hospital_data(results)

    # Load simulation results
    results_df = pd.read_excel("output/simulation.xlsx")

    patients_df = pd.read_excel("output/patients.xlsx")
    # Create PDF report with all plots
    create_pdf_report(results_df=results_df, patients_df=patients_df)
    print(f"Report generated: {REPORT}")

if __name__ == "__main__":
    main()