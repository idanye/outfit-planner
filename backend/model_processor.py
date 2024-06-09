from gradio_client import Client, file
import requests
from PIL import Image
from io import BytesIO
import os
from image_manager import ImageManager


class ModelProcessor:
    model_image = "C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\backend\\modelsImages\\model4.png"
    garment_image = "C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\backend\\\garmentsImages\\garment7.jpg"

    @staticmethod
    def process_image(model_image_path=model_image, garment_image_path=garment_image, category="Lower-body", images=1, steps=20, guidance_scale=1, seed=-1):
        # Initialize the Gradio client
        client = Client("https://levihsu-ootdiffusion.hf.space/--replicas/iif7h/")

        for i in range(1,3):
            # Make the API call
            result = client.predict(
                file(model_image_path),  # Use gradio_client.file() to specify the file path
                file(garment_image_path),  # Use gradio_client.file() to specify the file path
                category, # Literal['Upper-body', 'Lower-body', 'Dress'] in 'Garment category (important option!!!)'
                images, # float (numeric value between 1 and 4) in 'Images' Slider component
                steps, # float (numeric value between 20 and 40) in 'Steps' Slider component
                guidance_scale, # float (numeric value between 1.0 and 5.0) in 'Guidance scale' Slider component
                seed,  # float (numeric value between -1 and 2147483647) in 'Seed' Slider component
                api_name="/process_dc"
            )

            # print(result)
            original_img_path = result[0]['image']
            # extracted_path = result[0]['image'].replace("\\\\", "\\")
            ImageManager.move_image(original_img_path, i)
