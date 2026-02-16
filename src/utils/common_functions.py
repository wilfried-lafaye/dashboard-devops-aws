import pandas as pd 
import numpy as np
import os 
import matplotlib.pyplot as plt
import seaborn as sns
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from plotly.offline import plot as write_html
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from visualizations.scatter_plots import create_pollution_scatter
from visualizations.histograms import create_pollution_histogram

class read_data:
    def __init__(self):
        pass

    @staticmethod
    def load_data(file_path):
        """
        Loads data from a CSV file with error handling and formatting.

Args:
file_path (str): Path to the CSV file to load

Returns:
pandas.DataFrame: DataFrame containing the loaded data, or None in case of error
        """
        try:
            if file_path is None:
                raise ValueError("Le chemin du fichier ne peut pas être None")
            
            if not os.path.exists(file_path):
                print(f"ERREUR : Le fichier '{file_path}' n'existe pas.")
                return None
                
            data = pd.read_csv(
                file_path,
                encoding='cp1252',    
                skiprows=1,           
                sep=',',              
                decimal='.',          
                thousands=None,       
                low_memory=False
            )
            
            if len(data.columns) not in [12, 14]:
                print(f"ATTENTION : Nombre incorrect de colonnes ({len(data.columns)}). Attendu : 12 ou 14")
                print("Colonnes trouvées :")
                print(data.columns.tolist())
                return None
                
            required_columns = [
                'COM Insee',
                'Commune',
                'Population',
                'Moyenne annuelle de concentration de NO2 (ug/m3)',
                'Moyenne annuelle de concentration de PM10 (ug/m3)',
                'Moyenne annuelle de concentration de O3 (ug/m3)'
            ]
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                print("ERREUR : Colonnes manquantes :")
                print(missing_columns)
                return None
                
            print("Fichier chargé avec succès!")
            return data
            
        except pd.errors.EmptyDataError:
            print(f"ERREUR : Le fichier '{file_path}' est vide.")
            return None
        except pd.errors.ParserError as e:
            print(f"ERREUR : Problème de format dans le fichier '{file_path}' : {e}")
            return None
        except Exception as e:
            print(f"ERREUR : Problème lors du chargement du fichier '{file_path}' : {e}")
            return None
    
    @staticmethod
    def process_data(df):
        """    
Processes the data to ensure that the columns are correctly separated and typed.    
"""
        if df is None:
            return None
        
        try:
            numeric_columns = df.columns[2:]
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print("\nVérification de la cohérence des données :")
            print(f"Nombre total de lignes : {len(df)}")
            print(f"Nombre de colonnes : {len(df.columns)}")
            
            return df
            
        except Exception as e:
            print(f"Erreur lors du traitement des données : {str(e)}")
            return None

    @staticmethod
    def create_commune_insee_dict(df):
        """ 
        Creates a complete dictionary of correspondences between INSEE codes and municipality names. 
     
        Returns: 
            tuple: (municipality_to_insee, insee_to_municipality)
                - commune_to_insee (dict): {commune_name (str): INSEE_code (str)}
- INSEE_to_commune (dict): {INSEE_code (str): commune_name (str)}
        """
        if df is None:
            print("Erreur : DataFrame non fourni")
            return None, None
            
        if 'COM Insee' not in df.columns or 'Commune' not in df.columns:
            print("Erreur : Les colonnes 'COM Insee' et 'Commune' sont requises")
            print(f"Colonnes disponibles : {df.columns.tolist()}")
            return None, None
            
        try:
            # Convert INSEE codes to string for consistency
            df['COM Insee'] = df['COM Insee'].astype(str)
            
            # Remove any potential duplicates
            df_unique = df[['Commune', 'COM Insee']].drop_duplicates()
            
            # Create the dictionaries
            commune_to_insee = dict(zip(df_unique['Commune'], df_unique['COM Insee']))
            insee_to_commune = dict(zip(df_unique['COM Insee'], df_unique['Commune']))
            
            
            print(f"\nDictionnaires créés avec succès:")
            print(f"- Nombre total de communes : {len(commune_to_insee)}")
            print(f"- Nombre de codes INSEE uniques : {len(insee_to_commune)}")
            
            if len(commune_to_insee) != len(insee_to_commune):
                print("\nATTENTION : Certaines communes ont le même code INSEE ou vice-versa")
            
            
            print("\nExemples de correspondances :")
            for commune, insee in list(commune_to_insee.items())[:5]:
                print(f"Commune: {commune:30} -> Code INSEE: {insee}")
                
            print("\nUtilisation des dictionnaires:")
            print("commune_to_insee['nom_commune'] -> renvoie le code INSEE")
            print("insee_to_commune['code_insee'] -> renvoie le nom de la commune")
            
            return commune_to_insee, insee_to_commune
            
        except Exception as e:
            print(f"Erreur lors de la création des dictionnaires : {str(e)}")
            print("Détails des colonnes du DataFrame :")
            print(df.info())
            return None, None


def load_commune_mappings():
    """    
    Loads the correspondences between INSEE codes and municipality names.
    
    Args:
        year (int): The year for which to load the data (default: 2000)
        
    Returns:
        tuple: (municipality_to_insee, insee_to_municipality) correspondence dictionaries
    """
    try:
        # Upload the CSV file
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_path = os.path.join(script_dir, "data", "raw", "Indicateurs_QualiteAir_France_Commune_2000_Ineris_v.Sep2020.csv")
        
        data = read_data.load_data(data_path)
        if data is None:
            raise ValueError("Impossible de charger les données pour les correspondances communes")
        
        # Create the mapping dictionaries
        commune_to_insee = dict(zip(data['Commune'], data['COM Insee']))
        insee_to_commune = dict(zip(data['COM Insee'], data['Commune']))
        
        return commune_to_insee, insee_to_commune
        
    except Exception as e:
        print(f"Erreur lors du chargement des correspondances communes")
        return None, None


def load_data_for_year(year):
    """    
    Loads data for a specific year.    
        
    Args:    
        year (int): The year for which to load data.    
        
    Returns:    
        pd.DataFrame: Data for the specified year, or None if an error occurs.    
    """
    try:
        if year == 2006:
            return None
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_path = os.path.join(script_dir, "data", "raw", f"Indicateurs_QualiteAir_France_Commune_{year}_Ineris_v.Sep2020.csv")
        
        data = read_data.load_data(data_path)
        if data is not None:
            data['Année'] = year
            data = read_data.process_data(data)
            print(f"Données pour {year} chargées avec succès.")
            return data
        return None
        
    except Exception as e:
        print(f"Erreur lors du chargement des données pour {year}: {str(e)}")
        return None


def process_and_visualize_data(data, insee_to_commune):
    """    
Processes and visualises air pollution data over several years.
    
    Args:
        data (pd.DataFrame): The DataFrame containing the data
        insee_to_commune (dict): Dictionary mapping INSEE codes to commune names
        
    Returns:
        dict: Dictionary containing the generated figures
    """
    
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(script_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nDossier de sortie créé : {output_dir}")
    
    
    all_figures = {}
    
    for year in sorted(data['Année'].unique()):
        print(f"\nCréation des visualisations pour l'année {year}...")
        year_data = data[data['Année'] == year]
        
        for pollutant in ['NO2', 'PM10', 'O3']:
            
            fig_scatter = create_pollution_scatter(year_data, insee_to_commune, pollutant)
            
            fig_hist = create_pollution_histogram(year_data, pollutant)
            
            scatter_file = os.path.join(output_dir, f'{pollutant}_moyenne_annuelle_{year}.html')
            hist_file = os.path.join(output_dir, f'{pollutant}_histogram_{year}.html')
            
            write_html(fig_scatter, scatter_file, auto_open=False, include_plotlyjs='cdn')
            write_html(fig_hist, hist_file, auto_open=False, include_plotlyjs='cdn')
            
            all_figures[f'{pollutant}_scatter_{year}'] = fig_scatter
            all_figures[f'{pollutant}_histogram_{year}'] = fig_hist
    
    print("\nToutes les visualisations ont été générées avec succès !")
    return all_figures