from utils.simulation import simulate_hospital_system, simulate_hospital_system_without_animation
from utils.helpers import print_hospital_data
import pandas as pd
from utils.DataVisualizer import *
from utils.ReportGenerator import *
import yaml
from itertools import product
from datetime import datetime

# Load the configuration from the YAML file.
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access the configuration values.
number_of_days = config['NUMBER_OF_DAYS']
excel_path = config['EXCEL_PATH']
report_path = config['REPORT']
table_path = config['TABLE']

hospital_occupancy_configuration = {"CHU-SJ": {"Intensive": 0.95, "Intermediate": 0.95},
                                    "CHUQ": {"Intensive": 0.95, "Intermediate": 0.95},  
                                    "CHUS": {"Intensive": 0.95, "Intermediate": 0.95},
                                    "CUSM": {"Intensive": 0.95, "Intermediate": 0.95},
                                    "HGJ": {"Intensive": 0.95, "Intermediate": 0.95},
                                    "HMR": {"Intensive": 0.95, "Intermediate": 0.95}}


def main():    
    
    results = simulate_hospital_system(num_days=number_of_days, excel=excel_path, hospital_occupancy_configuration=hospital_occupancy_configuration)
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

def run_grid_search():
    """
    Generate all possible configurations, run simulations, and analyze results.
    """
    hospitals = ["CHU-SJ", "CHUQ", "CHUS", "CUSM", "HGJ", "HMR"]
    occupancy_rates = [round(rate/100, 2) for rate in range(90, 96)]  # [0.90, 0.91, 0.92, 0.93, 0.94, 0.95]
    
    # Create timestamp for unique file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"output/grid_search_results_{timestamp}.xlsx"
    
    # Initialize results storage
    all_results = []
    
    # Generate all possible combinations
    all_combinations = product(occupancy_rates, repeat=len(hospitals))
    total_configs = len(occupancy_rates)**len(hospitals)
    
    print(f"Starting grid search with {total_configs} configurations...")

    print(total_configs)


    for i, rates in enumerate(all_combinations, 1):
        # Create configuration
        config = {
            hospital: {"Intensive": rate, "Intermediate": rate}
            for hospital, rate in zip(hospitals, rates)
        }        
        try:
            # Run simulation with current configuration
            results = simulate_hospital_system_without_animation(
                num_days=number_of_days,
                excel=excel_path,
                hospital_occupancy_configuration=config
            )
            print_hospital_data(results)

            
            #Extract metrics from results
            metrics = {
                'configuration_id': i,
                'config': str(config),  # Store configuration as string
            }
            
            # Add all relevant metrics from your simulation results
            metrics.update(results)  # Assuming results contains your metrics
            
            # Store results
            all_results.append(metrics)
            
            # Print progress
            if i % 100 == 0:
                print(f"Completed {i}/{total_configs} configurations ({(i/total_configs)*100:.1f}%)")
                
                # Save intermediate results every 100 configurations
                results_df = pd.DataFrame(all_results)
                results_df.to_excel(results_file, index=False)
                
        except Exception as e:
            print(f"Error in configuration {i}: {str(e)}")
            continue
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(all_results)
    
    # Save final results
    results_df.to_excel(results_file, index=False)
    
    # Find and print best configurations based on different metrics
    print("\nAnalysis of Results:")
    print("-" * 80)
    
    # Example metrics to optimize (adjust based on your actual metrics)
    metrics_to_analyze = [
        'average_wait_time',
        'total_patients_served',
        'resource_utilization'
    ]
    
    for metric in metrics_to_analyze:
        if metric in results_df.columns:
            print(f"\nTop 5 configurations by {metric}:")
            if metric == 'average_wait_time':  # Lower is better
                best_configs = results_df.nsmallest(5, metric)
            else:  # Higher is better
                best_configs = results_df.nlargest(5, metric)
            
            print(best_configs[['configuration_id', metric, 'config']].to_string())
    
    print(f"\nComplete results saved to: {results_file}")
    return results_df

if __name__ == "__main__":
    # Run grid search instead of single simulation
    # results_df = run_grid_search()
    # main()
    run_grid_search()