# db_agent.py

# --- 1. Clasificación de Intención ---
def classify_intent(text):
    text_lower = text.lower()
    
    select_keywords = ["listar", "dame", "mostrar", "quienes", "cuantos"]
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
    entities = {}
    text_lower = text.lower()
    
    if "cliente" in text_lower or "clientes" in text_lower:
        entities['table'] = 'cliente'
    elif "empleado" in text_lower or "empleados" in text_lower:
        entities['table'] = 'empleado'
        
    return entities

# --- 3. Función Principal del Agente ---
def process_query(user_query, conversation_state={}):
    """
    Procesa la consulta del usuario, determina la acción y devuelve la respuesta.
    La variable 'conversation_state' se usará más tarde para el diálogo.
    """
    
    intent = classify_intent(user_query)
    entities = extract_entities(user_query)
    table = entities.get('table')
    
    response = {
        'agent_text': f"Entendí la intención: **{intent}**. La tabla objetivo es: **{table or 'Desconocida'}**.",
        'sql_statement': None,
        'type': 'status', # Puede ser 'dialog_needed', 'query_result', 'error'
        'data': []
    }
    
    if intent == "INSERT" and table:
        # Lógica futura: Si falta información, pide el email.
        response['agent_text'] = f"Entendí que quieres **insertar** en la tabla **{table}**. Necesitaré más datos."
        response['type'] = 'dialog_needed'
        
    elif intent == "SELECT" and table:
        # Lógica futura: Generar el SQL para el SELECT
        response['agent_text'] = f"Procesando la consulta de la tabla **{table}**."
        response['sql_statement'] = f"SELECT * FROM {table} WHERE [CONDICIÓN INFERIDA];"
        response['type'] = 'query_result'
        # Simulación de datos:
        if table == 'empleado':
             response['data'] = [{"nombre": "Simón", "salario": 4800}, {"nombre": "Andrea", "salario": 5200}]
    
    return response