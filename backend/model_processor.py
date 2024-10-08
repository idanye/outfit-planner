from gradio_client import Client, file
from datetime import datetime
import time
import shutil
import os
from dotenv import load_dotenv
from classification import clothes_classifier

# Load environment variables from .env file
load_dotenv()


class ModelProcessor:
    def __init__(self, model_image_path):
        self.model_image_path = model_image_path

    @staticmethod
    def process_image(model_image_path, garment_image_path, category="Upper-body", images=1,
                      steps=25, guidance_scale=2, seed=-1):
        try:
            print(f"process_image function started")
            # Convert to absolute paths
            model_image_path = os.path.abspath(model_image_path)
            garment_image_path = os.path.abspath(garment_image_path)

            print(f"Absolute model image path: {model_image_path}")
            print(f"Absolute garment image path: {garment_image_path}")

            # Ensure files exist
            if not os.path.exists(model_image_path):
                raise FileNotFoundError(f"Model image path '{model_image_path}' does not exist.")
            if not os.path.exists(garment_image_path):
                raise FileNotFoundError(f"Garment image path '{garment_image_path}' does not exist.")

            # Initialize the Gradio client
            client = Client("levihsu/OOTDiffusion", hf_token="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")
            # Make the API call
            result = client.predict(
                file(model_image_path),  # Use gradio_client.file() to specify the file path
                file(garment_image_path),  # Use gradio_client.file() to specify the file path
                category,  # Literal['Upper-body', 'Lower-body', 'Dress'] in 'Garment category (important option!!!)'
                images,  # float (numeric value between 1 and 4) in 'Images' Slider component
                steps,  # float (numeric value between 20 and 40) in 'Steps' Slider component
                guidance_scale,  # float (numeric value between 1.0 and 5.0) in 'Guidance scale' Slider component
                seed,  # float (numeric value between -1 and 2147483647) in 'Seed' Slider component
                api_name="/process_dc"
            )

            print(f"process_image function: Result: {result}")
            # Open the image
            temp_image_path = result[0]['image']

            # Define the result directory and ensure it exists
            script_dir = os.path.dirname(os.path.abspath(__file__))
            time.sleep(0.5)
            result_dir = os.path.join(script_dir, "resultImages")
            os.makedirs(result_dir, exist_ok=True)

            print(f"Result directory: {result_dir}")  # debug

            # Get the extension of the model image
            model_image_extension = os.path.splitext(model_image_path)[1]
            # Extract the image path from the response
            image_path = result[0]['image']

            # Ensure the file is closed before moving it
            with open(image_path, 'rb') as f:
                pass

            # Add a small delay to ensure the file handle is released
            time.sleep(0.5)

            # Generate a unique name using a timestamp and a UUID
            timestamp = datetime.now().strftime("result_image-%Y_%m_%d-%H_%M")
            unique_name = f"{timestamp}{model_image_extension}"
            print(f"Unique name is: {unique_name}")

            # Define the new image path with the unique name
            new_image_path = os.path.join(result_dir, unique_name)
            print(f"New unique image path: {new_image_path}")

            # Move the image to the result directory
            shutil.move(temp_image_path, new_image_path)

            # Return the new image path
            return new_image_path
        except Exception as e:
            print(e)
            return 'None'
