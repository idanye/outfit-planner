from gradio_client import Client, file
import requests
from PIL import Image
from io import BytesIO
import os
from image_manager import ImageManager


class ModelProcessor:
    def __init__(self, model_image_path):
        self.model_image_path = model_image_path

    @staticmethod
    def process_image(model_image_path, garment_image_path, category="Lower-body", images=1,
                      steps=25, guidance_scale=2, seed=-1):
        # Initialize the Gradio client
        client = Client("levihsu/OOTDiffusion")

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

        print(result)
        # Open the image
        image_path = result[0]['image']
        image = Image.open(image_path)
        image.show()

        # # extracted_path = result[0]['image'].replace("\\\\", "\\")
        # ImageManager.move_image(original_img_path, i)


if __name__ == '__main__':
    model_image_path = ".\\modelsImages\\model4.png"
    garment_image_path = ".\\garmentsImages\\garment7.jpg"
    ModelProcessor.process_image(model_image_path, garment_image_path)