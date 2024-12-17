from utils.simulation import simulate_hospital_system
from utils.helpers import print_hospital_data
import pandas as pd
from utils.DataVisualizer import *
from utils.ReportGenerator import *
import yaml

# Load the configuration from the YAML file.
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access the configuration values.
number_of_days = config['NUMBER_OF_DAYS']
excel_path = config['EXCEL_PATH']
excel_path_newdata = config['EXCEL_PATH_NEWDATA']
report_path = config['REPORT']
table_path = config['TABLE']

def main():    
    results = simulate_hospital_system(num_days=number_of_days, excel=excel_path ,excel_newdata=excel_path_newdata)
    print_hospital_data(results)

    # Load simulation results
    results_df = pd.read_excel("output/simulation.xlsx")

    patients_df = pd.read_excel("output/patients.xlsx")
    # Initialize DataVisualizer and ReportGenerator instances
    visualizer = DataVisualizer(report_path=report_path)
    report_generator = ReportGenerator(
        report_path=report_path,
        visualizer=visualizer, results_df=results_df, patients_df=patients_df,
    )

    # Generate the PDF report
    report_generator.create_pdf_report()
    print(f"Report generated: {report_path}")

    # Create tables
    intensive_patients_table, intermediate_patients_table, created_hospital_table, aggregated_intensive_patients_table, aggregated_intermediate_patients_table, metrics_table = visualizer.create_patients_table(patients_df)
    # Save tables to an Excel file with specified sheet names
    with pd.ExcelWriter(table_path) as writer:
        created_hospital_table.to_excel(writer, sheet_name="Hospitals", index=False)
        intensive_patients_table.to_excel(writer, sheet_name="Intensive Patients", index=False)
        intermediate_patients_table.to_excel(writer, sheet_name="Intermediate Patients", index=False)
        aggregated_intensive_patients_table.to_excel(writer, sheet_name="Agg Intensive Patients", index=False)
        aggregated_intermediate_patients_table.to_excel(writer, sheet_name="Agg Intermediate Patients",
                                                        index=False)
        metrics_table.to_excel(writer, sheet_name="Assignment Evaluation",
                                                        index=False)
        print(f"Table generated: {table_path}")

if __name__ == "__main__":
    main()