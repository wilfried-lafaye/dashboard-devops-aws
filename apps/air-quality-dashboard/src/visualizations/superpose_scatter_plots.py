import os
import webbrowser

def create_scatter_viewer():
    """
    Create an HTML viewer for superposed scatter plots of air pollutants.
    """
    # Directory containing the SCATTER HTML files
    html_source_dir = os.path.abspath("output_csv").replace("\\", "/")

    # Directory where the viewer will be created
    output_path = "output/FINAL_superposed_graphs_map/FINAL_scatter_viewer.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pollutants = ["NO2", "PM10", "O3", "SOMO35", "PM25"]
    years = [y for y in range(2000, 2016) if y != 2006]

    # ----------------------------------------------
    # HTML VIEWER
    # ----------------------------------------------

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Visualisation des Scatter Plots</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .controls {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; display: flex; align-items: center; gap: 20px; }}
        select {{ padding: 10px; font-size: 16px; border-radius: 5px; border: 2px solid #3498db; cursor: pointer; }}
        iframe {{ width: 100%; height: 90vh; border: none; display: block; }}  /* hauteur ajustée pour voir toutes les listes */
        .slider-container {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; text-align: center; }}
        .year-display {{ font-size: 22px; font-weight: bold; margin-top: 10px; color: #2c3e50; }}
        input[type=range] {{
            width: 300px;
            height: 12px;
            cursor: pointer;
        }}
        input[type=range]::-webkit-slider-thumb {{
            width: 20px;
            height: 20px;
            background: #3498db;
            border-radius: 50%;
            cursor: pointer;
            margin-top: -4px;
        }}
        input[type=range]::-moz-range-thumb {{
            width: 20px;
            height: 20px;
            background: #3498db;
            border-radius: 50%;
            cursor: pointer;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>📈 Scatter Plots - Polluants Atmosphériques</h1>
    </div>

    <div class="controls">
        <label>🧪 Polluant :</label>
        <select id="pollutant-select">
            {"".join([f'<option value="{p}">{p}</option>' for p in pollutants])}
        </select>
    </div>

    <div class="slider-container">
        <label>📅 Année :</label><br>
        <input type="range" id="year-slider" min="0" max="{len(years)-1}" value="0" step="1">
        <div class="year-display" id="year-display">{years[0]}</div>
    </div>

    <div class="graph-container">
        <iframe id="graph-frame"></iframe>
    </div>

    <script>
        const years = {years};
        const pollutantSelect = document.getElementById('pollutant-select');
        const yearSlider = document.getElementById('year-slider');
        const yearDisplay = document.getElementById('year-display');
        const graphFrame = document.getElementById('graph-frame');
        const basePath = "{html_source_dir}";

        function updateGraph() {{
            const pollutant = pollutantSelect.value;
            const year = years[parseInt(yearSlider.value)];
            yearDisplay.textContent = year;
            const filename = `${{pollutant}}_moyenne_annuelle_${{year}}.html`;
            graphFrame.src = `${{basePath}}/${{filename}}`;
        }}

        pollutantSelect.addEventListener('change', updateGraph);
        yearSlider.addEventListener('input', updateGraph);

        updateGraph();
    </script>

</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f" Viewer SCATTER créé : {output_path}")
    webbrowser.open('file://' + os.path.abspath(output_path))


if __name__ == "__main__":
    create_scatter_viewer()
