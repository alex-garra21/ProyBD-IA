# api.py (Versión Completa y Corregida)

from flask import Flask, request, jsonify
from flask_cors import CORS 
from db_agent import process_query 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import Numeric, ForeignKey
import os

# --- 1. CONFIGURACIÓN DE LA APLICACIÓN Y LA BASE DE DATOS (PostgreSQL con Docker) ---
app = Flask(__name__)
CORS(app) 

# Conexión a la base de datos Docker (de tu docker-compose.yml)
DB_URL = 'postgresql://agente_user:password@localhost:5432/hr_database'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) 
# -----------------------------------------------------------------------------------


# --- 2. DEFINICIÓN DE MODELOS (Esquema HR de Oracle adaptado) ---

# Tabla 1: JOB (Trabajos)
class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.String(10), primary_key=True)
    job_title = db.Column(db.String(35), nullable=False)
    employees = db.relationship('Employee', backref='job', lazy=True)

# Tabla 2: DEPARTMENT (Departamentos)
class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(30), unique=True, nullable=False)
    employees = db.relationship('Employee', backref='department', lazy=True)

# Tabla 3: EMPLOYEE (Empleados - la tabla central)
# ¡COLUMNAS FALTANTES AÑADIDAS AQUÍ!
class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(25), unique=True, nullable=False)
    hire_date = db.Column(db.String(10), nullable=True) # Simplificado
    salary = db.Column(db.Numeric(8, 2), nullable=False)
    
    # Claves Foráneas
    job_id = db.Column(db.String(10), db.ForeignKey('jobs.job_id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=True)

    # RELACIÓN JERÁRQUICA (Manager)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=True)
    manager = db.relationship(
        'Employee', 
        remote_side='Employee.employee_id', 
        backref=db.backref('subordinates', lazy=True), 
        uselist=False
    )

    def to_dict(self):
        """Convierte el objeto Employee a un diccionario para la respuesta JSON."""
        return {
            'id': self.employee_id,
            'nombre': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'salario': float(self.salary),
            'departamento_id': self.department_id
        }

# -----------------------------------------------------------------------------------


# --- 3. DEFINICIÓN DEL ENDPOINT DE LA API ---
@app.route('/ask-agent', methods=['POST'])
def ask_agent():
    with app.app_context():
        data = request.get_json()
        user_query = data.get('query', '')
        conversation_state = data.get('conversation_state', {}) 
        
        if not user_query:
            return jsonify({"agent_text": "Por favor, ingresa una consulta.", "type": "error"}), 400
            
        agent_response = process_query(user_query, db_session=db.session, conversation_state=conversation_state) 
        
        return jsonify(agent_response)

# -----------------------------------------------------------------------------------

# --- 4. FUNCIÓN DE DIAGNÓSTICO E INICIO ---

def setup_database(app, db):
    """Crea tablas e inserta datos iniciales, forzando la visualización de errores."""
    print("--- [SETUP] Intentando crear tablas y datos iniciales ---")
    try:
        db.create_all()
        print("✅ [SETUP] Tablas del esquema HR creadas con éxito.")
        
        if Department.query.count() == 0:
            print("--- [SETUP] Base de datos vacía. Insertando datos de prueba HR...")
            
            # Insertar Departamentos
            dep_sales = Department(department_id=10, department_name='Sales')
            dep_it = Department(department_id=20, department_name='IT')
            db.session.add_all([dep_sales, dep_it])
            
            # Insertar Trabajos
            job_mng = Job(job_id='IT_MNG', job_title='IT Manager')
            job_rep = Job(job_id='SAL_REP', job_title='Sales Representative')
            db.session.add_all([job_mng, job_rep])
            
            # Insertar Empleados de prueba
            db.session.add_all([
                Employee(employee_id=100, first_name='Steven', last_name='King', email='SKING', salary=24000.00, department_id=10, job_id='IT_MNG', hire_date='2003-06-17'),
                Employee(employee_id=101, first_name='Neena', last_name='Kochhar', email='NKOCHHAR', salary=17000.00, department_id=10, job_id='SAL_REP', hire_date='2005-09-21'),
                Employee(employee_id=200, first_name='Alberto', last_name='Perez', email='APERZ', salary=4500.00, department_id=20, job_id='SAL_REP', hire_date='2007-08-10')
            ])
            db.session.commit()
            print("✅ [SETUP] Datos de prueba HR insertados con éxito.")
        else:
            print("--- [SETUP] La base de datos ya contiene datos.")

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

