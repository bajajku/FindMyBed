from config import *
from utils.simulation import simulate_hospital_system

def main():
    
    simulate_hospital_system(num_days=NUMBER_OF_DAYS, excel=EXCEL_PATH)

if __name__ == "__main__":
    main()