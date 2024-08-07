from fastapi import FastAPI, HTTPException
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


base_directory = "./scrapers/scraped_images"
save_directory = "./garmentsImages"


@app.post("/scrape-images/")
def scrape_images(request: ScrapeRequest):
    scraper = ScraperFactory.get_scraper(request.url)
    saved_directory, item_name = scraper.scrape_images(request.url, base_directory)
    garment_image_path = save_first_image_without_person(saved_directory, save_directory)
    return {"saved_directory": saved_directory, "item_name": item_name, "garment_image_path": garment_image_path}


@app.post("/classify-item/")
def classify_item(request: ClassifyRequest):
    classifier = ClothesClassifier()
    category = classifier.classify_item(request.item_name)
    return {"item_name": request.item_name, "category": category}


@app.post("/process-image/")
def process_image(request: ProcessRequest):
    try:
        ModelProcessor.process_image(request.model_image_path, request.garment_image_path, request.category)
        return {"message": "Image processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)
