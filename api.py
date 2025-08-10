import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from app import initialize_agents_and_services, run_agentic_pipeline

app = Flask(__name__)
CORS(app)

agents = initialize_agents_and_services()
chat_histories = {}

@app.route('/start', methods=['POST'])
def start():
    session_id = str(uuid.uuid4())
    chat_histories[session_id] = []
    return jsonify({"session_id": session_id})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    query = data.get('query')
    session_id = data.get('session_id')

    if not query or not session_id:
        return jsonify({"error": "Query or session_id not provided"}), 400

    if session_id not in chat_histories:
        return jsonify({"error": "Invalid session_id"}), 400

    conversation_history = chat_histories[session_id]
    conversation_history.append({"role": "user", "content": query})

    # The agentic pipeline expects a single query string.
    # We'll pass the full conversation history for context.
    full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])

    final_response = ""
    for response_part in run_agentic_pipeline(full_query, agents):
        final_response = response_part
    
    conversation_history.append({"role": "assistant", "content": final_response})
    chat_histories[session_id] = conversation_history

    return jsonify({"response": final_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
