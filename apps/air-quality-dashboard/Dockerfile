# # ON PASSE À PYTHON 3.11 POUR SUPPORTER GEOPANDAS
FROM python:3.11-slim

# Installation des outils système (ajout de git et g++ pour la compilation)
RUN apt-get update && apt-get install -y libpq-dev gcc g++ git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le projet
COPY . .

# Création du dossier static pour être sûr
RUN mkdir -p /app/static

EXPOSE 5000

# --- LE CHANGEMENT CRUCIAL ---
# On lance D'ABORD la génération (main.py) PUIS le serveur (server.py)
# Sans ça, ton dashboard sera vide.
CMD ["sh", "-c", "python main.py && python server.py"]