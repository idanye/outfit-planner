from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from model_processor import ModelProcessor
from scrapers.scraper_factory import ScraperFactory
from detection.person_detector import save_first_image_without_person
from classification.clothes_classifier import ClothesClassifier
from azure.storage.blob import BlobServiceClient
from uuid import uuid4

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = "mycontainer"
container_client = blob_service_client.get_container_client(container_name)


def upload_test_file(file_path, blob_name):
    try:
        blob_client = container_client.get_blob_client(blob_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"Upload successful: {blob_client.url}")
        return blob_client.url
    except Exception as e:
        print(f"Failed to upload file: {e}")


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

# Get the absolute path to the frontend directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


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
    try:
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid4()}{file_extension}"

        # Upload the file directly to Azure Blob Storage
        blob_url = upload_test_file(file.file, unique_filename)

        return {"model_image_url": blob_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape-images/")
def scrape_images(request: ScrapeRequest):
    scraper = ScraperFactory.get_scraper(request.url)

    print(f"Base directory: {base_directory}")

    # Call the scraper function and ensure it returns an absolute path
    relative_saved_directory, item_name = scraper.scrape_images(request.url, base_directory)
    # print(f"Relative saved directory: {relative_saved_directory}")  # Debugging line

    saved_directory = os.path.join(base_directory, relative_saved_directory)  # Ensure full path

    # print(f"Saved directory path before processing: {saved_directory}")  # Debugging line

    garment_image_path = save_first_image_without_person(saved_directory, save_directory)
    return {"saved_directory": saved_directory, "item_name": item_name, "garment_image_path": garment_image_path}


@app.post("/classify-item/")
def classify_item(request: ClassifyRequest):
    classifier = ClothesClassifier()
    category = classifier.classify_item(request.item_name)
    print(f"Item name: {request.item_name}, Category: {category}")
    return {"item_name": request.item_name, "category": category}


@app.post("/process-image/")
def process_image(request: ProcessRequest):
    try:
        print(f"Model image path: {request.model_image_path}", f"Garment image path: {request.garment_image_path}")
        ModelProcessor.process_image(request.model_image_path, request.garment_image_path, request.category)
        return {"message": "Image processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=443, reload=True)
