from config import *
from utils.simulation import simulate_hospital_system
from utils.helpers import print_hospital_data
def main():
    
    results = simulate_hospital_system(num_days=NUMBER_OF_DAYS, excel=EXCEL_PATH)
    print_hospital_data(results)

if __name__ == "__main__":
    main()