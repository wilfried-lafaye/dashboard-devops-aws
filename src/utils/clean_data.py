import pandas as pd
import os
import glob
import warnings
import re


warnings.simplefilter(action='ignore', category=FutureWarning)

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Folder containing raw CSV files (data/raw/)
data_folder = os.path.join(base_dir, "data", "raw")

# Folder to save the cleaned CSV (data/cleaned/)
output_folder = os.path.join(base_dir, "data", "cleaned")
os.makedirs(output_folder, exist_ok=True)

print(" Dossier source :", data_folder)
print(" Dossier de sortie :", output_folder)

# List all CSV files
all_files = glob.glob(os.path.join(data_folder, "*.csv"))

if not all_files:
    print(" Aucun fichier CSV trouvé dans le dossier raw !")
    exit()

list_of_dfs = []

# Reading files and adding the year
for filepath in all_files:
    match = re.search(r'(\d{4})', os.path.basename(filepath))
    year = int(match.group(1)) if match else None

    df = pd.read_csv(filepath, encoding="latin1", skiprows=1)
    df['Année'] = year
    list_of_dfs.append(df)

# Harmonize columns
all_columns = set()
for df in list_of_dfs:
    all_columns.update(df.columns)
all_columns = list(all_columns)

for i, df in enumerate(list_of_dfs):
    for col in all_columns:
        if col not in df.columns:
            df[col] = pd.NA
    list_of_dfs[i] = df[all_columns]

# Merge all files
final_df = pd.concat(list_of_dfs, ignore_index=True)

# Pollutant columns for which NA is replaced by the median
pollutants_cols = [
    'Moyenne annuelle de concentration de PM25 (ug/m3)',
    'Moyenne annuelle de concentration de PM25 ponderee par la population (ug/m3)',
    'Moyenne annuelle de concentration de PM10 (ug/m3)',
    'Moyenne annuelle de concentration de PM10 ponderee par la population (ug/m3)',
    'Moyenne annuelle de concentration de NO2 (ug/m3)',
    'Moyenne annuelle de concentration de NO2 ponderee par la population (ug/m3)',
    'Moyenne annuelle de concentration de O3 (ug/m3)',
    'Moyenne annuelle de concentration de O3 ponderee par la population (ug/m3)',
    "Moyenne annuelle d'AOT 40 (ug/m3.heure)",
    'Moyenne annuelle de somo 35 (ug/m3.jour)',
    'Moyenne annuelle de somo 35 pondere par la population (ug/m3.jour)'
]

# Fill NA with the median if the column exists
for col in pollutants_cols:
    if col in final_df.columns:
        final_df[col].fillna(final_df[col].median(skipna=True), inplace=True)

# COM Insee: replace NA with "Unknown"
if 'COM Insee' in final_df.columns:
    final_df['COM Insee'].fillna('Unknown', inplace=True)

# Population: replace NA with 0
if 'Population' in final_df.columns:
    final_df['Population'].fillna(0, inplace=True)

# Check for duplicates by commune and year
duplicated_count = final_df.duplicated(subset=['COM Insee', 'Année']).sum()
print(f"🔹 Nombre de doublons par 'COM Insee' et 'Année' : {duplicated_count}")

# Save the cleaned file
output_path = os.path.join(output_folder, "cleaned_air_quality_with_year.csv")
final_df.to_csv(output_path, index=False)

print(" Fusion et nettoyage terminés ! Dimension du DataFrame :", final_df.shape)
print(" Fichier sauvegardé dans :", output_path)
