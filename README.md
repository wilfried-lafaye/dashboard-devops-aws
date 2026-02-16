# Air Quality Data Science Project - France (2000-2015)

Interactive dashboard for analyzing historical reconstruction of background air pollution concentrations and regulatory indicators across France using a combined measurement and modeling approach.
test
---

## User Guide

This guide provides complete instructions for deploying and using the interactive air quality dashboard on any machine.

### 1. Prerequisites

Before starting, ensure your machine has:
- **Python 3.9+** installed
- **pip** package manager
- **Git** (optional, for cloning)
- **Internet connection** (required only for initial data download)

### 2. Installation

#### 2.1 Clone the Repository

```bash
git clone https://github.com/longeacc/DATA_Science_PROJECT_AirQuality_France.git
cd DATA_Science_PROJECT_AirQuality_France
```

#### 2.2 Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Running the Dashboard

Execute the main script:

```bash
python main.py
```

The dashboard will automatically open in your browser at:
`output_csv/superposed_graphs_map/FINAL_dashboard.html`

### 4. Using the Dashboard

**3 Main Tabs:**
- **📄 README**: Project documentation
- **🗺️ Interactive Map**: Pollution heatmap with year slider (2000-2015) and pollutant filters
- **📊 Graphs**: Histograms and scatter plots

**Navigation:**
- Click sidebar buttons to switch tabs
- Use year slider to see pollution evolution
- Check/uncheck pollutants to filter map data
- Hover over markers for detailed information

### 5. Project Structure

```
DATA_Science_PROJECT_AirQuality_France/
├── data/
│   ├── raw/              # Original data
│   ├── cleaned/          # Processed data
│   └── air_quality.db   # SQLite database
├── src/
│   ├── visualizations/  # Map & graph generators
│   └── utils/           # Data processing
├── output_csv/
│   └── superposed_graphs_map/  # Generated dashboard
├── main.py              # Run this
└── requirements.txt
```

---

## Data

### Data Source

The dataset is automatically downloaded from **Zenodo** via public API:

- **Source**: [Zenodo Record 5043645](https://zenodo.org/records/5043645)
- **URL**: `https://zenodo.org/records/5043645/files/Indicateurs_QualiteAir_France_Commune_2000-2015_Ineris_v.Sep2020.zip`
- **Format**: ZIP archive containing CSV files
- **Download**: Automatic on first run via `src/utils/get_data.py`

### Dataset Characteristics

- **Observations**: 529,305 rows
- **Variables**: 15 columns
- **Time Range**: 2000–2015 (excluding 2006)
- **Geographic Coverage**: All metropolitan French communes
- **Pollutants**: PM10, PM2.5, NO₂, O₃, AOT40, SOMO35

### Data Processing Pipeline

1. **Download** (`src/utils/get_data.py`): Fetches ZIP from Zenodo
2. **Extract**: Unzips files to `data/raw/`
3. **Clean** (`src/utils/clean_data.py`): Processes and validates data
4. **Store**: Generates SQLite database `data/air_quality.db`

**Note**: Internet connection required only for initial download. Dashboard works offline afterwards.

---

## Developer Guide

### Architecture Overview

```
main.py                    # Dashboard generator
├── generate_dashboard()   # Creates HTML
├── find_existing_file()   # Locates visualizations
└── to_rel()              # Computes paths

src/visualizations/
├── map.py                # Interactive map
├── superpose_scatter_plots.py
└── superpose_histograms.py
```

The `main.py` file creates a standalone HTML dashboard with 3 main tabs, automatic integration of existing visualizations, and tab-based responsive navigation.

### How to Add a New Page

#### Step 1: Locate Your Visualization File

In `main.py`, add:

```python
new_viz = find_existing_file(candidates_base, 'my_new_viz.html')
new_src = to_rel(new_viz) if new_viz else None
new_block = iframe_or_message(new_src, 'Visualization not found')
```

#### Step 2: Add Tab Button in Sidebar

```html
<button id="tab-newviz" class="tab-btn" onclick="switchTab('newviz')">
  📈 My New Viz
</button>
```

#### Step 3: Add Page Content

```html
<div id="page-newviz" class="page card">
  {new_block}
</div>
```

#### Step 4: Update JavaScript

```javascript
const pages = ['readme', 'map', 'graphs', 'newviz'];
```

### How to Add a Sub-Tab in Graphs

Add a new button in the subtabs section:

```html
<button id="subtab-myvis" class="tab-btn">My Graph</button>
```

Add click handler in JavaScript:

```javascript
myVisBtn?.addEventListener('click', function() {
  myVisBtn.classList.add('active');
  // Remove active from others
  histBtn.classList.remove('active');
  scatBtn.classList.remove('active');
  // Load your visualization
  frame.src = '{my_vis_src}';
});
```

### How to Generate New Visualizations

Create a new script in `src/visualizations/`:

```python
import pandas as pd
import plotly.graph_objects as go
import sqlite3

def create_my_visualization():
    # Load data
    conn = sqlite3.connect('data/air_quality.db')
    df = pd.read_sql_query('SELECT * FROM air_quality', conn)
    
    # Create visualization
    fig = go.Figure(...)
    
    # Save output
    output_path = 'assets/output_csv/FINAL_superposed_graphs_map/my_viz.html'
    fig.write_html(output_path)
    
if __name__ == '__main__':
    create_my_visualization()
```

---

## Analysis Report

### Overview: Air Pollution Evolution in France (2000-2015)

This section presents the main findings extracted from the air quality dataset covering 15 years of measurements across all French metropolitan communes.

### 1. Large Urban Areas

**Observed Trends:**
- **NO₂**: Significant decline from ~40 µg/m³ (2000) to ~25 µg/m³ (2015)
  - Sharpest decrease observed after 2008
- **PM₁₀**: Reduction from ~30 µg/m³ to ~20 µg/m³
- **O₃**: Stable or slight increase (~50-55 µg/m³)
  - Ozone is a secondary pollutant formed from precursors

**Key Factors:**
- Dense traffic and industrial activities are primary NO₂ and PM sources
- Gradual improvement due to:
  - Stricter vehicle emission standards (Euro norms)
  - Implementation of low-emission zones
  - Industrial process modernization

### 2. Suburban Areas

**Observed Trends:**
- **NO₂**: Decrease from ~25 µg/m³ (2000) to ~18 µg/m³ (2015)
- **PM₁₀**: Reduction from ~22 µg/m³ to ~17 µg/m³
- **O₃**: Often higher than urban centers (~55-60 µg/m³ in summer)

**Key Factors:**
- Pollution transport from adjacent urban areas
- Fewer localized mitigation measures
- Chemical transformation of pollutants during transport

### 3. Rural Areas

**Observed Trends:**
- **NO₂**: Stable, typically < 15 µg/m³
- **PM₁₀**: Stable around ~15 µg/m³
- **O₃**: High variability, summer peaks up to 70 µg/m³

**Key Factors:**
- Minimal local emission sources
- Heavily influenced by:
  - Long-range pollutant transport
  - Meteorological conditions
  - Agricultural activities (seasonal)

### 4. Main Conclusions

**General Trends:**
1. **Primary Pollutants (NO₂, PM)**: Overall decrease across all zones
   - Urban areas show fastest improvement rates
   - Reflects success of anti-pollution policies

2. **Secondary Pollutants (O₃)**: Complex spatial patterns
   - More problematic in suburban and rural areas
   - Requires regional-scale mitigation strategies

3. **Geographic Factors**: Pollution distribution influenced by:
   - Topography (valleys trap pollutants)
   - Climate patterns (wind, temperature inversions)
   - Population density and industrial concentration

**Policy Impact:**
The observed improvements demonstrate the effectiveness of:
- European emission standards (vehicles, industry)
- Energy transition initiatives
- Fleet modernization programs
- Local air quality action plans

**Remaining Challenges:**
- Ozone pollution in summer months
- Persistent hotspots in high-density urban areas
- Need for continued monitoring and adaptive policies

---

## Copyright and Code Attribution

### Declaration of Originality

I/We solemnly declare that the code provided in this repository was produced by me/us, **except for the specific lines and sections explicitly declared below**.

### Third-Party Code and References

#### 1. Leaflet.js Integration (`src/visualizations/map.py`)

**Source**: [Leaflet Documentation](https://leafletjs.com/)

**Lines**: HTML template section (lines 118-450 in `map.py`)

**Purpose**: Interactive map rendering

**Syntax Explanation**:
```javascript
var map = L.map('map').setView([46.603354, 1.888334], 6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
```
- `L.map()`: Creates Leaflet map instance
- `setView()`: Centers map on France coordinates
- `L.tileLayer()`: Adds OpenStreetMap tile layer

#### 2. Leaflet.heat Plugin (`src/visualizations/map.py`)

**Source**: [Leaflet.heat GitHub](https://github.com/Leaflet/Leaflet.heat)

**Lines**: Heatmap implementation (lines 380-395 in `map.py`)

**Purpose**: Pollution heatmap visualization

**Syntax Explanation**:
```javascript
var heat = L.heatLayer(heatData, {
    radius: 25,
    blur: 35,
    maxZoom: 10,
    gradient: {0.0: 'green', 0.5: 'yellow', 1.0: 'red'}
}).addTo(map);
```
- `L.heatLayer()`: Creates heatmap layer from coordinates
- `gradient`: Color scale for intensity values

#### 3. Marked.js Library (`main.py`)

**Source**: [Marked.js CDN](https://cdn.jsdelivr.net/npm/marked/marked.min.js)

**Lines**: Dashboard HTML template (line 152 in `main.py`)

**Purpose**: Markdown to HTML conversion for README display

**Syntax Explanation**:
```javascript
const md = "{readme_js}";
target.innerHTML = marked.parse(md);
```
- `marked.parse()`: Converts Markdown string to HTML

#### 4. Data Source and Processing

**Source**: [Zenodo - INERIS Air Quality Dataset](https://zenodo.org/records/5043645)

**Attribution**: Institut National de l'Environnement Industriel et des Risques (INERIS)

**License**: Creative Commons Attribution 4.0 International

**Files**: `src/utils/get_data.py`, data download logic

### Original Contributions

All code **not explicitly declared above** is original work produced by the project author(s), including:
- Dashboard generation logic (`main.py`)
- Data cleaning and processing pipeline (`src/utils/`)
- Visualization generation scripts (`src/visualizations/`)
- SQLite database integration
- Custom HTML/CSS styling
- Interactive controls and event handlers

### Legal Notice

**Any line or code section not declared in this Copyright section is considered to be produced by the author(s) of this project.**

**Absence or omission of proper attribution for borrowed code will be considered plagiarism and is subject to academic and legal consequences.**

---

## Future Enhancements

### Planned Features for Next Release

#### 1. Commune Search Functionality

**Feature Description:**
Add a search bar on the interactive map allowing users to search for specific communes by name or postal code.

**Implementation Plan:**

**Step 1: Add Search Bar UI**
```javascript
// In src/visualizations/map.py, add to HTML template:
<div id="search-control">
  <input type="text" id="commune-search" placeholder="🔍 Search commune...">
  <div id="search-results"></div>
</div>
```

**Step 2: Implement Autocomplete**
```javascript
// JavaScript search logic
const searchInput = document.getElementById('commune-search');
searchInput.addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase();
    const matches = Object.values(data_by_year[currentYear])
        .filter(c => c.nom.toLowerCase().includes(query))
        .slice(0, 10);
    displaySearchResults(matches);
});
```

**Step 3: Pin Commune on Map**
```javascript
function selectCommune(commune) {
    // Center map on commune
    map.setView([commune.latitude, commune.longitude], 12);
    
    // Add highlight marker
    const marker = L.marker([commune.latitude, commune.longitude], {
        icon: L.icon({
            iconUrl: 'pin-icon.png',
            iconSize: [32, 32]
        })
    }).addTo(map);
    
    // Display info panel
    showCommuneDetails(commune);
}
```

#### 2. Commune Detail Panel

**Feature Description:**
Display detailed pollution data and graphs for selected commune in a sidebar panel.

**Implementation Plan:**

**UI Structure:**
```html
<div id="commune-panel" class="hidden">
  <div class="panel-header">
    <h3 id="commune-name"></h3>
    <button id="close-panel">×</button>
  </div>
  <div class="panel-content">
    <div id="commune-info"></div>
    <div id="commune-graphs"></div>
  </div>
</div>
```

**Display Commune Information:**
```javascript
function showCommuneDetails(commune) {
    document.getElementById('commune-name').textContent = commune.nom;
    document.getElementById('commune-info').innerHTML = `
        <p><strong>Population:</strong> ${commune.population.toLocaleString()}</p>
        <p><strong>NO₂:</strong> ${commune.NO2} µg/m³</p>
        <p><strong>PM10:</strong> ${commune.PM10} µg/m³</p>
        <p><strong>PM2.5:</strong> ${commune.PM25} µg/m³</p>
        <p><strong>O₃:</strong> ${commune.O3} µg/m³</p>
    `;
}
```

#### 3. Time-Series Graphs for Commune

**Feature Description:**
Generate interactive Plotly graphs showing pollution evolution over time for the selected commune.

**Implementation:**
```javascript
function generateCommuneGraphs(communeData) {
    // Fetch all years data for this commune
    const timeSeriesData = getAllYearsData(communeData.nom);
    
    // Create line chart
    const trace = {
        x: timeSeriesData.years,
        y: timeSeriesData.NO2_values,
        type: 'scatter',
        name: 'NO₂'
    };
    
    Plotly.newPlot('commune-graphs', [trace], {
        title: `Pollution Evolution in ${communeData.nom}`,
        xaxis: {title: 'Year'},
        yaxis: {title: 'Concentration (µg/m³)'}
    });
}
```

#### 4. Technical Requirements

**Libraries to Add:**
- **Leaflet Search Plugin**: For autocomplete functionality
- **Plotly.js**: For interactive commune-specific graphs (if not already included)

**CSS Styling:**
```css
#search-control {
    position: absolute;
    top: 70px;
    left: 10px;
    z-index: 1000;
    background: white;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

#commune-panel {
    position: absolute;
    right: 10px;
    top: 10px;
    bottom: 10px;
    width: 350px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    overflow-y: auto;
    z-index: 1001;
}

#commune-panel.hidden {
    display: none;
}
```

**Database Query Optimization:**
```sql
-- Create index for faster commune lookups
CREATE INDEX idx_commune_name ON air_quality(commune);
CREATE INDEX idx_commune_year ON air_quality(commune, annee);
```

#### 5. Implementation Steps

1. **Update `src/visualizations/map.py`**:
   - Add search bar HTML
   - Implement search JavaScript logic
   - Add commune panel UI

2. **Create helper functions**:
   - `searchCommunes(query)`: Filter communes by name
   - `selectCommune(commune)`: Pin and display details
   - `generateCommuneGraphs(commune)`: Create time-series plots

3. **Update dashboard** (`main.py`):
   - Ensure commune panel integrates with existing tabs
   - Add instructions in README tab about search feature

4. **Test thoroughly**:
   - Search with partial names
   - Verify graph generation for all pollutants
   - Check performance with large datasets

#### 6. User Benefits

- **Quick access** to specific commune data
- **Visual comparison** of pollution trends over 15 years
- **Detailed insights** without browsing the entire map
- **Enhanced usability** for local authorities and researchers

---

**Project maintained by**: [longeacc] (https://github.com/longeacc)
                           [william-zee] (https://github.com/william-zee)
**License**: MIT (for original code) | CC-BY-4.0 (for INERIS data)
**Copyright** :

I declare on my honour that the code provided has been produced by me/us, with the exception of the lines below; for each line (or group of lines) borrowed, give the source reference and an explanation of the syntax used any line not declared above is deemed to have been produced by the author(s) of the project. The absence or omission of a declaration will be considered plagiarism.