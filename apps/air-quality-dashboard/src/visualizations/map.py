import pandas as pd
import folium
from folium.plugins import HeatMap
import sqlite3
import json
import os

output_dir = "assets"
os.makedirs(output_dir, exist_ok=True)


print("🔄 Chargement des données depuis la base de données...")

# --- Load data from the SQLite database ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
db_path = os.path.join(base_dir, "data", "air_quality.db")

# Connect to the database
conn = sqlite3.connect(db_path)

# Using DISTINCT to avoid duplicates
query = """
SELECT DISTINCT com_insee, commune, population, annee, 
       pm25, pm10, no2, o3, aot40, somo35
FROM air_quality
ORDER BY annee, com_insee
"""
df_pollution = pd.read_sql_query(query, conn)
conn.close()

print(f"✅ Données chargées depuis la base : {len(df_pollution)} lignes")

# Renommer les colonnes pour correspondre au format attendu
df_pollution = df_pollution.rename(columns={
    'com_insee': 'COM Insee',
    'commune': 'Commune',
    'population': 'Population',
    'annee': 'Année',
    'pm25': 'Moyenne annuelle de concentration de PM2.5 (ug/m3)',
    'pm10': 'Moyenne annuelle de concentration de PM10 (ug/m3)',
    'no2': 'Moyenne annuelle de concentration de NO2 (ug/m3)',
    'o3': 'Moyenne annuelle de concentration de O3 (ug/m3)',
    'aot40': 'Moyenne annuelle de concentration de AOT 40 (ug/m3.h)',
    'somo35': 'Moyenne annuelle de concentration de somo 35 (ug/m3.j)'
})

# --- Load the contact details for the municipalities ---
df_communes = pd.read_csv(os.path.join(base_dir, "data", "cleaned", "base-officielle-codes-postaux.csv"), dtype={"code_commune_insee": str})

# --- Deduplicate municipalities ---
df_communes = df_communes.drop_duplicates(subset=['code_commune_insee'], keep='first')
print(f"✅ Communes uniques avec coordonnées: {len(df_communes)}")

# --- Prepare columns for merge ---
df_pollution['COM Insee'] = df_pollution['COM Insee'].astype(str)
df_communes['code_commune_insee'] = df_communes['code_commune_insee'].astype(str)

    # --- Merge to add latitude, longitude, and commune name ---
df_merged = df_pollution.merge(
    df_communes[['code_commune_insee', 'latitude', 'longitude', 'nom_de_la_commune']],
    left_on='COM Insee',
    right_on='code_commune_insee',
    how='left'
)

# --- Filter valid data ---
df_map = df_merged.dropna(subset=['latitude', 'longitude']).copy()

print(f"✅ Données chargées : {len(df_map)} communes avec coordonnées")

# Polluants
pollutants = {
    'PM10': 'Moyenne annuelle de concentration de PM10 (ug/m3)',
    'PM25': 'Moyenne annuelle de concentration de PM2.5 (ug/m3)',
    'NO2': 'Moyenne annuelle de concentration de NO2 (ug/m3)',
    'O3': 'Moyenne annuelle de concentration de O3 (ug/m3)',
    'AOT40': 'Moyenne annuelle de concentration de AOT 40 (ug/m3.h)',
    'SOMO35': 'Moyenne annuelle de concentration de somo 35 (ug/m3.j)'
}

# Get available years
years = sorted([int(y) for y in df_map['Année'].unique()])
print(f"📅 Années disponibles : {years}")

# Create a data dictionary by year and by municipality
data_by_year = {}
for year in years:
    df_year = df_map[df_map['Année'] == year]
    data_by_year[year] = {}
    
    for _, row in df_year.iterrows():
        commune_key = f"{row['latitude']:.6f}_{row['longitude']:.6f}"
        data_by_year[year][commune_key] = {
            'nom': row['nom_de_la_commune'] if pd.notna(row['nom_de_la_commune']) else row['Commune'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'population': int(row['Population']) if pd.notna(row['Population']) else 0,
        }
        
        # Add pollutant concentrations
        for pollutant_key, pollutant_col in pollutants.items():
            if pollutant_col in row and pd.notna(row[pollutant_col]):
                data_by_year[year][commune_key][pollutant_key] = float(row[pollutant_col])


html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carte Interactive de la Pollution en France</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
    }
    
    #map {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 20px !important;
        right: 20px !important;
    }
    
    #map-title {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        padding: 15px 30px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        z-index: 1000;
        font-family: Arial, sans-serif;
        font-size: 20px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
    }
    
    #year-control {
        position: absolute;
        top: 10px;
        right: 10px;
        background: white;
        padding: 12px 15px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        z-index: 1000;
        font-family: Arial, sans-serif;
        width: 200px;
    }
    
    #pollutant-control {
        position: absolute;
        top: 90px;
        right: 10px;
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        z-index: 1000;
        font-family: Arial, sans-serif;
        width: 200px;
        max-height: 280px;
        overflow-y: auto;
    }
    
    #legend {
        position: absolute;
        bottom: 30px;
        right: 10px;
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        z-index: 1000;
        font-family: Arial, sans-serif;
        width: 200px;
    }
    
    #year-slider {
        width: 100%;
        height: 6px;
        border-radius: 5px;
        background: #d3d3d3;
        outline: none;
        -webkit-appearance: none;
        margin-top: 8px;
    }
    
    #year-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #4CAF50;
        cursor: pointer;
    }
    
    #year-slider::-moz-range-thumb {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #4CAF50;
        cursor: pointer;
        border: none;
    }
    
    #year-display {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    
    .control-label {
        font-size: 12px;
        color: #666;
        margin-bottom: 5px;
        display: block;
    }
    
    .pollutant-checkbox {
        display: flex;
        align-items: center;
        margin: 6px 0;
        padding: 4px;
        border-radius: 4px;
        transition: background-color 0.2s;
    }
    
    .pollutant-checkbox:hover {
        background-color: #f0f0f0;
    }
    
    .pollutant-checkbox input {
        margin-right: 8px;
        width: 16px;
        height: 16px;
        cursor: pointer;
    }
    
    .pollutant-checkbox label {
        cursor: pointer;
        user-select: none;
        font-size: 13px;
    }
    
    h3 {
        margin-top: 0;
        margin-bottom: 12px;
        color: #2c3e50;
        font-size: 14px;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 6px;
    }
    
    .legend-scale {
        margin-top: 10px;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        margin: 5px 0;
        font-size: 12px;
    }
    
    .legend-color {
        width: 30px;
        height: 15px;
        margin-right: 8px;
        border-radius: 2px;
    }
    
    .leaflet-popup-content {
        font-family: Arial, sans-serif;
    }
    
    .popup-title {
        font-size: 16px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 5px;
    }
    
    .popup-info {
        margin: 5px 0;
        font-size: 13px;
    }
    
    .popup-pollutant {
        background-color: #f8f9fa;
        padding: 5px;
        margin: 3px 0;
        border-radius: 3px;
    }
</style>
</head>
<body>
    <div id="map-title">
        🗺️ Carte Interactive de la Pollution Atmosphérique en France
    </div>
    
    <div id="year-control">
        <span class="control-label">📅 Année</span>
        <div id="year-display">""" + str(years[0]) + """</div>
        <input type="range" id="year-slider" min="0" max=\"""" + str(len(years)-1) + """\" value="0" step="1">
    </div>
    
    <div id="pollutant-control">
        <h3>🧪 Polluants</h3>
"""

for pollutant_key in pollutants.keys():
    html_content += f"""
        <div class="pollutant-checkbox">
            <input type="checkbox" id="{pollutant_key}" value="{pollutant_key}">
            <label for="{pollutant_key}">{pollutant_key}</label>
        </div>
"""

html_content += """
    </div>
    
    <div id="map"></div>
    
    <div id="legend">
        <h3>📊 Légende</h3>
        <div class="legend-info" style="font-size: 11px; color: #666; margin-bottom: 8px;">
            Intensité de pollution
        </div>
        <div class="legend-scale">
            <div class="legend-item">
                <div class="legend-color" style="background: blue;"></div>
                <span>Faible</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: cyan;"></div>
                <span>Modérée</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: lime;"></div>
                <span>Moyenne</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: yellow;"></div>
                <span>Élevée</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: orange;"></div>
                <span>Très élevée</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: red;"></div>
                <span>Critique</span>
            </div>
        </div>
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 11px; color: #666;">
            💡 Cliquez sur les marqueurs pour plus d'infos
        </div>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    <script>
        var years = """ + json.dumps(years) + """;
        var dataByYear = """ + json.dumps(data_by_year) + """;
        var pollutants = """ + json.dumps(list(pollutants.keys())) + """;
        
        var yearSlider = document.getElementById('year-slider');
        var yearDisplay = document.getElementById('year-display');
        var map = null;
        var heatmapLayer = null;
        var markersLayer = null;
        
        // Initialiser la carte
        map = L.map('map').setView([46.5, 2.5], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
        
        markersLayer = L.layerGroup().addTo(map);
        
        // Initialiser la carte avec les données
        updateMap();
        
        function updateMap() {
            if (!map) return;
            
            var yearIndex = parseInt(yearSlider.value);
            var year = years[yearIndex];
            yearDisplay.textContent = year;
            
            // Récupérer les polluants sélectionnés
            var selectedPollutants = [];
            pollutants.forEach(function(pollutant) {
                var checkbox = document.getElementById(pollutant);
                if (checkbox && checkbox.checked) {
                    selectedPollutants.push(pollutant);
                }
            });
            
            // Nettoyer les anciens marqueurs
            if (markersLayer) {
                markersLayer.clearLayers();
            }
            
            // Supprimer l'ancienne heatmap
            if (heatmapLayer) {
                map.removeLayer(heatmapLayer);
                heatmapLayer = null;
            }
            
            // Préparer les données pour la heatmap et les marqueurs
            var heatData = [];
            var yearData = dataByYear[year];
            
            if (yearData) {
                Object.keys(yearData).forEach(function(communeKey) {
                    var commune = yearData[communeKey];
                    var lat = commune.latitude;
                    var lon = commune.longitude;
                    
                    // Calculer la valeur moyenne des polluants sélectionnés pour la heatmap
                    var totalValue = 0;
                    var count = 0;
                    
                    selectedPollutants.forEach(function(pollutant) {
                        if (commune[pollutant] !== undefined && commune[pollutant] !== null) {
                            totalValue += commune[pollutant];
                            count++;
                        }
                    });
                    
                    var avgValue = count > 0 ? totalValue / count : 0;
                    
                    // Ajouter à la heatmap si des polluants sont sélectionnés
                    if (selectedPollutants.length > 0 && avgValue > 0) {
                        heatData.push([lat, lon, avgValue / 100]); // Normaliser pour la heatmap
                    }
                    
                    // Créer le popup
                    var popupContent = '<div style="min-width: 220px;">';
                    popupContent += '<div class="popup-title">' + commune.nom + '</div>';
                    popupContent += '<div class="popup-info"><strong>👥 Population:</strong> ' + commune.population.toLocaleString('fr-FR') + '</div>';
                    
                    if (selectedPollutants.length > 0) {
                        popupContent += '<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">';
                        selectedPollutants.forEach(function(pollutant) {
                            if (commune[pollutant] !== undefined && commune[pollutant] !== null) {
                                popupContent += '<div class="popup-pollutant"><strong>' + pollutant + ':</strong> ' + commune[pollutant].toFixed(2) + ' µg/m³</div>';
                            }
                        });
                        popupContent += '</div>';
                    }
                    
                    popupContent += '</div>';
                    
                    // Ajouter un marqueur
                    var markerColor = selectedPollutants.length > 0 ? '#ff7800' : '#3388ff';
                    var marker = L.circleMarker([lat, lon], {
                        radius: 5,
                        fillColor: markerColor,
                        color: '#fff',
                        weight: 1.5,
                        opacity: 0.8,
                        fillOpacity: 0.6
                    }).bindPopup(popupContent);
                    
                    markersLayer.addLayer(marker);
                });
            }
            
            // Ajouter la nouvelle heatmap si des polluants sont sélectionnés
            if (heatData.length > 0) {
                heatmapLayer = L.heatLayer(heatData, {
                    radius: 25,
                    blur: 35,
                    maxZoom: 13,
                    max: 1.0,
                    gradient: {
                        0.0: 'blue',
                        0.3: 'cyan',
                        0.5: 'lime',
                        0.7: 'yellow',
                        0.9: 'orange',
                        1.0: 'red'
                    }
                }).addTo(map);
            }
        }
        
        // Event listeners
        yearSlider.addEventListener('input', updateMap);
        
        pollutants.forEach(function(pollutant) {
            var checkbox = document.getElementById(pollutant);
            if (checkbox) {
                checkbox.addEventListener('change', updateMap);
            }
        });
    </script>
</body>
</html>
"""

# --- Save the map ---
output_path = os.path.join(output_dir, 'interactive_pollution_map.html')

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Carte interactive créée : {output_path}")
print(f"📊 {len(years)} années disponibles")
print(f"🗺️ {len(df_map)} communes avec coordonnées")
print(f"🧪 {len(pollutants)} polluants disponibles")
