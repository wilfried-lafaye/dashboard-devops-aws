import os
import requests
import zipfile
from config import DATA_URL, RAW_DATA_PATH

def get_data():
    """
    Download the ZIP file from Zenodo and store it in data/raw/.
Then unzip its contents into data/raw/.
    """
    raw_folder = os.path.dirname(RAW_DATA_PATH)
    os.makedirs(raw_folder, exist_ok=True)

    zip_path = os.path.join(raw_folder, "temp.zip")

    print(f" Téléchargement des données depuis : {DATA_URL}")
    response = requests.get(DATA_URL)
    response.raise_for_status()

    with open(zip_path, "wb") as f:
        f.write(response.content)
    print(f" Fichier ZIP enregistré dans {zip_path}")

    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(raw_folder)
    print(f" Fichiers extraits dans {raw_folder}")

    os.remove(zip_path)
    print(" Téléchargement et extraction terminés.")

if __name__ == "__main__":
    get_data()