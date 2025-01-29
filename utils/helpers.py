from tabulate import tabulate

# print the hospital data in a table format
def print_hospital_data(results):
    '''
    Print the hospital data in a table format
    Args:
        results (list): The results from the simulation

    '''
    # Define the headers for the table
    headers = ["Day", "Hospital", "Arrived Patients", "Discharged Patients", "Intensive Occupancy Rate", "Intermediate Occupancy Rate"]
    
    # Create a list of rows
    table_data = [
        [
            result["Day"],
            result["Hospital"],
            result["Arrived Patients"],
            result["Discharged Patients"],
            f"{result['Intensive Occupancy Rate']:.2%}",
            f"{result['Intermediate Occupancy Rate']:.2%}"
        ]
        for result in results
    ]
    
    # Print the table
    # print(tabulate(table_data, headers=headers, tablefmt="pretty"))

