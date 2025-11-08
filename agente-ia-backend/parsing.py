# parsing.py
import re
# Importamos las constantes de configuración
from config import FIELD_MAP, OPERATOR_MAP 
# Importamos funciones auxiliares
from utils import get_db_column_name

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

# --- 2. Extracción de Entidades (Tablas) ---
def extract_entities(text):
    """Extrae la tabla principal mencionada en la consulta."""
    entities = {}
    text_lower = text.lower()
    if "empleado" in text_lower or "employees" in text_lower:
        entities['table'] = 'employees'
    elif "departamento" in text_lower or "departments" in text_lower:
        entities['table'] = 'departments'
    elif "puesto" in text_lower or "jobs" in text_lower:
        entities['table'] = 'jobs'
    elif "region" in text_lower or "regions" in text_lower:
        entities['table'] = 'regions'
    elif "pais" in text_lower or "countries" in text_lower:
        entities['table'] = 'countries'
    elif "ubicacion" in text_lower or "locations" in text_lower:
        entities['table'] = 'locations'
    return entities

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

def extract_conditions(text, table_name, for_set=False):
    text_lower = text.lower()
    conditions = []
    
    if for_set:
        pattern = rf'({"|".join(FIELD_MAP.keys())})\s+(a|por|con)\s+([a-zA-Z0-9.@\s]+)' # Ajustado para capturar valores con espacios
        match = re.search(pattern, text_lower)
        if match:
            es_field = match.group(1) 
            value_str = match.group(3).replace('q', '').replace('$', '').replace(',', '').strip()
            try:
                value = float(value_str) if '.' in value_str or any(c.isdigit() for c in value_str) else value_str
            except ValueError:
                value = value_str
            conditions.append({
                'field': FIELD_MAP.get(es_field, es_field),
                'op': '=', # Siempre '=' para SET
                'value': value
            })
            return conditions
    else:
        for es_op, sql_op in OPERATOR_MAP.items():
            # *** CÓDIGO CORREGIDO *** # El bloque 'else' estaba incompleto en tu archivo original.
            pattern = rf'\b({"|".join(FIELD_MAP.keys())})\b.*?{re.escape(es_op)}.*?\s+([a-zA-Z0-9.,]+)'
            match = re.search(pattern, text_lower)
            
            if match:
                es_field = match.group(1) 
                value_str = match.group(2).replace('q', '').replace('$', '').replace(',', '').strip()
                try:
                    value = float(value_str) if '.' in value_str or any(c.isdigit() for c in value_str) else value_str
                except ValueError:
                    value = value_str
                    
                conditions.append({
                    'field': FIELD_MAP.get(es_field, es_field),
                    'op': sql_op,
                    'value': value
                })
                return conditions # Devolvemos la primera condición encontrada
    return conditions # Devolvemos lista vacía si no hay match

def extract_update_params(user_query):
    """
    Extrae las condiciones SET y WHERE de una consulta de actualización en lenguaje natural.
    """
    query_lower = user_query.lower()
    
    set_pattern = r"((?:\w+\s?)+\s?)\s?(?:a|por|=|es)\s?(['\"]?[\w\s\.-]+['\"]?)"
    where_pattern = r"(?:donde|con)\s+((?:\w+\s?)+\s?)\s?(?:es|=|a|sea)\s?(['\"]?[\w\s\.-]+['\"]?)"
    
    set_match = re.search(set_pattern, query_lower)
    where_match = re.search(where_pattern, query_lower)
    
    if not set_match or not where_match:
        # Si no encontramos el patrón completo, falta información
        return None

    set_field_es = set_match.group(1).strip()
    set_value_str = set_match.group(2).strip().replace('"', '').replace("'", '')
    set_column = get_db_column_name(set_field_es)
    
    if not set_column:
        print(f"DEBUG: Campo SET '{set_field_es}' no encontrado en FIELD_MAP.")
        return None
        
    set_cond = {
        'field': set_column,
        'value': set_value_str 
    }

    where_field_es = where_match.group(1).strip()
    where_value_str = where_match.group(2).strip().replace('"', '').replace("'", '')
    where_column = get_db_column_name(where_field_es)
    
    if not where_column:
        print(f"DEBUG: Campo WHERE '{where_field_es}' no encontrado en FIELD_MAP.")
        return None

    where_cond = {
        'field': where_column,
        'op': '==', 
        'value': where_value_str 
    }

    return {
        'set_cond': set_cond,
        'where_cond': where_cond
    }