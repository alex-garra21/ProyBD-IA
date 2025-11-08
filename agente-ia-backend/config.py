# config.py

# --- 3. Definición del Esquema de la Base de Datos (HR) - COMPLETA ---
DB_SCHEMA = {
    'employees': {
        'required': ['first_name', 'last_name', 'email', 'salary', 'hire_date', 'job_id', 'department_id'], 
        'optional': ['manager_id', 'phone_number', 'commission_pct'],
        'fields': ['employee_id', 'first_name', 'last_name', 'email', 'salary', 'hire_date', 'job_id', 'department_id', 'manager_id', 'phone_number', 'commission_pct']
    },
    'departments': {
        'required': ['department_name', 'location_id'],
        'optional': ['manager_id'],
        'fields': ['department_id', 'department_name', 'manager_id', 'location_id']
    },
    'jobs': {
        'required': ['job_id', 'job_title'], 
        'optional': ['min_salary', 'max_salary'],
        'fields': ['job_id', 'job_title', 'min_salary', 'max_salary']
    },
    'regions': {
        'required': ['region_name'], 
        'optional': [],
        'fields': ['region_id', 'region_name']
    },
    'countries': {
        'required': ['country_name', 'region_id'], 
        'optional': [],
        'fields': ['country_id', 'country_name', 'region_id']
    },
    'locations': {
        'required': ['city', 'country_id'], 
        'optional': ['street_address', 'postal_code', 'state_province'],
        'fields': ['location_id', 'street_address', 'postal_code', 'city', 'state_province', 'country_id']
    },
}

# --- 4. Extracción Simple de Datos y Condiciones ---

OPERATOR_MAP = {
'mayor a': '>',
    'mayor que': '>',
    'más de': '>',
    'gana más de': '>',
    'que ganan más de': '>', # Añadido
    'mas de': '>',
    'gana mas de': '>',
    'que ganan mas de': '>',
    
    'menor a': '<',
    'menor que': '<',
    'menos de': '<',
    'que ganan menos de': '<', # ¡Añadido!
    'gana menos de': '<', # Añadido
    
    'igual a': '==',
    'es': '==',
    'es igual a': '==',
    
    'no es': '!=',
}

FIELD_MAP = {
    # ------------------------------------
    # CAMPOS DE LA TABLA EMPLOYEES
    # ------------------------------------
    'id': 'employee_id',
    'id de empleado': 'employee_id',
    'identificador': 'employee_id',
    'nombre': 'first_name',
    'primer nombre': 'first_name',
    'apellido': 'last_name',
    'apellidos': 'last_name',
    'email': 'email',
    'correo': 'email',
    'correo electronico': 'email',
    'telefono': 'phone_number',
    'numero de telefono': 'phone_number',
    'fecha de contratacion': 'hire_date',
    'fecha contratacion': 'hire_date',
    'fecha de ingreso': 'hire_date',
    'id de puesto': 'job_id',
    'puesto': 'job_id',
    'trabajo': 'job_id',
    'salario': 'salary',
    'sueldo': 'salary',
    'comision': 'commission_pct',
    'porcentaje de comision': 'commission_pct',
    'pct comision': 'commission_pct',
    'id de manager': 'manager_id',
    'manager': 'manager_id',
    'jefe': 'manager_id',
    'id de departamento': 'department_id',
    'departamento': 'department_id',
    # ------------------------------------
    # CAMPOS DE LA TABLA JOBS (PUESTOS)
    # ------------------------------------
    'id de trabajo': 'job_id',
    #'id de puesto': 'job_id', # Ya está arriba, pero no afecta
    'titulo': 'job_title',
    'titulo de puesto': 'job_title',
    'salario minimo': 'min_salary',
    'minimo salario': 'min_salary',
    'salario maximo': 'max_salary',
    'maximo salario': 'max_salary',
    # ------------------------------------
    # CAMPOS DE LA TABLA DEPARTMENTS
    # ------------------------------------
    #'id de departamento': 'department_id', # Ya está arriba
    'nombre de departamento': 'department_name',
    'nombre del departamento': 'department_name',
    'id de localizacion': 'location_id',
    'localizacion': 'location_id',
    # ------------------------------------
    # CAMPOS DE LA TABLA LOCATIONS
    # ------------------------------------
    #'id de localizacion': 'location_id', # Ya está arriba
    'direccion': 'street_address',
    'calle': 'street_address',
    'codigo postal': 'postal_code',
    'zip code': 'postal_code',
    'ciudad': 'city',
    'estado': 'state_province',
    'provincia': 'state_province',
    'id de pais': 'country_id',
    'pais': 'country_id',
    # ------------------------------------
    # CAMPOS DE LA TABLA COUNTRIES
    # ------------------------------------
    #'id de pais': 'country_id', # Ya está arriba
    'nombre de pais': 'country_name',
    'id de region': 'region_id',
    'region': 'region_id',
    # ------------------------------------
    # CAMPOS DE LA TABLA REGIONS
    # ------------------------------------
    #'id de region': 'region_id', # Ya está arriba
    'nombre de region': 'region_name',
}

# --- MAPEO DE TRADUCCIÓN (INGLÉS -> ESPAÑOL) ---
TRANSLATION_MAP = {
    # Tablas
    'employees': 'empleados',
    'departments': 'departamentos',
    'jobs': 'puestos',
    'regions': 'regiones',
    'countries': 'países',
    'locations': 'ubicaciones',
    # Campos de EMPLOYEES
    'employee_id': 'ID de empleado',
    'first_name': 'nombre',
    'last_name': 'apellido',
    'email': 'correo electrónico',
    'phone_number': 'número de teléfono',
    'hire_date': 'fecha de contratación',
    'salary': 'salario',
    'commission_pct': 'porcentaje de comisión',
    'manager_id': 'ID de gerente',
    'department_id': 'ID de departamento',
    'job_id': 'ID de puesto',
    # Campos de DEPARTMENTS
    'department_id': 'ID de departamento',
    'department_name': 'nombre del departamento',
    'location_id': 'ID de ubicación',
    # Campos de JOBS
    'job_id': 'ID de puesto',
    'job_title': 'título del puesto',
    'min_salary': 'salario mínimo',
    'max_salary': 'salario máximo',
    # Campos de LOCATIONS
    'location_id': 'ID de ubicación',
    'street_address': 'dirección',
    'postal_code': 'código postal',
    'city': 'ciudad',
    'state_province': 'estado/provincia',
    'country_id': 'ID de país',
    # Campos de COUNTRIES
    'country_id': 'ID de país',
    'country_name': 'nombre del país',
    'region_id': 'ID de región',
    # Campos de REGIONS
    'region_id': 'ID de región',
    'region_name': 'nombre de la región',
}

# MAPEO DE PALABRAS CLAVE PARA FACILITAR LA EXTRACCIÓN
UPDATE_KEYWORDS = ['cambiar', 'actualizar', 'modificar']
WHERE_KEYWORDS = ['donde', 'del', 'con']