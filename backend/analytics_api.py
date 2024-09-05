from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify  # Using Flask for simplicity
import requests

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GA_ENDPOINT = "https://www.google-analytics.com/mp/collect"
MEASUREMENT_ID = os.getenv('MEASUREMENT_ID')
API_SECRET = os.getenv('API_SECRET')

app = Flask(__name__)

# Endpoint to receive data from the frontend and send it to Google Analytics
@app.route('/send-analytics', methods=['POST'])
def send_analytics():
    data = request.json
    client_id = data['client_id']
    event_name = data['event_name']
    event_params = data['event_params']

    url = f'https://www.google-analytics.com/mp/collect?measurement_id={MEASUREMENT_ID}&api_secret={API_SECRET}'
    payload = {
        'client_id': client_id,
        'events': [{
            'name': event_name,
            'params': event_params
        }]
    }
    response = requests.post(url, json=payload)

    if response.status_code == 204:
        return jsonify({'status': 'success', 'message': 'Event sent to Google Analytics'}), 200
    else:
        return jsonify({'status': 'error', 'message': response.text}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)  # Replace `debug=True` with `debug=False` in production






# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# # Access the environment variables
# MEASUREMENT_ID = os.getenv('MEASUREMENT_ID')
# API_SECRET = os.getenv('API_SECRET')

# # Function to send analytics data
# def send_analytics(client_id, event_name, event_params):
#     import requests

#     url = f'https://www.google-analytics.com/mp/collect?measurement_id={MEASUREMENT_ID}&api_secret={API_SECRET}'
#     payload = {
#         'client_id': client_id,
#         'events': [{
#             'name': event_name,
#             'params': event_params
#         }]
#     }
#     response = requests.post(url, json=payload)
#     print(f'Status Code: {response.status_code}, Response: {response.text}')