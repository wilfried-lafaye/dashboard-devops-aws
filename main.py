# import os
# import shutil
# import glob
# import pandas as pd
# from src.visualizations.scatter_plots import create_pollution_scatter
# from src.visualizations.histograms import create_pollution_histogram
# from src.utils.common_functions import load_commune_mappings, load_data_for_year

# # --- CONFIGURATION ---
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# STATIC_DIR = os.path.join(BASE_DIR, 'static')
# ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# # On s'assure que le dossier static existe
# if not os.path.exists(STATIC_DIR):
#     os.makedirs(STATIC_DIR)

# def generate_graphs():
#     """ Simule la génération ou vérifie que les données sont là """
#     print("--- 1. Vérification des données ---")
#     # Ici, tu peux remettre ton code de boucle sur les années si tu veux régénérer à chaque fois.
#     # Pour l'instant, on suppose que tes graphiques unitaires sont dans 'assets' ou 'output'
#     print("Données prêtes.")

# def create_viewer_page(title, source_folder_name, output_filename):
#     """ 
#     Cette fonction remplace le 'script magique'. 
#     Elle cherche les graphiques individuels et crée une page HTML pour les afficher tous.
#     """
#     print(f"--- Création du viewer : {title} ---")
    
#     # On cherche dans assets/source_folder_name (ex: assets/html_histograms)
#     search_dir = os.path.join(ASSETS_DIR, source_folder_name)
    
#     html = f"""<!DOCTYPE html>
#     <html><head><title>{title}</title>
#     <style>
#         body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f6; padding: 20px; text-align: center; }}
#         h1 {{ color: #333; margin-bottom: 30px; }}
#         .card {{ background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 0 auto 30px; max-width: 1000px; overflow: hidden; }}
#         .card-header {{ background: #f8f9fa; padding: 15px; border-bottom: 1px solid #eee; font-weight: bold; color: #555; }}
#         iframe {{ width: 100%; height: 550px; border: none; }}
#     </style></head><body><h1>{title}</h1>"""
    
#     found = False
#     if os.path.exists(search_dir):
#         files = sorted(glob.glob(os.path.join(search_dir, "*.html")))
#         for filepath in files:
#             filename = os.path.basename(filepath)
#             # Copie vers static pour que le serveur le voie
#             shutil.copy(filepath, os.path.join(STATIC_DIR, filename))
            
#             html += f"""
#             <div class="card">
#                 <div class="card-header">{filename}</div>
#                 <iframe src="/static/{filename}" loading="lazy"></iframe>
#             </div>
#             """
#             found = True
    
#     if not found:
#         html += "<p>Aucun graphique trouvé. Vérifiez la génération des données.</p>"
#         # On regarde si des fichiers traînent déjà dans static (cas de secours)
#         existing = glob.glob(os.path.join(STATIC_DIR, f"*{'scatter' if 'scatter' in output_filename else 'histogram'}*.html"))
#         if existing:
#              html += "<p><i>Des fichiers anciens ont été trouvés dans le cache, essayez de recharger.</i></p>"

#     html += "</body></html>"
    
#     with open(os.path.join(STATIC_DIR, output_filename), 'w', encoding='utf-8') as f:
#         f.write(html)
#     print(f"Viewer généré : {output_filename}")

# def generate_dashboard():
#     """ Génère le Dashboard Final avec le Beau Design (Sidebar + Tabs) """
#     print("--- 2. Génération du Dashboard Design ---")
    
#     # Copie de la carte vers static
#     map_src = os.path.join(ASSETS_DIR, 'output_csv', 'FINAL_superposed_graphs_map', 'interactive_pollution_map.html')
#     if os.path.exists(map_src):
#         shutil.copy(map_src, os.path.join(STATIC_DIR, 'interactive_pollution_map.html'))
    
#     # Contenu HTML (Le Vrai Design)
#     html_content = """
# <!DOCTYPE html>
# <html lang="fr">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Dashboard Pollution France</title>
#     <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
#     <style>
#         :root { --primary: #2c3e50; --accent: #3498db; --bg: #f4f7f6; --text: #333; --sidebar-width: 250px; }
#         body { margin: 0; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: var(--bg); display: flex; height: 100vh; overflow: hidden; }
        
#         /* Sidebar */
#         .sidebar { width: var(--sidebar-width); background: var(--primary); color: white; display: flex; flex-direction: column; box-shadow: 2px 0 5px rgba(0,0,0,0.1); z-index: 10; }
#         .brand { padding: 20px; font-size: 1.2rem; font-weight: bold; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); background: #1a252f; }
#         .menu { list-style: none; padding: 0; margin: 0; flex: 1; }
#         .menu li { border-bottom: 1px solid rgba(255,255,255,0.05); }
#         .menu button { width: 100%; padding: 15px 20px; background: none; border: none; color: #ecf0f1; text-align: left; cursor: pointer; font-size: 1rem; transition: all 0.3s; display: flex; align-items: center; gap: 10px; }
#         .menu button:hover { background: rgba(255,255,255,0.1); padding-left: 25px; }
#         .menu button.active { background: var(--accent); border-left: 4px solid white; }
        
#         /* Main Content */
#         .main { flex: 1; position: relative; display: flex; flex-direction: column; }
#         .header { background: white; padding: 15px 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }
#         .header h2 { margin: 0; font-size: 1.2rem; color: var(--primary); }
        
#         /* Frames */
#         .content-area { flex: 1; position: relative; padding: 0; overflow: hidden; }
#         iframe { width: 100%; height: 100%; border: none; position: absolute; top: 0; left: 0; opacity: 0; z-index: 0; transition: opacity 0.3s; pointer-events: none; }
#         iframe.active { opacity: 1; z-index: 1; pointer-events: all; }
        
#         /* Readme Container */
#         #readme-container { padding: 40px; overflow-y: auto; background: white; height: 100%; box-sizing: border-box; display: none; }
#         #readme-container.active { display: block; }
#         .markdown-body { max-width: 800px; margin: 0 auto; line-height: 1.6; color: #24292e; }
#         h1, h2, h3 { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
#         pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; }
#     </style>
# </head>
# <body>

#     <div class="sidebar">
#         <div class="brand"><i class="fas fa-smog"></i> Pollution France</div>
#         <ul class="menu">
#             <li><button class="nav-btn active" onclick="show('readme', this)"><i class="fas fa-file-alt"></i> Documentation</button></li>
#             <li><button class="nav-btn" onclick="show('map', this)"><i class="fas fa-map-marked-alt"></i> Carte Interactive</button></li>
#             <li><button class="nav-btn" onclick="show('hist', this)"><i class="fas fa-chart-bar"></i> Histogrammes</button></li>
#             <li><button class="nav-btn" onclick="show('scatter', this)"><i class="fas fa-chart-line"></i> Scatter Plots</button></li>
#         </ul>
#         <div style="padding: 20px; font-size: 0.8rem; text-align: center; color: #bdc3c7;">
#             Projet DevOps 2026<br>v2.0
#         </div>
#     </div>

#     <div class="main">
#         <div class="header">
#             <h2 id="page-title">Documentation du Projet</h2>
#             <div style="font-size: 0.9rem; color: #7f8c8d;">Status: <span style="color: #27ae60; font-weight: bold;">● En ligne</span></div>
#         </div>

#         <div class="content-area">
#             <div id="readme-container" class="active">
#                 <div class="markdown-body">
#                     <h1>Bienvenue sur le Dashboard</h1>
#                     <p>Ce projet visualise les données de pollution en France entre 2000 et 2016.</p>
#                     <h3>Fonctionnalités :</h3>
#                     <ul>
#                         <li><b>Carte :</b> Visualisation géographique des stations.</li>
#                         <li><b>Histogrammes :</b> Répartition des polluants.</li>
#                         <li><b>Scatter Plots :</b> Corrélation entre polluants.</li>
#                     </ul>
#                     <p><i>Utilisez le menu à gauche pour naviguer.</i></p>
#                 </div>
#             </div>

#             <iframe id="frame-map" src="/static/interactive_pollution_map.html"></iframe>
#             <iframe id="frame-hist" src="/static/FINAL_histogrammes_viewer.html"></iframe>
#             <iframe id="frame-scatter" src="/static/FINAL_superposed_scatter_plots.html"></iframe>
#         </div>
#     </div>

#     <script>
#         function show(id, btn) {
#             // Gestion boutons
#             document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
#             btn.classList.add('active');

#             // Gestion Titre
#             const titles = {
#                 'readme': 'Documentation du Projet',
#                 'map': 'Carte de France des Polluants',
#                 'hist': 'Distributions (Histogrammes)',
#                 'scatter': 'Corrélations (Scatter Plots)'
#             };
#             document.getElementById('page-title').innerText = titles[id];

#             // Masquer tout
#             document.getElementById('readme-container').classList.remove('active');
#             document.querySelectorAll('iframe').forEach(f => f.classList.remove('active'));

#             // Afficher la cible
#             if (id === 'readme') {
#                 document.getElementById('readme-container').classList.add('active');
#             } else {
#                 // Astuce : on recharge l'iframe si elle était vide (erreur 404 précédente)
#                 const frame = document.getElementById('frame-' + id);
#                 frame.classList.add('active');
#             }
#         }
#     </script>
# </body>
# </html>
#     """
    
#     with open(os.path.join(STATIC_DIR, 'FINAL_dashboard.html'), 'w', encoding='utf-8') as f:
#         f.write(html_content)
#     print("Dashboard Design généré dans static/FINAL_dashboard.html")

# if __name__ == '__main__':
#     generate_graphs()
#     # On lance les "aspirateurs" à graphiques (l'équivalent de ton script de tout à l'heure)
#     create_viewer_page('Histogrammes', 'html_histograms', 'FINAL_histogrammes_viewer.html')
#     create_viewer_page('Scatter Plots', 'scatter', 'FINAL_superposed_scatter_plots.html')
#     # On génère la belle page d'accueil
#     generate_dashboard()
"""
Script HYBRIDE : Design Original + Compatibilité Kubernetes.
Ce script génère le dashboard avec ton design exact, mais corrige les liens pour qu'ils fonctionnent.
"""
import os
import shutil
import glob
import html
import pandas as pd
from src.utils.common_functions import load_commune_mappings, load_data_for_year
# On garde tes imports d'origine s'ils fonctionnent
try:
    from src.visualizations.scatter_plots import create_pollution_scatter
    from src.visualizations.histograms import create_pollution_histogram
except ImportError:
    pass

# --- CONFIGURATION KUBERNETES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

def generate_graphs():
    """ 
    Partie 1: Génération des données (identique à ton script original, simplifié)
    """
    print("=== Génération des graphiques (Simulation ou Exécution) ===")
    # Ici, tu peux remettre ta boucle de calcul si nécessaire. 
    # Pour l'instant, on suppose que les fichiers sont déjà générés ou présents dans assets.
    pass

def create_viewer_page(title, source_subfolder, output_filename):
    """
    Partie 2: Création des viewers (Histogrammes/Scatter) manquants.
    On crée une page simple qui liste toutes les images trouvées.
    """
    print(f"--- Création du viewer : {title} ---")
    search_dir = os.path.join(ASSETS_DIR, source_subfolder)
    
    html_content = f"""<!DOCTYPE html>
    <html><head><title>{title}</title>
    <style>
        body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; background: #f5f7fb; padding: 20px; text-align: center; }}
        h1 {{ color: #2c3e50; margin-bottom: 30px; }}
        .graph-container {{ background: white; margin: 0 auto 30px; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); max-width: 1000px; }}
        .graph-title {{ padding: 10px; font-weight: bold; color: #555; border-bottom: 1px solid #eee; }}
        iframe {{ width: 100%; height: 600px; border: none; }}
    </style></head><body><h1>{title}</h1>"""
    
    found = False
    if os.path.exists(search_dir):
        files = sorted(glob.glob(os.path.join(search_dir, "*.html")))
        for filepath in files:
            filename = os.path.basename(filepath)
            # IMPORTANT: On copie vers static pour que le serveur le voie
            shutil.copy(filepath, os.path.join(STATIC_DIR, filename))
            
            html_content += f"""
            <div class="graph-container">
                <div class="graph-title">{filename}</div>
                <iframe src="/static/{filename}" loading="lazy"></iframe>
            </div>
            """
            found = True
            
    if not found:
        # Tentative de récupération depuis le cache static
        keyword = 'scatter' if 'scatter' in output_filename else 'histogram'
        existing = glob.glob(os.path.join(STATIC_DIR, f"*{keyword}*.html"))
        if existing:
             for filepath in existing:
                if filepath.endswith(output_filename): continue
                filename = os.path.basename(filepath)
                html_content += f"""<div class="graph-container"><div class="graph-title">{filename}</div><iframe src="/static/{filename}"></iframe></div>"""
                found = True

    if not found:
        html_content += "<p>Aucun graphique trouvé.</p>"

    html_content += "</body></html>"
    
    with open(os.path.join(STATIC_DIR, output_filename), 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_dashboard():
    """
    Partie 3: Le Dashboard avec TON DESIGN EXACT.
    Seuls les chemins src="..." sont modifiés pour pointer vers /static/.
    """
    print("\n=== Génération du dashboard ===")
    dashboard_path = os.path.join(STATIC_DIR, 'FINAL_dashboard.html')

    # 1. Récupération de la carte
    map_src_path = "/static/interactive_pollution_map.html"
    # On cherche la carte physique pour la copier
    possible_maps = [
        os.path.join(ASSETS_DIR, 'output_csv', 'FINAL_superposed_graphs_map', 'interactive_pollution_map.html'),
        os.path.join(ASSETS_DIR, 'maps', 'interactive_pollution_map.html')
    ]
    for p in possible_maps:
        if os.path.exists(p):
            shutil.copy(p, os.path.join(STATIC_DIR, 'interactive_pollution_map.html'))
            break

    # 2. Liens vers les viewers qu'on vient de créer/vérifier
    hist_src = "/static/FINAL_histogrammes_viewer.html"
    scatter_src = "/static/FINAL_superposed_scatter_plots.html"

    # 3. Le README
    readme_content = "# Projet DevOps\nBienvenue."
    if os.path.exists(os.path.join(BASE_DIR, 'README.md')):
        with open(os.path.join(BASE_DIR, 'README.md'), 'r', encoding='utf-8') as f:
            readme_content = f.read()
    readme_js = readme_content.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')
    
    # 4. Bloc Carte (Gestion erreur)
    map_block = f'<iframe src="{map_src_path}" class="content-frame"></iframe>'

    # --- TON CODE HTML ORIGINAL (INTOUCHÉ SAUF VARIABLES) ---
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Dashboard Pollution - README | Carte | Graphiques</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #f5f7fb; --surface: #ffffff; --text: #2c3e50; --muted: #6b7280;
      --primary: #2563eb; --primary-600: #1d4ed8; --primary-700: #1e40af;
      --border: #e5e7eb; --sidebar-width: 220px;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }}
    .sidebar {{ width: var(--sidebar-width); background: var(--surface); border-right: 2px solid var(--border); display: flex; flex-direction: column; }}
    .header {{ background: linear-gradient(135deg, var(--primary), var(--primary-700)); color:#fff; padding: 20px 16px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
    .header h1 {{ margin:0; font-size: 16px; font-weight: 600; line-height: 1.3; }}
    .tabs {{ display:flex; flex-direction: column; gap:6px; padding: 16px 12px; flex: 1; }}
    .tab-btn {{ padding:12px 14px; border:1px solid var(--border); background: #fff; color: var(--text); border-radius:8px; cursor:pointer; font-weight:600; font-size:14px; text-align: left; transition: all 0.2s; }}
    .tab-btn:hover {{ background: #f9fafb; border-color: var(--primary-600); }}
    .tab-btn.active {{ background: var(--primary); color:#fff; border-color: transparent; box-shadow: 0 2px 4px rgba(37,99,235,0.2); }}
    .main-content {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
    .container {{ flex: 1; padding: 0; overflow: hidden; }}
    .card {{ background: var(--surface); border:1px solid var(--border); border-radius: 10px; box-shadow: 0 2px 8px rgba(16,24,40,0.04); padding: 20px; height: 100%; overflow: auto; }}
    .card.map-card {{ padding: 0; overflow: hidden; }}
    .content-frame {{ width: 100%; height: 100%; border: none; border-radius: 8px; }}
    .missing {{ padding: 16px; color: #b91c1c; background: #fee2e2; border: 1px solid #fecaca; border-radius: 8px; }}
    .readme {{ line-height: 1.6; color: var(--text); }}
    .readme h1, .readme h2, .readme h3 {{ margin-top: 1.2em; }}
    .readme pre {{ background:#0b1020; color:#e5e7eb; padding:12px; border-radius:8px; overflow:auto; }}
    .subtabs {{ display:flex; gap:8px; margin-bottom: 12px; }}
    .page {{ display: none; height: 100%; }}
    .page.active {{ display: block; }}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      // Tabs gestion
      const pages = ['readme','map','graphs'];
      function show(id) {{
        pages.forEach(p => {{
          document.getElementById('page-'+p).style.display = (p===id)?'block':'none';
          document.getElementById('tab-'+p).classList.toggle('active', p===id);
        }});
      }}
      window.switchTab = function(id) {{
        pages.forEach(p => {{
          const page = document.getElementById('page-'+p);
          const tab = document.getElementById('tab-'+p);
          if (p === id) {{
            page.classList.add('active');
            tab.classList.add('active');
          }} else {{
            page.classList.remove('active');
            tab.classList.remove('active');
          }}
        }});
      }};
      window.switchTab('readme');

      // Render README markdown
      const md = "{readme_js}";
      const target = document.getElementById('readme-content');
      try {{ target.innerHTML = marked.parse(md); }} catch(e) {{ target.textContent = md; }}

      // Graphs subtabs
      const histBtn = document.getElementById('subtab-hist');
      const scatBtn = document.getElementById('subtab-scat');
      const frame = document.getElementById('graphs-frame');
      
      // URLs injectées par Python
      const histUrl = '{hist_src}';
      const scatUrl = '{scatter_src}';

      histBtn?.addEventListener('click', function() {{
        histBtn.classList.add('active'); scatBtn.classList.remove('active');
        frame.src = histUrl;
      }});
      scatBtn?.addEventListener('click', function() {{
        scatBtn.classList.add('active'); histBtn.classList.remove('active');
        frame.src = scatUrl;
      }});
      // Default subtab
      if (histBtn && scatBtn) {{ histBtn.click(); }}
    }});
  </script>
</head>
<body>
  <div class="sidebar">
    <div class="header">
      <h1>📊 Dashboard Pollution Atmosphérique France</h1>
    </div>
    <div class="tabs">
      <button id="tab-readme" class="tab-btn" onclick="switchTab('readme')">📄 README</button>
      <button id="tab-map" class="tab-btn" onclick="switchTab('map')">🗺️ Carte Interactive</button>
      <button id="tab-graphs" class="tab-btn" onclick="switchTab('graphs')">📊 Graphiques</button>
    </div>
  </div>
  <div class="main-content">
    <div class="container">
      <div id="page-readme" class="page card">
        <div id="readme-content" class="readme"></div>
      </div>
      <div id="page-map" class="page card map-card">
        {map_block}
      </div>
      <div id="page-graphs" class="page card">
        <div class="subtabs">
          <button id="subtab-hist" class="tab-btn">Histogrammes</button>
          <button id="subtab-scat" class="tab-btn">Scatter Plots</button>
        </div>
        <iframe id="graphs-frame" class="content-frame" src="{hist_src}"></iframe>
    </div>
  </div>
</body>
</html>
"""

    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Dashboard généré avec succès : {dashboard_path}")


if __name__ == '__main__':
    # 1. On lance la génération (si besoin)
    generate_graphs()
    
    # 2. On prépare les Viewers (pour que les onglets Graphiques ne soient pas vides)
    create_viewer_page('Histogrammes', 'html_histograms', 'FINAL_histogrammes_viewer.html')
    create_viewer_page('Scatter Plots', 'scatter', 'FINAL_superposed_scatter_plots.html')
    
    # 3. On génère le Dashboard
    generate_dashboard()