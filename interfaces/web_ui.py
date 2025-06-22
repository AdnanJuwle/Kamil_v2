import threading
import logging
import os
from flask import Flask, render_template, request, jsonify, session
from core.agent import SAFETY_KEYWORDS
import uuid

# Get the current directory of this file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the kamil directory
base_dir = os.path.dirname(current_dir)
# Set template folder path
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'super_secret_key'  # For session management
logger = logging.getLogger("WebUI")

# Session storage for chat histories
chat_sessions = {}

@app.route('/')
def index():
    # Create a new session ID
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    chat_sessions[session_id] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    session_id = session.get('session_id')
    if not session_id or session_id not in chat_sessions:
        return jsonify({'response': "Session expired. Please refresh the page."})
    
    user_input = request.json.get('message')
    logger.info(f"Received message: {user_input}")
    history = chat_sessions[session_id]
    
    try:
        # Safety check
        if any(keyword in user_input.lower() for keyword in SAFETY_KEYWORDS):
            return jsonify({
                'response': "I've detected you might need help. Please contact a mental health professional immediately.",
                'crisis': True,
                'resources': [
                    "National Suicide Prevention Lifeline: 1-800-273-8255",
                    "Crisis Text Line: Text HOME to 741741",
                    "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
                ]
            })
        
        # Get agent from application context
        agent = app.config['AGENT']
        response = agent.process_request(user_input, history=history)
        
        # Store interaction
        chat_sessions[session_id].append((user_input, response))
        if len(chat_sessions[session_id]) > 20:  # Limit history
            chat_sessions[session_id] = chat_sessions[session_id][-10:]
        
        return jsonify({'response': response})
    except Exception as e:
        logger.exception("Error processing request")
        return jsonify({'response': f"Error: {str(e)}"}), 500

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

def start_web_server(agent):
    app.config['AGENT'] = agent
    thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    thread.start()
    logger.info("Web server started on http://localhost:5000")
    return thread
