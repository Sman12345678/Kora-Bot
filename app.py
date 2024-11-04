import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import fbchat
import importlib
import google.generativeai as genai
import requests

app = Flask(__name__)
CORS(app)
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
PREFIX = os.getenv("PREFIX")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Set up generative model
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
*System Name:* KORA AI Assistance ...
"""

# Verify Token for Facebook webhook setup
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

# Main bot response endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry.get("messaging", []):
                if "message" in event:
                    sender_id = event["sender"]["id"]
                    message_text = event["message"]["text"]

                    # Check if message starts with the prefix
                    if message_text.startswith(PREFIX):
                        command_name = message_text[len(PREFIX):].split()[0]
                        response = execute_command(command_name)  # Run CMD command if exists
                    else:
                        # Generate AI response if no command
                        response = generate_ai_response(message_text)

                    # Send response to user
                    send_message(sender_id, response)
    return "EVENT_RECEIVED", 200

# Execute command from CMD folder
def execute_command(command_name):
    try:
        cmd_module = importlib.import_module(f"CMD.{command_name}")
        return cmd_module.execute()
    except ImportError:
        return "Command not found."

# Generate AI response
def generate_ai_response(query):
    chat = model.start_chat(history=[])
    response = chat.send_message(f"{system_instruction}\n\nHuman: {query}")
    return response.text

# Send message back to Facebook
def send_message(recipient_id, message_text):
    params = {
        "access_token": os.getenv("PAGE_ACCESS_TOKEN")  # Use page token here
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post("https://graph.facebook.com/v11.0/me/messages",
                             params=params, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Unable to send message: {response.text}")

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=3000)
