# db_agent.py

import re
from sqlalchemy.orm import Session
from sqlalchemy import inspect # Necesario para inspeccionar los nombres de las columnas

# --- 1. Clasificación de Intención ---
def classify_intent(text):
    text_lower = text.lower()
    
    select_keywords = ["listar", "dame", "mostrar", "quienes", "cuantos", "lista", "ver"]
    if any(keyword in text_lower for keyword in select_keywords):
        return "SELECT"

    insert_keywords = ["insertar", "agregar", "crear", "nuevo", "ingresar"]
    if any(keyword in text_lower for keyword in insert_keywords):
        return "INSERT"
        
    delete_keywords = ["eliminar", "borrar", "quitar", "dar de baja"]
    if any(keyword in text_lower for keyword in delete_keywords):
        return "DELETE"
        
    update_keywords = ["actualizar", "modificar", "cambiar", "revisar"]
    if any(keyword in text_lower for keyword in update_keywords):
        return "UPDATE"
        
    return "UNKNOWN"

# --- 2. Extracción de Entidades (Tablas) - ACTUALIZADA ---
def extract_entities(text):
    """Extrae la tabla principal mencionada en la consulta."""
    entities = {}
    text_lower = text.lower()
    
    # Tablas de Entidades Principales
    if "empleado" in text_lower or "employees" in text_lower:
        entities['table'] = 'employees'
    elif "departamento" in text_lower or "departments" in text_lower:
        entities['table'] = 'departments'
    elif "trabajo" in text_lower or "jobs" in text_lower:
        entities['table'] = 'jobs'
    
    # Tablas de Entidades Geográficas
    elif "region" in text_lower or "regions" in text_lower:
        entities['table'] = 'regions'
    elif "pais" in text_lower or "countries" in text_lower:
        entities['table'] = 'countries'
    elif "ubicacion" in text_lower or "locations" in text_lower:
        entities['table'] = 'locations'
        
    return entities

# --- 3. Definición del Esquema de la Base de Datos (HR) - COMPLETA ---
DB_SCHEMA = {
    'employees': {
        'required': ['first_name', 'last_name', 'email', 'salary', 'hire_date'],
        'optional': ['job_id', 'department_id', 'manager_id', 'phone_number', 'commission_pct'],
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
        'required': ['country_id', 'country_name', 'region_id'], 
        'optional': [],
        'fields': ['country_id', 'country_name', 'region_id']
    },
    'locations': {
        'required': ['location_id', 'city', 'country_id'], 
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
    'que ganan más de': '>',

    'mas de': '>',
    'gana mas de': '>',
    'que ganan mas de': '>',
    
    'menor a': '<',
    'menor que': '<',
    'menos de': '<',
    'que ganan menos de': '<',
    
    'igual a': '==',
    'es': '==',
    
    'no es': '!=',
}

FIELD_MAP = {
    'salario': 'salary',
    'sueldo': 'salary',
    'apellido': 'last_name',
    'departamento': 'department_id',
    'email': 'email',
    'fecha de contratacion': 'hire_date',
    'id': 'employee_id', 
    'ciudad': 'city',
    'pais': 'country_id',
    'nombre de region': 'region_name',
}

def simple_data_extractor(text):
    """Intenta extraer nombres o un valor simple de la respuesta."""
    extracted = {}
    text_lower = text.lower()
    
    match_name = re.search(r'(a|en)\s+([^\s]+)\s+([^\s]+)', text_lower)
    if match_name:
        extracted['first_name'] = match_name.group(2).capitalize()
        extracted['last_name'] = match_name.group(3).capitalize()
    
    extracted['value'] = text.strip() 
        
    return extracted


def extract_conditions(text, table_name):
    """Analiza el texto para extraer una condición (campo, operador, valor)."""
    text_lower = text.lower()
    conditions = []
    
    for es_op, sql_op in OPERATOR_MAP.items():
        # Patrón: busca (Campo) [0 o más palabras] (Operador) [0 o más palabras] (Valor)
        pattern = rf'({"|".join(FIELD_MAP.keys())}).*?{re.escape(es_op)}.*?\s+(\S+)'
        match = re.search(pattern, text_lower)
        
        if match: 
            es_field = match.group(1) 
            value_str = match.group(2).replace('q', '').replace('$', '').replace(',', '')
            
            try:
                value = float(value_str)
            except ValueError:
                value = value_str
            
            conditions.append({
                'field': FIELD_MAP.get(es_field, es_field),
                'op': sql_op,
                'value': value
            })
            break 
            
    return conditions

# --- FUNCIÓN DE MAPEO DINÁMICO (CRÍTICA para SELECT) ---
def map_to_dict_dynamic(item, model_map):
    """Mapea una instancia de SQLAlchemy a un diccionario, extrayendo todas las columnas."""
    data = {}
    
    try:
        # Obtiene los nombres de las columnas del inspector de SQLAlchemy
        columns = inspect(item).mapper.columns.keys()
    except Exception:
        # Fallback si inspect falla (aunque no debería)
        return item.__dict__
        
    for col in columns:
        if col.startswith('_'):
            continue
            
        value = getattr(item, col)
        
        # 1. Conversión de tipos para JSON
        if value is not None:
             # Convertimos cualquier valor numérico (incluyendo Decimal/Numeric) a float para JSON
             if hasattr(value, 'as_integer_ratio'): # Una forma robusta de chequear si es numérico
                 data[col.upper()] = float(value)
             else:
                 data[col.upper()] = str(value)
        else:
             data[col.upper()] = None
    
    # 2. Arreglos de Presentación (Fusionar Nombre y Apellido)
    if 'FIRST_NAME' in data and 'LAST_NAME' in data:
         data['NOMBRE'] = f"{data.pop('FIRST_NAME')} {data.pop('LAST_NAME')}"
    
    data.pop('LAST_NAME', None)
    
    return data

# -----------------------------------------------------------------
# --- 5. Función Principal del Agente (CON db_session) ---
# -----------------------------------------------------------------
def process_query(user_query, db_session: Session = None, conversation_state={}):
    
    # Importar modelos localmente para evitar importación circular
    try:
        from api import Employee, Department, Job, Region, Country, Location
        MODEL_MAP = {
            'employees': Employee, 
            'departments': Department, 
            'jobs': Job,
            'regions': Region,
            'countries': Country,
            'locations': Location
        }
    except ImportError:
         return {'agent_text': f"Error crítico: No se pudieron cargar los modelos de la base de datos desde api.py.", 'type': 'error', 'conversation_state': {}}
    
    user_query = user_query.strip()

    # --- A) MANEJO DE ESTADO DE CONVERSACIÓN (Diálogo Activo) ---
    if conversation_state and conversation_state.get('intent') in ["INSERT", "UPDATE"] and user_query:
        intent = conversation_state['intent']
        table = conversation_state['table']
        
        extracted_data = simple_data_extractor(user_query)
        
        if 'value' in extracted_data and conversation_state.get('last_asked_field'):
            last_asked = conversation_state['last_asked_field']
            conversation_state['data_collected'][last_asked] = extracted_data['value']
            
            if last_asked in conversation_state['missing_fields']:
                conversation_state['missing_fields'].remove(last_asked)
        
    # --- B) INICIO DE NUEVA CONVERSACIÓN ---
    else:
        intent = classify_intent(user_query)
        entities = extract_entities(user_query)
        table = entities.get('table')
        
        initial_data = simple_data_extractor(user_query)
        if intent == "UNKNOWN":
            initial_data.pop('value', None)

        conversation_state = {
            'intent': intent,
            'table': table,
            'data_collected': initial_data,
            'missing_fields': [],
            'last_asked_field': None
        }

    # --- C) LÓGICA DE DIÁLOGO (SLOT FILLING para INSERT) ---
    if intent == "INSERT" and table:
        schema = DB_SCHEMA.get(table)
        if not schema:
             return {'agent_text': f"Error: No tengo un esquema definido para la tabla '{table}'.", 'type': 'error', 'conversation_state': {}}

        all_required = schema['required']
        current_data = conversation_state['data_collected']
        
        missing = [field for field in all_required if field not in current_data]
        conversation_state['missing_fields'] = missing 
        
        if missing:
            next_field = missing[0]
            conversation_state['last_asked_field'] = next_field
            
            prompt_text = "Por favor, dime el valor para el campo: **{}**.".format(next_field)
            if next_field == 'hire_date':
                prompt_text = "Por favor, dime la **fecha de contratación** (formato YYYY-MM-DD)."
            
            agent_text = f"Entendí la inserción en la tabla **{table}**. {prompt_text}"
            
            return {
                'agent_text': agent_text,
                'type': 'dialog_needed',
                'conversation_state': conversation_state
            }
        else:
            # Ejecutar INSERT
            try:
                Model = MODEL_MAP.get(table)
                
                if Model:
                    data_to_insert = {k: v for k, v in current_data.items() if k in schema['fields']}
                    
                    # Para la tabla employees, necesitamos un employee_id único (PK)
                    if table == 'employees':
                         # CRÍTICO: Usar db_session.query(Model) para obtener el máximo ID
                         max_id_result = db_session.query(Employee.employee_id).order_by(Employee.employee_id.desc()).first()
                         
                         # max_id_result es una tupla, tomamos el primer elemento si existe
                         current_max_id = max_id_result[0] if max_id_result else 205 # Usamos 205 como un ID base seguro
                         
                         data_to_insert['employee_id'] = current_max_id + 1
                         
                    new_record = Model(**data_to_insert)
                    db_session.add(new_record)
                    db_session.commit()
                    
                    sql_display = f"INSERT INTO {table} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join([f'{v!r}' for v in data_to_insert.values()])});"
                    
                    return {
                        'agent_text': f"✅ ¡Inserción realizada con éxito en **{table}**!",
                        'sql_statement': sql_display,
                        'type': 'query_success',
                        'conversation_state': {}
                    }
                else:
                    raise Exception(f"No se encontró el modelo para la tabla {table}")

            except Exception as e:
                db_session.rollback()
                return {
                    'agent_text': f"❌ Error al ejecutar la inserción en la BD: {e}",
                    'sql_statement': None,
                    'type': 'error',
                    'conversation_state': {}
                }

    # --- D) LÓGICA DE SELECT (Avanzada con Condiciones) ---
    elif intent == "SELECT" and table:
        try:
            Model = MODEL_MAP.get(table)
            if not Model:
                return {'agent_text': f"No se encontró el modelo para {table}.", 'type': 'error', 'conversation_state': {}}

            # 1. Extracción de condiciones
            conditions = extract_conditions(user_query, table)
            
            query = db_session.query(Model)
            sql_display_condition = ""

            if conditions:
                condition = conditions[0]
                field = condition['field']
                value = condition['value']
                op = condition['op']

                column = getattr(Model, field, None)
                if column is None:
                    raise Exception(f"Campo '{field}' no válido para la tabla '{table}'")

                # Mapping de operadores a métodos de SQLAlchemy
                if op == '>':
                    query = query.filter(column > value)
                elif op == '<':
                    query = query.filter(column < value)
                elif op == '==':
                    query = query.filter(column == value)
                elif op == '!=':
                    query = query.filter(column != value)
                
                sql_display_condition = f" WHERE {field} {op} {value}"
            
            # 3. Ejecutar la consulta y mostrar resultados
            # Limitamos la consulta a 10 resultados para rendimiento
            results = query.limit(10).all() 
            
            # --- USO DE MAPEO DINÁMICO ---
            data_list = [map_to_dict_dynamic(item, MODEL_MAP) for item in results]
            # ---------------------------

            return {
                'agent_text': f"Mostrando los primeros {len(data_list)} registros de **{table}** encontrados.",
                'sql_statement': f"SELECT * FROM {table}{sql_display_condition} LIMIT 10;",
                'type': 'query_result',
                'data': data_list,
                'conversation_state': {}
            }
            
        except Exception as e:
            return {'agent_text': f"❌ Error al consultar la BD: {e}", 'type': 'error', 'conversation_state': {}}

    # --- E) LÓGICA UPDATE, DELETE y ERRORES ---
    elif intent == "UPDATE":
        return {'agent_text': "Intención UPDATE reconocida. Lógica aún no implementada.", 'type': 'status', 'conversation_state': {}}
        
    elif intent == "DELETE":
        return {'agent_text': "Intención DELETE reconocida. Lógica aún no implementada.", 'type': 'status', 'conversation_state': {}}
        
    elif intent == "UNKNOWN" or not table:
         return {
            'agent_text': f"No pude procesar la solicitud: **{user_query}**. Por favor, sé más específico sobre la tabla (ej. 'employees' o 'departments') y la acción.",
            'type': 'error',
            'conversation_state': {}
        }
    
    return {
        'agent_text': f"Entendí la intención: **{intent}**. Pero aún no tengo la lógica para ejecutar esta acción.",
        'type': 'status', 
        'conversation_state': {}
    }