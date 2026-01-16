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
    """
    Receives webhook from Google Chat and forwards to Salesforce
    """
    try:
        # Get the payload from Google Chat
        payload = request.get_json()
        print(f"Received from Google Chat: {payload}")
        
        # Get event type
        event_type = payload.get('type', '')
        
        # Only process MESSAGE events
        if event_type == 'MESSAGE':
            # Forward to Salesforce (without Google's auth header)
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Forward the payload to Salesforce
            response = requests.post(
                SALESFORCE_WEBHOOK_URL,
                json=payload,
                headers=headers
            )
            
            print(f"Salesforce response: {response.status_code} - {response.text}")
            
            # Return success to Google Chat
            return jsonify({'text': 'Message received and forwarded to Salesforce!'}), 200
        
        elif event_type == 'ADDED_TO_SPACE':
            return jsonify({'text': 'Thanks for adding me! I am connected to Salesforce.'}), 200
        
        elif event_type == 'REMOVED_FROM_SPACE':
            return jsonify({}), 200
        
        else:
            return jsonify({}), 200
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'text': f'Error: {str(e)}'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
