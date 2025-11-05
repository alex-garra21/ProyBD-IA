# api.py

from flask import Flask, request, jsonify
from flask_cors import CORS 
from db_agent import process_query # <--- ¡Importamos la función del agente!

app = Flask(__name__)
CORS(app) 

# ... (Configuración de la BD iría aquí) ...

@app.route('/ask-agent', methods=['POST'])
def ask_agent():
    # 1. Obtener la pregunta del usuario
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({"agent_text": "Por favor, ingresa una consulta.", "type": "error"}), 400
        
    # 2. Llamar a la Lógica del Agente de IA
    # El agente procesa la consulta y devuelve el diccionario de respuesta
    agent_response = process_query(user_query) 
    
    # 3. Devolver la respuesta en formato JSON
    return jsonify(agent_response)

if __name__ == '__main__':
    app.run(debug=True)