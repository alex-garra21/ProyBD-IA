# db_agent.py (Versión Completa y Corregida)

import re
from sqlalchemy.orm import Session
# Importamos los modelos desde api.py para poder usarlos en las consultas

# --- 1. Clasificación de Intención ---
def classify_intent(text):
    text_lower = text.lower()
    
    select_keywords = ["listar", "dame", "mostrar", "quienes", "cuantos", "lista"]
    if any(keyword in text_lower for keyword in select_keywords):
        return "SELECT"

    insert_keywords = ["insertar", "agregar", "crear", "nuevo"]
    if any(keyword in text_lower for keyword in insert_keywords):
        return "INSERT"
        
    delete_keywords = ["eliminar", "borrar", "quitar", "dar de baja"]
    if any(keyword in text_lower for keyword in delete_keywords):
        return "DELETE"
        
    update_keywords = ["actualizar", "modificar", "cambiar", "revisar"]
    if any(keyword in text_lower for keyword in update_keywords):
        return "UPDATE"
        
    return "UNKNOWN"

# --- 2. Extracción de Entidades (Tablas) ---
def extract_entities(text):
    """Extrae la tabla principal mencionada en la consulta."""
    entities = {}
    text_lower = text.lower()
    
    if "empleado" in text_lower or "employees" in text_lower:
        entities['table'] = 'employees'
    elif "departamento" in text_lower or "departments" in text_lower:
        entities['table'] = 'departments'
    elif "trabajo" in text_lower or "jobs" in text_lower:
        entities['table'] = 'jobs'
        
    return entities

# --- 3. Definición del Esquema de la Base de Datos (HR) ---
DB_SCHEMA = {
    'employees': {
        'required': ['first_name', 'last_name', 'email', 'salary'],
        'optional': ['job_id', 'department_id'],
        'fields': ['first_name', 'last_name', 'email', 'salary', 'job_id', 'department_id']
    },
    'departments': {
        'required': ['department_name'], 
        'optional': [],
        'fields': ['department_name']
    },
    'jobs': {
        'required': ['job_id', 'job_title'], 
        'optional': [],
        'fields': ['job_id', 'job_title']
    }
}

# --- 4. Extracción Simple de Datos ---
def simple_data_extractor(text):
    """Intenta extraer nombres o un valor simple de la respuesta."""
    extracted = {}
    text_lower = text.lower()
    
    # Intenta extraer Nombre y Apellido (Ej. 'a juan perez')
    match_name = re.search(r'(a|en)\s+([^\s]+)\s+([^\s]+)', text_lower)
    if match_name:
        extracted['first_name'] = match_name.group(2).capitalize()
        extracted['last_name'] = match_name.group(3).capitalize()
    
    # Asume que el texto es un valor para el campo solicitado
    extracted['value'] = text.strip() 
        
    return extracted

# -----------------------------------------------------------------
# --- 5. Función Principal del Agente (CON db_session) ---
# -----------------------------------------------------------------
def process_query(user_query, db_session: Session = None, conversation_state={}):
    """
    Procesa la consulta del usuario, gestiona el diálogo y ejecuta consultas/inserciones.
    """
    # Importar modelos localmente para evitar importación circular ---
    try:
        from api import Employee, Department, Job
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
        # Limpiamos 'value' si no es un dato de inicio (ej. 'hola')
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
            # 1. Si faltan campos, pedir el primero
            next_field = missing[0]
            conversation_state['last_asked_field'] = next_field
            
            agent_text = (
                f"Entendí la inserción en la tabla **{table}**. "
                f"Por favor, dime el valor para el campo: **{next_field}**."
            )
            return {
                'agent_text': agent_text,
                'type': 'dialog_needed',
                'conversation_state': conversation_state
            }
        else:
            # 2. Si todos los campos están, ejecutar INSERT (usando SQLAlchemy)
            try:
                Model = None
                if table == 'employees':
                    Model = Employee
                elif table == 'departments':
                    Model = Department
                
                if Model:
                    # Filtramos solo los campos que pertenecen al modelo
                    data_to_insert = {k: v for k, v in current_data.items() if k in schema['fields']}
                    
                    new_record = Model(**data_to_insert)
                    db_session.add(new_record)
                    db_session.commit()
                    
                    sql_display = f"INSERT INTO {table} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join([f'{v!r}' for v in data_to_insert.values()])});"
                    
                    return {
                        'agent_text': f"✅ ¡Inserción realizada con éxito en **{table}**!",
                        'sql_statement': sql_display,
                        'type': 'query_success',
                        'conversation_state': {} # Limpiar estado
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

    # --- D) LÓGICA DE SELECT (Simple) ---
    elif intent == "SELECT" and table:
        try:
            # Lógica simple: 'listar empleados'
            if table == 'employees':
                results = db_session.query(Employee).limit(10).all()
                data_list = [emp.to_dict() for emp in results]
                
                return {
                    'agent_text': f"Mostrando los primeros {len(data_list)} registros de **{table}**:",
                    'sql_statement': f"SELECT * FROM {table} LIMIT 10;",
                    'type': 'query_result',
                    'data': data_list,
                    'conversation_state': {}
                }
            else:
                 return {'agent_text': f"La lógica SELECT para la tabla {table} aún no está implementada.", 'type': 'status', 'conversation_state': {}}
        
        except Exception as e:
             return {'agent_text': f"Error al consultar la BD: {e}", 'type': 'error', 'conversation_state': {}}

    # --- E) MANEJO DE ERRORES/UNKNOWN ---
    if intent == "UNKNOWN" or not table:
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