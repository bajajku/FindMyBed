import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

# Load Excel file
file_path = "analysis_output/summary_report_20250313_030504.xlsx"
xls = pd.ExcelFile(file_path)

# Identify all configuration detail sheets
config_sheets = [sheet for sheet in xls.sheet_names if "Config_" in sheet and "Details" in sheet]

# Initialize PDF document
pdf = FPDF()

def visualize_configuration(sheet_name):
    # Load configuration data
    df = xls.parse(sheet_name)
    
    # Extract and parse config column
    df["parsed_config"] = df["config"].apply(json.loads)
    
    # Aggregate configuration values (assuming numerical values)
    aggregated_data = {}
    for config in df["parsed_config"]:
        for category, subconfig in config.items():
            if category not in aggregated_data:
                aggregated_data[category] = {}
            for key, value in subconfig.items():
                if key not in aggregated_data[category]:
                    aggregated_data[category][key] = []
                aggregated_data[category][key].append(value)
    
    # Plot and save figures to PDF
    for category, data in aggregated_data.items():
        plt.figure(figsize=(10, 5))
        sns.boxplot(data=pd.DataFrame(data))
        plt.title(f'Configuration Distribution for {category} ({sheet_name})')
        plt.xticks(rotation=45)
        img_path = f"{sheet_name}_{category}.png"
        plt.savefig(img_path)
        plt.close()
        
        # Add to PDF
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Configuration: {sheet_name} - {category}", ln=True, align='C')
        pdf.image(img_path, x=10, y=30, w=180)

# Process all config sheets
for sheet in config_sheets:
    visualize_configuration(sheet)

# Save PDF
pdf.output("configuration_visualizations.pdf")
