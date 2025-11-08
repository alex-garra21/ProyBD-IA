# utils.py
from sqlalchemy import inspect 
# Importamos las constantes de configuración
from config import TRANSLATION_MAP, FIELD_MAP

def translate_term(term):
    """Traduce un término (tabla o campo) a español, si existe."""
    return TRANSLATION_MAP.get(term.lower(), term)

def map_to_dict_dynamic(item, model_map):
    """Mapea una instancia de SQLAlchemy a un diccionario, extrayendo todas las columnas."""
    data = {}
    try:
        columns = inspect(item).mapper.columns.keys()
    except Exception:
        return item.__dict__
        
    for col in columns:
        if col.startswith('_'):
            continue
        value = getattr(item, col)
        
        if value is not None:
             if hasattr(value, 'as_integer_ratio'): 
                 data[col.upper()] = float(value)
             else:
                 data[col.upper()] = str(value)
        else:
             data[col.upper()] = None
    
    if 'FIRST_NAME' in data and 'LAST_NAME' in data:
         data['NOMBRE'] = f"{data.pop('FIRST_NAME')} {data.pop('LAST_NAME')}"
    data.pop('LAST_NAME', None)
    
    return data

def get_db_column_name(spanish_term):
    """Busca el nombre de la columna DB usando el FIELD_MAP."""
    return FIELD_MAP.get(spanish_term.lower())

def requires_auto_id(table_name):
    """Verifica si la tabla usa una clave primaria numérica que debe ser autogenerada."""
    auto_id_tables = ['employees', 'departments', 'locations', 'regions']
    return table_name in auto_id_tables