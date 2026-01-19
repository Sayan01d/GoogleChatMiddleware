from flask import Flask, request, jsonify, Response
import requests
import os

app = Flask(__name__)

SALESFORCE_WEBHOOK_URL = os.getenv('SALESFORCE_WEBHOOK_URL')

@app.route('/')
def home():
    return 'Google Chat Webhook Middleware is running!'

@app.route('/webhook', methods=['POST'])
def google_chat_webhook():
    try:
        payload = request.get_json()
        print(f"Headers:{request.headers}")
        print(f"Received from Google Chat: {payload}")
        
        chat_data = payload.get('chat', {})
        message_payload = chat_data.get('messagePayload', {})
        
        if message_payload:
            message = message_payload.get('message', {})
            space = message_payload.get('space', {})
            
            formatted_text = message.get('formattedText', '')
            argument_text = message.get('argumentText', '')
            space_name = space.get('name', '')
            space_display_name = space.get('displayName', '')
            
            sender = message.get('sender', {})
            sender_name = sender.get('displayName', '')
            sender_email = sender.get('email', '')
            
            salesforce_payload = {
                'type': 'MESSAGE',
                'message': {
                    'text': formatted_text,
                    'argumentText': argument_text,
                    'sender': {
                        'displayName': sender_name,
                        'email': sender_email
                    }
                },
                'space': {
                    'name': space_name,
                    'displayName': space_display_name
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                SALESFORCE_WEBHOOK_URL,
                json=salesforce_payload,
                headers=headers
            )
            
            print(f"Salesforce response: {response.status_code} - {response.text}")
            
            # Return empty JSON to Google Chat (Salesforce sends reply via API)
            if response.status_code == 200:
                return Response('{}', status=200, mimetype='application/json')
            else:
                return Response('{}', status=200, mimetype='application/json')
        
        else:
            return Response('{}', status=200, mimetype='application/json')
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return Response('{}', status=200, mimetype='application/json')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)