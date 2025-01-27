from utils.simulation import simulate_hospital_system, simulate_hospital_system_without_animation
from utils.helpers import print_hospital_data
import pandas as pd
from utils.DataVisualizer import *
from utils.ReportGenerator import *
import yaml
from itertools import product
from datetime import datetime
import numpy as np

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



# TODO: Save metrics in better format
def analyze_simulation_results(results, patients_df):
    """
    Analyze simulation results and calculate key metrics.

    Args:
        results: Simulation results
        patients_df: Patients DataFrame

    Returns:
        metrics: Dictionary of metrics
    """
    # Convert results to DataFrame if not already
    results_df = pd.DataFrame(results)
    metrics = {}
    
    # 1. Calculate occupancy metrics per hospital
    for hospital in results_df['Hospital'].unique():
        hospital_data = results_df[results_df['Hospital'] == hospital]
        
        metrics[hospital] = {
            'avg_intensive_occupancy': hospital_data['Intensive Occupancy Rate'].mean(),
            'min_intensive_occupancy': hospital_data['Intensive Occupancy Rate'].min(),
            'max_intensive_occupancy': hospital_data['Intensive Occupancy Rate'].max(),
            'std_intensive_occupancy': hospital_data['Intensive Occupancy Rate'].std(),
            
            'avg_intermediate_occupancy': hospital_data['Intermediate Occupancy Rate'].mean(),
            'min_intermediate_occupancy': hospital_data['Intermediate Occupancy Rate'].min(),
            'max_intermediate_occupancy': hospital_data['Intermediate Occupancy Rate'].max(),
            'std_intermediate_occupancy': hospital_data['Intermediate Occupancy Rate'].std(),
        }
    
    # 2. Calculate travel distance metrics
    metrics['global'] = {
        'avg_travel_distance': patients_df['Assigned Distance'].mean(),
        'max_travel_distance': patients_df['Assigned Distance'].max(),
        'std_travel_distance': patients_df['Assigned Distance'].std(),
        'total_patients': len(patients_df),
        'patients_at_nearest': (patients_df['is it assigned to the nearest hospital']).mean() * 100,
        'patients_at_best_occupancy': (patients_df['is it assigned to the best occupancy rate hospital']).mean() * 100,
    }
    
    return metrics


def run_grid_search():
    """
    Generate all possible configurations, run simulations, and analyze results.

    Returns:
        all_configurations_results: List of all configurations results
        optimal_configs: List of optimal configurations
    """

    # Our hospitals
    hospitals = ["CHU-SJ", "CHUQ", "CHUS", "CUSM", "HGJ", "HMR"]
    occupancy_rates = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95] # Occupancy thresholds to test
    # Create timestamp for unique file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize results storage
    all_configurations_results = []
    
    # Generate all possible combinations
    all_combinations = list(product(occupancy_rates, repeat=len(hospitals)))
    # Take only first 10 combinations for testing
    total_configs = len(all_combinations) # 6^6 = 46656


    # 6 6 , 6 6 , 6 6 , 6 6 , 6 6 , 6 6

    # 6 ^ 12 = 2,176,782,336
    
    print(f"Starting test grid search with {total_configs} configurations...")

    for i, rates in enumerate(all_combinations[:5], 1):
        config = {
            hospital: {"Intensive": rate, "Intermediate": rate}
            for hospital, rate in zip(hospitals, rates)
        }
        
        try:
            # Run simulation
            results = simulate_hospital_system_without_animation(
                num_days=number_of_days,
                excel=excel_path,
                hospital_occupancy_configuration=config
            )
            
            # Load the generated files for analysis
            results_df = pd.read_excel("output/simulation.xlsx")
            patients_df = pd.read_excel("output/patients.xlsx")
            
            # Analyze results
            metrics = analyze_simulation_results(results, patients_df)
            
            # Store configuration and its metrics
            config_results = {
                'configuration_id': i,
                'config': str(config),
                'metrics': metrics
            }
            
            all_configurations_results.append(config_results)
            
            # Save intermediate results
            if i % 100 == 0:
                save_analysis_results(all_configurations_results, f"output/grid_search_analysis_{timestamp}.xlsx")
                print(f"Completed {i}/{total_configs} configurations ({(i/total_configs)*100:.1f}%)")
                
        except Exception as e:
            print(f"Error in configuration {i}:")
            print(f"Configuration: {config}")
            print(f"Error details: {str(e)}")
            continue
    
    # Find optimal configurations
    optimal_configs = find_optimal_configurations(all_configurations_results)
    
    # Save final results
    save_analysis_results(all_configurations_results, f"output/final_grid_search_analysis_{timestamp}.xlsx")
    save_optimal_configurations(optimal_configs, f"output/optimal_configurations_{timestamp}.xlsx")
    
    return all_configurations_results, optimal_configs

def find_optimal_configurations(all_results):
    """
    Find optimal configurations based on different criteria with improved sensitivity.
    """
    df = pd.DataFrame(all_results)
    
    # Define weights for optimization function

    # TODO: Loop through different weights

    # new weights
    '''{
         occupancy_balance: (occupancy_balance_intermediate occupancy_balance_intensive)
    }'''
    weights = {
        'occupancy_balance': 0.4, # (0.2 - 0.7) 
        'travel_distance': 0.3, # (1 - occupancy_balance)
        # (0.2 - 0.7) * (0.2 - 0.7) 
        'patient_satisfaction': 0.3 # remove this
    }
    # Calculate composite scores
    scores = []
    for _, row in df.iterrows():
        metrics = row['metrics']
        
        # Calculate occupancy balance score with more sensitivity
        occupancy_variations = []
        for hospital in metrics.keys():
            if hospital != 'global':
                # Include both average and variation in scoring
                occupancy_variations.append(metrics[hospital]['std_intensive_occupancy'])
                occupancy_variations.append(metrics[hospital]['avg_intensive_occupancy'])
                occupancy_variations.append(metrics[hospital]['std_intermediate_occupancy'])
                occupancy_variations.append(metrics[hospital]['avg_intermediate_occupancy'])
        
        # Normalize occupancy score differently
        occupancy_balance = 1 / (1 + np.mean(occupancy_variations))
        
        # Calculate travel distance score with more granularity
        avg_distance = metrics['global']['avg_travel_distance']
        max_distance = metrics['global']['max_travel_distance']
        travel_score = np.exp(-avg_distance / max_distance)
        
        # Calculate patient satisfaction score with more weight on nearest hospital
        satisfaction_score = (
            0.6 * metrics['global']['patients_at_nearest'] + 
            0.4 * metrics['global']['patients_at_best_occupancy']
        ) / 100
        
        # Calculate optimization score, to find the best configuration
        composite_score = (
            weights['occupancy_balance'] * occupancy_balance +
            weights['travel_distance'] * travel_score +
            weights['patient_satisfaction'] * satisfaction_score
        )
        
        scores.append(round(composite_score, 4))  # Round to 4 decimal places for differentiation
    
    df['composite_score'] = scores
    
    # Return top 5 configurations with more details
    top_configs = df.nlargest(5, 'composite_score')
    print("\nTop 5 Configurations Details:")
    for _, row in top_configs.iterrows():
        print(f"\nScore: {row['composite_score']}")
        print(f"Configuration: {row['config']}")
        print("Metrics:", row['metrics'])
    
    return top_configs

def save_analysis_results(results, filename):
    """Save analysis results to Excel file."""
    df = pd.DataFrame(results)
    df.to_excel(filename, index=False)

def save_optimal_configurations(configs, filename):
    """Save optimal configurations to Excel file."""
    configs.to_excel(filename, index=False)

if __name__ == "__main__":
    # main()
    run_grid_search()