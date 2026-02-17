import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, send_from_directory

# --- CONFIGURATION ROBUSTE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/static')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)

def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.environ.get('DB_HOST', 'postgres-service'),
            database=os.environ.get('DB_NAME', 'postgres'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'password')
        )
    except: return None

def init_db():
    conn = get_db_connection()
    if conn:
        conn.cursor().execute('CREATE TABLE IF NOT EXISTS visiteurs (id SERIAL PRIMARY KEY, nom VARCHAR(100));')
        conn.commit(); conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nom = request.form.get('nom')
        conn = get_db_connection()
        if conn and nom:
            cur = conn.cursor()
            cur.execute('INSERT INTO visiteurs (nom) VALUES (%s)', (nom,))
            conn.commit(); conn.close()
        return redirect('/')

    dashboard_path = os.path.join(STATIC_FOLDER, 'FINAL_dashboard.html')
    content = "<div style='text-align:center; padding:50px;'><h1>⏳ Génération...</h1><p>Actualisez dans 10 secondes.</p></div>"
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as f: content = f.read()

    return render_template_string(content)

if __name__ == '__main__':
    if not os.path.exists(STATIC_FOLDER): os.makedirs(STATIC_FOLDER)
    init_db()
    app.run(host='0.0.0.0', port=5000)
