from utils.simulation import simulate_hospital_system, simulate_hospital_system_without_animation
from utils.helpers import print_hospital_data
import pandas as pd
from utils.DataVisualizer import *
from utils.ReportGenerator import *
import yaml
from itertools import product
from datetime import datetime
import numpy as np
from tqdm import tqdm

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
    # print_hospital_data(results)

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
    occupancy_rates = [0.90, 0.925, 0.95] # Occupancy thresholds to test
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

    # Add tqdm progress bar
    for i, rates in enumerate(tqdm(all_combinations[:100], total=100, desc="Running grid search"), 1):
        config = {
            hospital: {"Intensive": rate, "Intermediate": rate}
            for hospital, rate in zip(hospitals, rates)
        }
        
        try:
            # Run simulation
            # This simulation follows all recommendation criteria.
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
                # print(f"Completed {i}/{total_configs} configurations ({(i/total_configs)*100:.1f}%)")
                
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
    Find optimal configurations based on different optimization strategies.
    Returns top configurations for each strategy.
    """
    df = pd.DataFrame(all_results)
    
    # more strategies using grid search

    '''
        Total weight = 1
        intensive_weight = [0.3 - 0.5]
        intermediate_weight = [0.3 - 0.5]
        distance_weight = [0.3 - 0.5]

        all should sum to 1
        so if
    '''
    optimization_strategies = {
        'min_travel_distance': {
            'distance_weight': 0.9,
            'occupancy_weight': 0.1
        },
        'balanced_occupancy': {
            'intensive_weight': 0.45,
            'intermediate_weight': 0.45,
            'distance_weight': 0.1
        },
        'balanced_overall': {
            'distance_weight': 0.4,
            'intensive_weight': 0.3,
            'intermediate_weight': 0.3
        },


    }
    
    results = {}
    
    for strategy, weights in optimization_strategies.items():
        scores = []
        for _, row in df.iterrows():
            metrics = row['metrics']
            
            # Calculate distance score (normalized)
            avg_distance = metrics['global']['avg_travel_distance']
            max_distance = metrics['global']['max_travel_distance']

            # Normalize the distance score, by dividing the average distance by the maximum distance
            # such that the score is between 0 and 1
            distance_score = 1 - (avg_distance / max_distance)
            
            # Calculate occupancy balance scores
            occupancy_variations = {hospital: {
                'intensive': metrics[hospital]['std_intensive_occupancy'],
                'intermediate': metrics[hospital]['std_intermediate_occupancy'],
                'avg_intensive': metrics[hospital]['avg_intensive_occupancy'],
                'avg_intermediate': metrics[hospital]['avg_intermediate_occupancy']
            } for hospital in metrics if hospital != 'global'}
            
            # Calculate average standard deviations for both types
            intensive_std = np.mean([v['intensive'] for v in occupancy_variations.values()])
            intermediate_std = np.mean([v['intermediate'] for v in occupancy_variations.values()])
            
            # Calculate final score based on strategy
            if strategy == 'min_travel_distance':
                score = (weights['distance_weight'] * distance_score +
                        weights['occupancy_weight'] * (1 - (intensive_std + intermediate_std) / 2))
            
            elif strategy == 'balanced_occupancy':
                occupancy_score = (1 - intensive_std) * weights['intensive_weight'] + \
                                (1 - intermediate_std) * weights['intermediate_weight']
                score = occupancy_score + (distance_score * weights['distance_weight'])
            
            else:  # balanced_overall
                score = (distance_score * weights['distance_weight'] + 
                        (1 - intensive_std) * weights['intensive_weight'] +
                        (1 - intermediate_std) * weights['intermediate_weight'])
            
            scores.append(round(score, 4))
        
        df[f'score_{strategy}'] = scores
        results[strategy] = df.nlargest(5, f'score_{strategy}')
    
    # Save results for each strategy
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for strategy, top_configs in results.items():
        filename = f"output/optimal_configurations_{strategy}_{timestamp}.xlsx"
        top_configs.to_excel(filename, index=False)
        
        # print(f"\nTop 5 Configurations for {strategy}:")
        # for _, row in top_configs.iterrows():
        #     print(f"\nScore: {row[f'score_{strategy}']}")
        #     print(f"Configuration: {row['config']}")
        #     print("Metrics:", row['metrics'])
    
    return results

def save_analysis_results(results, filename):
    """Save analysis results to Excel file."""
    df = pd.DataFrame(results)
    df.to_excel(filename, index=False)

def save_optimal_configurations(configs, filename_prefix):
    """Save optimal configurations to Excel file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for strategy, df in configs.items():
        filename = f"{filename_prefix}_{strategy}_{timestamp}.xlsx"
        df.to_excel(filename, index=False)

if __name__ == "__main__":
    # main()
    run_grid_search()