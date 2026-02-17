import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix 

class treatment_data():
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        
    def load_data(self):
        try:
            # Lecture du fichier CSV avec des paramètres pour gérer les erreurs
            self.data = pd.read_csv(
                self.file_path,
                on_bad_lines='skip',    # Skip les lignes problématiques (nouveau paramètre remplaçant error_bad_lines)
                low_memory=False        # Évite les problèmes de type d'inférence
            )
            print(f"Données chargées avec succès. Nombre de lignes : {len(self.data)}")
            return True
        except Exception as e:
            print(f"Erreur lors du chargement des données : {str(e)}")
            return False

    def preprocess(self):
        if self.data is None:
            print("Aucune donnée n'a été chargée. Appelez d'abord load_data()")
            return None
            
        try:
            # Afficher les informations sur les colonnes
            print("\nInformations sur les colonnes :")
            print(self.data.info())
            
            # Handle missing values
            self.data = self.data.dropna()
            print(f"\nAprès suppression des valeurs manquantes : {len(self.data)} lignes")
            
            # Remove problematic rows
            rows_to_remove = [838, 905, 874, 891, 2061]
            self.data = self.data.drop(index=rows_to_remove, errors='ignore')
            print(f"Après suppression des lignes problématiques : {len(self.data)} lignes")

            print("\nValeurs uniques par colonne :")
            for col in self.data.columns:
                n_unique = self.data[col].nunique()
                print(f"{col}: {n_unique} valeurs uniques")

            # Identify categorical columns
            categorical_columns = [col for col in self.data.columns 
                                if self.data[col].nunique() < 100 and self.data[col].dtype == 'object']
            
            print(f"\nColonnes catégorielles identifiées : {categorical_columns}")
            
            if categorical_columns:
                # Encode only categorical variables with limited unique values
                self.data = pd.get_dummies(self.data, columns=categorical_columns, drop_first=True)
                print("Encodage des variables catégorielles terminé")
            
            return self.data
            
        except Exception as e:
            print(f"Erreur lors du prétraitement : {str(e)}")
            return None
    


if __name__ == "__main__":

    treatment = treatment_data('effectifs.csv')
    
    # Load data
    if treatment.load_data():
        processed_data = treatment.preprocess()
        if processed_data is not None:
            print("\nAperçu des données traitées :")
            print(processed_data.head())
            print(f"\nDimensions finales des données : {processed_data.shape}")

# Zenodo dataset public URL

DATA_URL = "https://zenodo.org/records/5043645/files/Indicateurs_QualiteAir_France_Commune_2000-2015_Ineris_v.Sep2020.zip?download=1"

RAW_DATA_PATH = "data/raw/Indicateurs_QualiteAir_France_Commune_2000-2015_Ineris_v.Sep2020.csv"
