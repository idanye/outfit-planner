from gradio_client import Client, file
import requests
from PIL import Image
from io import BytesIO
import shutil
import os


# Local file paths
model_image_path = "C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\model_image.jpg"
garment_image_path = "C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\garment_image.jpeg"

# Initialize the Gradio client
client = Client("https://levihsu-ootdiffusion.hf.space/--replicas/iif7h/")

# Make the API call
result = client.predict(
    file(model_image_path),  # Use gradio_client.file() to specify the file path
    file(garment_image_path),  # Use gradio_client.file() to specify the file path
    "Lower-body",	# Literal['Upper-body', 'Lower-body', 'Dress']  in 'Garment category (important option!!!)' Dropdown component
    1,  # float (numeric value between 1 and 4) in 'Images' Slider component
    20,  # float (numeric value between 20 and 40) in 'Steps' Slider component
    1,  # float (numeric value between 1.0 and 5.0) in 'Guidance scale' Slider component
    -1,  # float (numeric value between -1 and 2147483647) in 'Seed' Slider component
    api_name="/process_dc"
)

# Print the result
print(result)

# # Assuming the result is a file path
# result_image_path = result['output'][0]  # Adjust this based on the actual output structure


# # Define the new path for the result image
# new_result_image_path = os.path.join("C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\outputImages", os.path.basename(result_image_path))

# # Move the result image to the desired directory
# shutil.move(result_image_path, new_result_image_path)





