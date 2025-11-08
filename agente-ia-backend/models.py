# models.py
from extensions import db  # Importamos la instancia 'db' compartida
from sqlalchemy import Numeric, ForeignKey
# (Puedes necesitar importar otros tipos de Columnas si los usas)

# --- 2. DEFINICIÓN DE MODELOS (Esquema HR completo adaptado) ---

# Tabla 1: REGIONS
class Region(db.Model):
    __tablename__ = 'regions'
    region_id = db.Column(db.Integer, primary_key=True)
    region_name = db.Column(db.String(25), nullable=False, unique=True)
    countries = db.relationship('Country', backref='region', lazy=True)

# Tabla 2: COUNTRIES
class Country(db.Model):
    __tablename__ = 'countries'
    country_id = db.Column(db.String(2), primary_key=True)
    country_name = db.Column(db.String(40), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.region_id'), nullable=False)
    locations = db.relationship('Location', backref='country', lazy=True)

# Tabla 3: LOCATIONS
class Location(db.Model):
    __tablename__ = 'locations'
    location_id = db.Column(db.Integer, primary_key=True)
    street_address = db.Column(db.String(40), nullable=True)
    postal_code = db.Column(db.String(12), nullable=True)
    city = db.Column(db.String(30), nullable=False)
    state_province = db.Column(db.String(25), nullable=True)
    country_id = db.Column(db.String(2), db.ForeignKey('countries.country_id'), nullable=False)
    departments = db.relationship('Department', backref='location', lazy=True)

# Tabla 4: JOB (Trabajos)
class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.String(10), primary_key=True)
    job_title = db.Column(db.String(35), nullable=False)
    min_salary = db.Column(db.Numeric(8, 2), nullable=True)
    max_salary = db.Column(db.Numeric(8, 2), nullable=True)
    employees = db.relationship('Employee', backref='job', lazy=True)

# Tabla 5: DEPARTMENT (Departamentos)
class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(30), unique=True, nullable=False)
    manager_id = db.Column(db.Integer, nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=True)
    employees = db.relationship('Employee', backref='department', lazy=True)
    
    # Nuevo: Agregamos to_dict para las tablas de soporte
    def to_dict(self):
        return {
            'ID': self.department_id,
            'NOMBRE': self.department_name,
            'LOCATION_ID': self.location_id,
        }

# Tabla 6: EMPLOYEE (Empleados - la tabla central)
class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(25), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    hire_date = db.Column(db.String(10), nullable=True)
    salary = db.Column(db.Numeric(8, 2), nullable=False)
    commission_pct = db.Column(db.Numeric(2, 2), nullable=True)
    
    # Claves Foráneas
    job_id = db.Column(db.String(10), db.ForeignKey('jobs.job_id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=True)

    # RELACIÓN JERÁRQUICA (Manager - Apunta a sí misma)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=True)
    manager = db.relationship(
        'Employee', 
        remote_side='Employee.employee_id', 
        backref=db.backref('subordinates', lazy=True), 
        uselist=False
    )
    
    def to_dict(self):
        """Método simple para el SELECT sin mapeo dinámico (no usado en db_agent.py, pero bueno tenerlo)."""
        return {
            'id': self.employee_id,
            'nombre': f"{self.first_name} {self.last_name}",
            'salario': float(self.salary),
        }