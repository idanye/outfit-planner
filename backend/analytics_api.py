from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
MEASUREMENT_ID = os.getenv('MEASUREMENT_ID')
API_SECRET = os.getenv('API_SECRET')
