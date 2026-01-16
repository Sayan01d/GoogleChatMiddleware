from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Salesforce webhook URL (set in Render environment variables)
SALESFORCE_WEBHOOK_URL = os.getenv('SALESFORCE_WEBHOOK_URL')

@app.route('/')
def home():
    return 'Google Chat Webhook Middleware is running!'

@app.route('/webhook', methods=['POST'])
def google_chat_webhook():
    try:
        payload = request.get_json()
        print(f"Received from Google Chat: {payload}")
        
        # Extract chat data from Google's payload structure
        chat_data = payload.get('chat', {})
        message_payload = chat_data.get('messagePayload', {})
        
        # Check if this is a message event
        if message_payload:
            # Extract message details
            message = message_payload.get('message', {})
            space = message_payload.get('space', {})
            
            # Get the text and space info
            formatted_text = message.get('formattedText', '')
            argument_text = message.get('argumentText', '')  # Text without @mention
            space_name = space.get('name', '')  # Format: "spaces/AAQAOD4O8h4"
            space_display_name = space.get('displayName', '')
            
            # Get sender info
            sender = message.get('sender', {})
            sender_name = sender.get('displayName', '')
            sender_email = sender.get('email', '')
            
            print(f"Message: {formatted_text}")
            print(f"Space: {space_name}")
            print(f"Sender: {sender_name} ({sender_email})")
            
            # Build payload for Salesforce in the format it expects
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
            
            print(f"Sending to Salesforce: {salesforce_payload}")
            
            # Forward to Salesforce
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                SALESFORCE_WEBHOOK_URL,
                json=salesforce_payload,
                headers=headers
            )
            
            print(f"Salesforce response: {response.status_code} - {response.text}")
            
            return jsonify({'text': 'Message received and forwarded to Salesforce!'}), 200
        
        else:
            # Handle other events (ADDED_TO_SPACE, REMOVED_FROM_SPACE, etc.)
            return jsonify({'text': 'Event received.'}), 200
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'text': f'Error: {str(e)}'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)