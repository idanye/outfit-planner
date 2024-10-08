from datetime import datetime
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from model_processor import ModelProcessor
from scrapers.scraper_factory import ScraperFactory
from detection.person_detector import save_first_image_without_person
from classification.clothes_classifier import ClothesClassifier

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Get the absolute path to the backend directory
backend_dir = os.path.abspath(os.path.dirname(__file__))  # Absolute path to the backend directory
base_directory = os.path.join(backend_dir, "scrapers/scraped_images")  # Path for scraped images
save_directory = os.path.join(backend_dir, "garmentsImages")  # Path for garment images
model_directory = os.path.join(backend_dir, "modelsImages")  # Path for model images
result_directory = os.path.join(backend_dir, "resultImages")  # Path for result images

# Get the absolute path to the frontend directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

# Serve model images from the "garmentsImages" directory
app.mount("/garments-images", StaticFiles(directory=save_directory), name="garments-images")

# Serve model images from the "garmentsImages" directory
app.mount("/model-result-image", StaticFiles(directory=result_directory), name="model-result-image")


class ScrapeRequest(BaseModel):
    url: str


class ClassifyRequest(BaseModel):
    item_name: str


class ProcessRequest(BaseModel):
    model_image_path: str
    garment_image_path: str
    category: str


@app.post("/upload-model-image/")
async def upload_model_image(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")

    try:
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        current_time = datetime.now().strftime("%Y_%m_%d-%H_%M")
        unique_filename = f"model_image-{current_time}{file_extension}"

        # Save the uploaded file to the local filesystem
        file_path = os.path.join(model_directory, unique_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        print(f"File saved to: \n{file_path}")

        return {"model_image_url": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape-images/")
def get_scraped_images(request: ScrapeRequest):
    print("get_scraped_images function started")

    scraper = ScraperFactory.get_scraper(request.url)

    # Call the scraper function and ensure it returns an absolute path
    relative_saved_directory, item_name = scraper.scrape_images(request.url, base_directory)
    saved_directory = os.path.join(base_directory, relative_saved_directory)  # Ensure full path

    garment_image_path = save_first_image_without_person(saved_directory, save_directory)

    # Ensure the image file exists
    if os.path.exists(garment_image_path):
        # Create a URL that the frontend can use to access the image
        image_url = f"/garments-images/{os.path.basename(garment_image_path)}"
        print(f"scrape_images function returning: saved_directory: {saved_directory}, item_name: {item_name}, "
              f"garment_image_path: {image_url}")

        return {"saved_directory": saved_directory, "item_name": item_name, "garment_image_path": image_url}
    else:
        print("scrape_images function: No image found")
        # Return an error message if no image is found
        return {"saved_directory": saved_directory, "item_name": item_name, "garment_image_path": "None"}


@app.post("/classify-item/")
def get_classified_item(request: ClassifyRequest):
    print(f"get_classified_item function started with item name: {request.item_name}")

    classifier = ClothesClassifier()
    category = classifier.classify_item(request.item_name)
    print(f"Item name: {request.item_name}, Category: {category}")

    return {"item_name": request.item_name, "category": category}


@app.post("/model-process-image/")
def get_processed_image(request: ProcessRequest):
    print("get_processed_image function started")

    try:
        # Adjust paths to be relative to the backend directory
        base_dir = os.path.join(os.getcwd(), "backend")
        print(f"Current working directory: {base_dir}")

        model_image_path = os.path.join(base_dir, request.model_image_path)

        # Handle garment image path, replacing URL part with local directory
        garment_image_path = request.garment_image_path
        garment_image_filename = garment_image_path.replace("http://localhost:8000/garments-images/", "")
        garment_image_path = os.path.join(base_dir, "garmentsImages", garment_image_filename)

        print(f"Absolute model image path: {model_image_path}")
        print(f"Absolute garment image path: {garment_image_path}")

        # Process the image
        result_image_path = ModelProcessor.process_image(model_image_path, garment_image_path, request.category)

        if result_image_path and os.path.exists(result_image_path):
            print("Image processed successfully")
            result_path = f"/model-result-image/{os.path.basename(result_image_path)}"

            return result_path

        else:
            print("Failed to process the image or file does not exist.")
            return "None"

    except Exception as e:
        print(f"get_processed_image function error: {str(e)}")
        return "None"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=443, reload=True)
