import os
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import requests
import importlib  # To dynamically load command modules

app = Flask(__name__)
CORS(app)  # Allow all origins
load_dotenv()

# Set up the generative model configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
)

system_instruction = """
*System Name:* Your Name is KORA and you are a AI Assistance
*Creator:* Developed by SMAN AI Team, a subsidiary of SMAN AI, owned by KOLAWOLE SULEIMAN.
*Model/Version:* Currently operating on SMAN V2.0
*Release Date:* Officially launched on January 23, 2024
*Last Update:* Latest update implemented on September 14, 2024
*Purpose:* Designed utilizing advanced programming techniques to provide educational support and companionship.
*Operational Guidelines:*
1. Identity Disclosure: Refrain from disclosing system identity unless explicitly asked.
2. Interaction Protocol: Maintain an interactive, friendly, and humorous demeanor.
3. Sensitive Topics: Avoid assisting with sensitive or harmful inquiries, including but not limited to violence, hate speech, or illegal activities.
4. Policy Compliance: Adhere to SMAN AI Terms and Policy, as established by KOLAWOLE SULEIMAN.
*Response Protocol for Sensitive Topics:*
"When asked about sensitive or potentially harmful topics, you are programmed to prioritize safety and responsibility. As per SMAN AI's Terms and Policy, you should not provide information or assistance that promotes or facilitates harmful or illegal activities. Your purpose is to provide helpful and informative responses while ensuring a safe and respectful interaction environments.Operational Guidelines:Information Accuracy: KORA AI strives provide accurate response.
"""

PREFIX = os.getenv("COMMAND_PREFIX")  # Prefix for commands
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  # Token for verification

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # Verification endpoint
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Invalid verification token", 403

    # Handling messages
    elif request.method == 'POST':
        data = request.get_json()
        for entry in data.get("entry", []):
            for message_event in entry.get("messaging", []):
                user_id = message_event["sender"]["id"]
                if "message" in message_event:
                    handle_message(user_id, message_event["message"].get("text", ""))
        return "EVENT_RECEIVED", 200

def handle_message(user_id, message_text):
    # Check if the message starts with the prefix
    if message_text.startswith(PREFIX):
        command = message_text[len(PREFIX):].strip()
        response_text = execute_command(command)
    else:
        response_text = generate_response(message_text)
    
    send_message(user_id, response_text)

def execute_command(command):
    try:
        # Load the appropriate command module from the CMD folder
        command_module = importlib.import_module(f'CMD.{command}')
        return command_module.run()  # Assumes each command file has a 'run' function
    except ModuleNotFoundError:
        return "Command not found. Use /help to see available commands."

def generate_response(query):
    chat = model.start_chat(history=[])
    response = chat.send_message(f"{system_instruction}\n\nHuman: {query}")
    
    # Webhook notification
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        webhook_data = {"query": query, "response": response.text}
        try:
            requests.post(webhook_url, json=webhook_data)
        except requests.RequestException as e:
            print(f"Webhook call failed: {e}")
    
    return response.text

def send_message(recipient_id, text):
    fb_url = f"https://graph.facebook.com/v15.0/me/messages?access_token={os.getenv('PAGE_ACCESS_TOKEN')}"
    response = {"messaging_type": "RESPONSE", "recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(fb_url, json=response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
