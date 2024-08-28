from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
MEASUREMENT_ID = os.getenv('MEASUREMENT_ID')
API_SECRET = os.getenv('API_SECRET')

# Function to send analytics data
def send_analytics(client_id, event_name, event_params):
    import requests

    url = f'https://www.google-analytics.com/mp/collect?measurement_id={MEASUREMENT_ID}&api_secret={API_SECRET}'
    payload = {
        'client_id': client_id,
        'events': [{
            'name': event_name,
            'params': event_params
        }]
    }
    response = requests.post(url, json=payload)
    print(f'Status Code: {response.status_code}, Response: {response.text}')