from config import *
from utils.simulation import simulate_hospital_system
from utils.helpers import print_hospital_data
import pandas as pd
from utils.DataVisualizer import *
from utils.ReportGenerator import *

def main():
    
    results = simulate_hospital_system(num_days=NUMBER_OF_DAYS, excel=EXCEL_PATH,excel_newdata=EXCEL_PATH_NEWDATA)
    print_hospital_data(results)

    # Load simulation results
    results_df = pd.read_excel("output/simulation.xlsx")

    patients_df = pd.read_excel("output/patients.xlsx")
    # Initialize DataVisualizer and ReportGenerator instances
    visualizer = DataVisualizer(report_path=REPORT)
    report_generator = ReportGenerator(
        report_path=REPORT,
        visualizer=visualizer, results_df=results_df, patients_df=patients_df,
    )

    # Generate the PDF report
    report_generator.create_pdf_report()
    print(f"Report generated: {REPORT}")

    # Create tables
    intensive_patients_table, intermediate_patients_table, created_hospital_table, aggregated_intensive_patients_table, aggregated_intermediate_patients_table = visualizer.create_patients_table(patients_df)

    # Save tables to an Excel file with specified sheet names
    with pd.ExcelWriter(TABLE) as writer:
        created_hospital_table.to_excel(writer, sheet_name="Hospitals", index=False)
        intensive_patients_table.to_excel(writer, sheet_name="Intensive Patients", index=False)
        intermediate_patients_table.to_excel(writer, sheet_name="Intermediate Patients", index=False)
        aggregated_intensive_patients_table.to_excel(writer, sheet_name="Aggregated Intensive Patients", index=False)
        aggregated_intermediate_patients_table.to_excel(writer, sheet_name="Aggregated Intermediate Patients",
                                                        index=False)
        print(f"Table generated: {TABLE}")

if __name__ == "__main__":
    main()