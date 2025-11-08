from flask import Flask, request, jsonify
from flask_cors import CORS 
import os

# Importar las extensiones, modelos y el agente
from extensions import db  # La instancia de SQLAlchemy
from models import Employee, Department, Job, Region, Country, Location # Para db.create_all() y setup
from db_agent import process_query # La función principal de la IA
# -----------------------------------------------------------------------------------

# --- 2. CONFIGURACIÓN DE LA APLICACIÓN ---
app = Flask(__name__)
CORS(app)

# Conexión a la base de datos Docker
DB_URL = 'postgresql://agente_user:password@localhost:5432/hr_database'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 3. INICIALIZAR LA BASE DE DATOS ---
# Vinculamos la instancia 'db' (de extensions.py) con nuestra 'app'
db.init_app(app)
# -----------------------------------------------------------------------------------

# --- 4. DEFINICIÓN DEL ENDPOINT DE LA API ---
@app.route('/ask-agent', methods=['POST'])
def ask_agent():
    with app.app_context():
        data = request.get_json()
        user_query = data.get('query', '')
        conversation_state = data.get('conversation_state', {})
        
        if not user_query:
            return jsonify({"agent_text": "Por favor, ingresa una consulta.", "type": "error"}), 400
            
        # Pasamos la sesión de la base de datos (db.session) a la función del agente
        agent_response = process_query(user_query, db_session=db.session, conversation_state=conversation_state)
        
        return jsonify(agent_response)

# --- 5. FUNCIÓN DE DIAGNÓSTICO E INICIO ---
def setup_database(app, db):
    """Crea tablas e inserta datos iniciales SOLO si es necesario y respeta FKs."""
    print("--- [SETUP] Intentando crear tablas y datos iniciales ---")
    try:
        # db.create_all() ahora sabe qué modelos crear porque
        # los modelos en models.py usaron la instancia 'db'
        db.create_all()
        print("✅ [SETUP] Tablas del esquema HR creadas o mapeadas con éxito.")
        
        # --- LÓGICA CLAVE: Confiar en Docker para la inserción ---
        # 'Employee' fue importado desde models.py
        if db.session.query(Employee).count() > 0:
            print("--- [SETUP] La base de datos ya contiene datos (cargados por Docker).")
        else:
            print("--- [SETUP] La base de datos está vacía. ¡Verifique que el script 2-hr_data.sql se ejecute en Docker!")
            
    except Exception as e:
        print("\n" + "="*50)
        print(f"❌ ERROR FATAL AL INICIALIZAR LA BASE DE DATOS ❌")
        print(f"Tipo de Error: {type(e).__name__}")
        print(f"Mensaje: {e}")
        print("="*50 + "\n")
        raise e

if __name__ == '__main__':
    with app.app_context():
        try:
            setup_database(app, db)
            
            # Si setup_database() fue exitoso, iniciamos el servidor
            print("\n--- [FLASK] INICIANDO SERVIDOR FLASK ---")
            app.run(debug=True)
            
        except Exception as e:
            print("🔴 [FLASK] No se puede iniciar el servidor debido a un fallo en la base de datos.")