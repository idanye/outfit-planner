from dotenv import load_dotenv
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GA_ENDPOINT = "https://www.google-analytics.com/mp/collect"
MEASUREMENT_ID = os.getenv('MEASUREMENT_ID')
API_SECRET = os.getenv('API_SECRET')

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Endpoint to receive data from the frontend and send it to Google Analytics
@app.post("/send-analytics")
async def send_analytics(request: Request):
    print("Received analytics call in backend...")
    data = await request.json()
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
        print("Event sent to Google Analytics")
        return JSONResponse(content={'status': 'success', 'message': 'Event sent to Google Analytics'}, status_code=200)
    else:
        print(f"Error sending event to Google Analytics: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.text)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000, reload=True, log_level="debug")