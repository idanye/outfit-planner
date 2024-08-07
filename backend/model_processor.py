from gradio_client import Client, file
import uuid
import json
from PIL import Image
import requests
import shutil
import os
from image_manager import ImageManager


class ModelProcessor:
    def __init__(self, model_image_path):
        self.model_image_path = model_image_path

    @staticmethod
    def process_image(model_image_path, garment_image_path, category="Lower-body", images=1,
                      steps=25, guidance_scale=2, seed=-1):
        # Initialize the Gradio client
        client = Client("levihsu/OOTDiffusion", hf_token="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")
                            # "idany/OOTDiffusion"
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
        temp_image_path = result[0]['image']
        image = Image.open(temp_image_path)

        # Define the result directory and ensure it exists
        script_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(script_dir, "resultImages")
        os.makedirs(result_dir, exist_ok=True)

        # Get the extension of the model image
        model_image_extension = os.path.splitext(model_image_path)[1]

        # Generate a unique name using a UUID
        unique_name = f"{uuid.uuid4()}{model_image_extension}"
       
        # Define the new image path with the unique name
        new_image_path = os.path.join(result_dir, unique_name)

        # # Define the new image path with the same extension as the model image
        # new_image_path = os.path.join(result_dir, os.path.basename(temp_image_path).replace('.webp', model_image_extension))

        # Move the image to the result directory
        shutil.move(temp_image_path, new_image_path)
    
        # Open the moved image
        image = Image.open(new_image_path)
        image.show()


    def get_image_evaluation(image_path):
        # Define the API endpoint and your API key
        api_endpoint = "https://api.openai.com/v1/chat/completions"
        api_key = "sk-proj-cQM9UT4EGqws9XBxkXydT3BlbkFJ41c9duQB6DCS1wnZfCsp"
        with open(image_path, "rb") as image_file:
            # Send the image to the API for evaluation
            response = requests.post(api_endpoint, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "image/png"  # Adjust as needed
            }, data=image_file.read())
            
            # Process the response to get the evaluation score
            # Assuming the response contains a score in a JSON field called 'score'
            evaluation = response.json().get('score', 0)
            return evaluation
        
    @staticmethod
    def find_best_image(directory):
        best_image = None
        best_score = float('-inf')

        for filename in os.listdir(directory):
            if filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                image_path = os.path.join(directory, filename)
                score = get_image_evaluation(image_path)
                print(f"Image: {filename}, Score: {score}")

                if score > best_score:
                    best_score = score
                    best_image = filename

        return best_image


        # # Define the headers
        # headers = {
        #     "Authorization": f"Bearer {api_key}",
        #     "Content-Type": f"image/png"  # f"image/{image_format}"
        # }

        # # Construct the prompt based on user input
        # prompt = (
        #     f"Please evaluate the following images: that are the output of a model that dresses a model with the input grament. You need to return the most realistic looking, fits good on the model and look like the origin grament image: {garment_img}, image"
        # )

        # # Define the data for the request
        # data = {
        #     "model": "gpt-4",  # Specify the model you want to use
        #     "messages": [
        #         {"role": "system", "content": "You are an helpful evaluator of images."},
        #         {"role": "user", "content": prompt}
        #     ]
        # }

        # # Open the image file in binary mode
        # with open("path/to/image.file", "rb") as image_file:
        #     response = requests.post(api_endpoint, headers=headers, data=image_file.read())

        # response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
            
        # if response.status_code == 200:
        #     response_data = response.json()

        #     # Extract the assistant's response
        #     best_img = response_data.get('choices', [])[0].get('message', {}).get('content', '') 
        #     return best_img
        #     # # Open the image
        #     # image = Image.open(result_image_path)
        #     # image.show()

        # else:
        #     print(f"Request failed with status code {response.status_code}: {response.text}")
        #     return None






if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_image_path = os.path.join(script_dir, "modelsImages", "model4.png")
    garment_image_path = os.path.join(script_dir, "garmentsImages", "garment7.jpg")


    # Check if the files exist
    if not os.path.exists(model_image_path):
        raise FileNotFoundError(f"Model image not found: {model_image_path}")
    if not os.path.exists(garment_image_path):
        raise FileNotFoundError(f"Garment image not found: {garment_image_path}")

    ModelProcessor.process_image(model_image_path, garment_image_path)