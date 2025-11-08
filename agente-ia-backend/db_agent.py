# db_agent.py
from sqlalchemy.orm import Session
from sqlalchemy import inspect, func # func para max_id en INSERT

# Importar modelos, utilidades y lógica de parsing
from models import Employee, Department, Job, Region, Country, Location 
from config import DB_SCHEMA 
from utils import translate_term, map_to_dict_dynamic, requires_auto_id
from parsing import (
    classify_intent, 
    extract_entities, 
    simple_data_extractor, 
    extract_conditions, 
    extract_update_params
)
# 1. Importar Modelos (Ahora desde models.py, que es la fuente correcta)
try:
    from models import Employee, Department, Job, Region, Country, Location 
except ImportError as e:
    # Si la importación falla, imprime el error de depuración real.
    print(f"Error de Importación Crítico: {e}")
    # Nota: Si models.py no está en el mismo directorio, la importación fallará.
    # Para fines de este proyecto, asumiremos que models.py está en el mismo nivel o es accesible.
    exit()

# 2. Importar Constantes y Utilidades (Ahora desde config.py y utils.py)
from config import DB_SCHEMA 
from parsing import classify_intent, extract_entities, simple_data_extractor, extract_conditions, extract_update_params
from utils import translate_term, map_to_dict_dynamic, requires_auto_id

# 3. Definir el Mapa de Modelos
MODEL_MAP = {
    'employees': Employee, 
    'departments': Department, 
    'jobs': Job,
    'regions': Region,
    'countries': Country,
    'locations': Location
}
# Definimos el MODEL_MAP aquí para que esté disponible globalmente en este módulo

# -----------------------------------------------------------------
# --- 5. Función Principal del Agente (CON db_session) ---
# -----------------------------------------------------------------
def process_query(user_query, db_session: Session = None, conversation_state={}):
    
    if not db_session:
         return {'agent_text': f"Error crítico: No hay conexión a la base de datos.", 'type': 'error', 'conversation_state': {}}

    user_query = user_query.strip()
    
    # Inicialización de variables para el flujo
    intent = conversation_state.get('intent', 'UNKNOWN')
    table = conversation_state.get('table')
    
    # --- A) MANEJO DE ESTADO DE CONVERSACIÓN (Diálogo Activo) ---
    if conversation_state and user_query:
        if intent in ["UPDATE", "DELETE"] and table:
            pass 
        
        if intent == "INSERT" or (intent in ["UPDATE", "DELETE"] and conversation_state.get('last_asked_field')):
            extracted_data = simple_data_extractor(user_query)
            if 'value' in extracted_data and conversation_state.get('last_asked_field'):
                last_asked = conversation_state['last_asked_field']
                conversation_state['data_collected'][last_asked] = extracted_data['value']
                if last_asked in conversation_state['missing_fields']:
                    conversation_state['missing_fields'].remove(last_asked)
        
    # --- B) INICIO DE NUEVA CONVERSACIÓN (o primer paso de una acción) ---
    else:
        intent = classify_intent(user_query)
        entities = extract_entities(user_query)
        table = entities.get('table')
        
        initial_data = simple_data_extractor(user_query)
        if intent == "UNKNOWN":
             initial_data.pop('value', None)
        
        if not table and intent in ["UPDATE", "DELETE"]:
            table = 'employees'
            
        conversation_state = {
            'intent': intent,
            'table': table,
            'data_collected': initial_data,
            'missing_fields': [],
            'last_asked_field': None
        }

    # =========================================================================
    # --- LÓGICA DE EJECUCIÓN/DIÁLOGO ---
    # =========================================================================

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
            translated_field = translate_term(next_field)
            translated_table = translate_term(table)
            prompt_text = "Por favor, dime el valor para el campo: **{}**.".format(translated_field)
            if next_field == 'hire_date':
                prompt_text = "Por favor, dime la **fecha de contratación** (formato YYYY-MM-DD)."
            agent_text = (f"Entendí la inserción en la tabla **{translated_table}**. {prompt_text}")
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
                    if requires_auto_id(table):
                         pk_column_name = schema['fields'][0] 
                         PkColumn = getattr(Model, pk_column_name)
                         max_id_result = db_session.query(PkColumn).order_by(PkColumn.desc()).first()
                         if table == 'regions': base_id = 1
                         elif table == 'locations': base_id = 1001
                         elif table == 'departments': base_id = 100 
                         else: base_id = 300
                         current_max_id = max_id_result[0] if max_id_result else base_id
                         data_to_insert[pk_column_name] = current_max_id + 1
                    
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
                last_field = conversation_state.get('last_asked_field', 'dato')
                error_message = (f"❌ Error de validación: El último valor ingresado (para {translate_term(last_field)}) no es válido o viola una restricción. Intenta de nuevo.")
                return {
                    'agent_text': error_message,
                    'sql_statement': None,
                    'type': 'dialog_needed',
                    'conversation_state': conversation_state 
                }

    # --- D) LÓGICA DE SELECT (Avanzada con Condiciones) ---
    elif intent == "SELECT" and table:
        try:
            Model = MODEL_MAP.get(table)
            if not Model:
                return {'agent_text': f"No se encontró el modelo para {table}.", 'type': 'error', 'conversation_state': {}}

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

                if op == '>': query = query.filter(column > value)
                elif op == '<': query = query.filter(column < value)
                elif op == '==': query = query.filter(column == value)
                elif op == '!=': query = query.filter(column != value)
                sql_display_condition = f" WHERE {field} {op} {value}"
            
            results = query.limit(10).all() 
            data_list = [map_to_dict_dynamic(item, MODEL_MAP) for item in results]
            
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
    elif intent == "UPDATE" and table:
        try:
            Model = MODEL_MAP.get(table)
            if not Model:
                raise Exception(f"Modelo no encontrado para la tabla {table}.")

            # 1. Intentar extraer el SET y WHERE de una sola frase (usa parsing.py)
            update_params = extract_update_params(user_query)

            if not update_params:
                 return {'agent_text': "Para actualizar, necesito la condición **SET** (ej. 'salario a 25000') Y la condición **WHERE** (ej. 'donde ID es 100').", 'type': 'dialog_needed', 'conversation_state': {}}
            
            # --- EXTRACCIÓN Y PREPARACIÓN ---
            set_cond = update_params['set_cond']
            where_cond = update_params['where_cond']
            
            # 2. Conversión de Tipos (Manejo de IDs, Salarios, etc.)
            
            # Para el valor SET (el nuevo valor a asignar)
            set_value_raw = set_cond['value']
            try:
                # Intentamos convertir a numérico (útil para salary, commission_pct)
                set_value_typed = float(set_value_raw)
            except ValueError:
                # Si no es numérico, lo dejamos como string (nombre, apellido, email)
                set_value_typed = set_value_raw

            # Para la condición WHERE (clave de búsqueda)
            where_value_raw = where_cond['value']
            try:
                # Intentamos convertir a entero (útil para todos los IDs)
                where_value_typed = int(where_value_raw) 
            except ValueError:
                # Si no es entero, lo dejamos como string (apellido, nombre del depto, etc.)
                where_value_typed = where_value_raw

            
            # 3. Obtener Columnas y Preparar Data
            where_column = getattr(Model, where_cond['field'], None)
            set_column = getattr(Model, set_cond['field'], None)

            if where_column is None or set_column is None:
                 raise Exception(f"Uno de los campos (SET: {set_cond['field']} o WHERE: {where_cond['field']}) no es válido.")
                
            update_data = {set_column: set_value_typed}
            
            # 4. Ejecución del UPDATE con SQLAlchemy
            # Filtramos por la condición WHERE y ejecutamos el UPDATE con los datos SET
            num_rows_updated = db_session.query(Model).filter(
                where_column == where_value_typed 
            ).update(update_data, synchronize_session=False) 

            db_session.commit()
            
            # 5. Generación del SQL para visualización
            # Usamos los valores sin tipado para que se vean como el usuario los escribió
            sql_statement = f"UPDATE {table} SET {set_cond['field']} = '{set_value_raw}' WHERE {where_cond['field']} = '{where_value_raw}';"
            
            # 6. Retorno de Respuesta
            if num_rows_updated > 0:
                return {'agent_text': f"✅ Actualización exitosa! Se modificaron **{num_rows_updated}** registros.", 'sql_statement': sql_statement, 'type': 'query_success', 'conversation_state': {}}
            else:
                return {'agent_text': f"⚠️ No se encontró ningún registro para actualizar con la condición {where_cond['field']} = {where_value_raw}.", 'sql_statement': sql_statement, 'type': 'status', 'conversation_state': {}}
                
        except Exception as e:
            db_session.rollback()
            return {'agent_text': f"❌ Error al intentar actualizar los datos: {str(e)}", 'sql_statement': "N/A", 'type': 'error', 'conversation_state': {}}
        
    # --- F) LÓGICA DELETE (Eliminar Registros) ---
    elif intent == "DELETE" and table:
        try:
            Model = MODEL_MAP.get(table)
            if not Model:
                raise Exception(f"Modelo no encontrado para la tabla {table}.")

            # 1. Extracción de la Condición WHERE (quién o qué eliminar)
            # Reutilizamos extract_conditions para el filtro
            where_conditions = extract_conditions(user_query, table)

            if not where_conditions:
                 return {'agent_text': "Para eliminar, necesito la condición **WHERE** (ej. 'donde ID es 206').", 'type': 'dialog_needed', 'conversation_state': {}}
                 
            # --- PREPARACIÓN ---
            where_cond = where_conditions[0]
            where_value_raw = where_cond['value']

            # Conversión de Tipos (Aseguramos el tipo correcto, ej. entero para IDs)
            try:
                # Intentamos convertir a entero para IDs
                where_value_typed = int(where_value_raw) 
            except ValueError:
                # Si no es entero, lo dejamos como string
                where_value_typed = where_value_raw
            
            where_column = getattr(Model, where_cond['field'], None)

            if where_column is None:
                 raise Exception(f"El campo WHERE '{where_cond['field']}' no es válido.")
            
            # 2. Ejecución del DELETE con SQLAlchemy
            num_rows_deleted = db_session.query(Model).filter(
                where_column == where_value_typed 
            ).delete(synchronize_session=False) # Usamos synchronize_session=False para una operación rápida
            
            db_session.commit()
            
            # 3. Generación del SQL para visualización
            sql_statement = f"DELETE FROM {table} WHERE {where_cond['field']} = '{where_value_raw}';"
            
            # 4. Retorno de Respuesta
            if num_rows_deleted > 0:
                return {'agent_text': f"✅ Eliminación exitosa! Se borraron **{num_rows_deleted}** registros.", 'sql_statement': sql_statement, 'type': 'query_success', 'conversation_state': {}}
            else:
                return {'agent_text': f"⚠️ No se encontró ningún registro para eliminar con la condición {where_cond['field']} = {where_value_raw}.", 'sql_statement': sql_statement, 'type': 'status', 'conversation_state': {}}
            
        except Exception as e:
            db_session.rollback()
            return {'agent_text': f"❌ Error al intentar eliminar datos: {str(e)}", 'sql_statement': "N/A", 'type': 'error', 'conversation_state': {}}
        
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