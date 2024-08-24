import shutil
import os


class ImageManager:
    # Move the result image to the resultImages folder
    @staticmethod
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


    @staticmethod
    def take_input_images():
        model_image_path = "C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\backend\\modelsImages\\model4.png"
        garment_image_path = "C:\\Users\\Nofar\\year4SemB\\FromIdeaToApp\\outfit-planner\\backend\\garmentsImages\\garment7.jpg"
        return model_image_path, garment_image_path