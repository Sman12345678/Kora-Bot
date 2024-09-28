from flask import Flask, request
import os
import importlib
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# Verify the Facebook token (used during webhook setup)
@app.route('/webhook', methods=['GET'])
def verify():
    token = os.getenv('VERIFY_TOKEN')
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == token:
        return request.args.get('hub.challenge'), 200
    return 'Verification token mismatch', 403

# Handle messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # Iterate over the messages
    for entry in data['entry']:
        for message_event in entry['messaging']:
            if 'message' in message_event and 'text' in message_event['message']:
                sender_id = message_event['sender']['id']
                message_text = message_event['message']['text'].lower()

                # Dynamically attempt to import a command module from CMD based on the message text
                try:
                    command_module = importlib.import_module(f'CMD.{message_text}_cmd')
                    response = command_module.handle_command()
                except ModuleNotFoundError:
                    response = "Command not recognized."

                # Send response back to Facebook
                send_message(sender_id, response)

    return 'EVENT_RECEIVED', 200

def send_message(recipient_id, message_text):
    """Send a message to the user"""
    access_token = os.getenv('PAGE_ACCESS_TOKEN')
    url = f'https://graph.facebook.com/v12.0/me/messages?access_token={access_token}'
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0',port=5000)
