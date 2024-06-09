from gradio_client import Client, file
import requests
from PIL import Image
from io import BytesIO
import shutil
import os


def move_image(original_img_path, counter):
    filename_without_extension, extension = os.path.splitext(os.path.basename(original_img_path))
    # filename = os.path.basename(original_img_path)
    new_filename = f"{filename_without_extension}_{counter}{extension}"
    # Define the new path including the filename
    destination_path = os.path.join("C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\backend\\resultImages", new_filename)
    # Rename (move) the file
    # os.rename(original_img_path, destination_path)
    
    # Use shutil.move to overwrite the file if it already exists
    shutil.move(original_img_path, destination_path)

# Local file paths
model_image_path = "C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\backend\\modelsImages\\model4.png"
garment_image_path = "C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\backend\\\garmentsImages\\garment7.jpg"

# Initialize the Gradio client
client = Client("https://levihsu-ootdiffusion.hf.space/--replicas/iif7h/")

for i in range(1,3):
    # Make the API call
    result = client.predict(
        file(model_image_path),  # Use gradio_client.file() to specify the file path
        file(garment_image_path),  # Use gradio_client.file() to specify the file path
        "Lower-body",  # Literal['Upper-body', 'Lower-body', 'Dress']  in 'Garment category (important option!!!)'
        # Dropdown component
        1,  # float (numeric value between 1 and 4) in 'Images' Slider component
        20,  # float (numeric value between 20 and 40) in 'Steps' Slider component
        1,  # float (numeric value between 1.0 and 5.0) in 'Guidance scale' Slider component
        -1,  # float (numeric value between -1 and 2147483647) in 'Seed' Slider component
        api_name="/process_dc"
    )

    # print(result)
    original_img_path = result[0]['image']
    # extracted_path = result[0]['image'].replace("\\\\", "\\")
    move_image(original_img_path, i)