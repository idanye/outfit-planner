from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model_processor import ModelProcessor
from scrapers.scraper_factory import ScraperFactory
from detection.person_detector import save_first_image_without_person
from classification.clothes_classifier import ClothesClassifier

app = FastAPI()


class ScrapeRequest(BaseModel):
    url: str


class ClassifyRequest(BaseModel):
    item_name: str


class ProcessRequest(BaseModel):
    model_image_path: str
    garment_image_path: str
    category: str


base_directory = "./scrapers/scraped_images"  # Adjusted path
save_directory = "./garmentsImages"


@app.post("/scrape-images/")
async def scrape_images(request: ScrapeRequest):
    scraper = ScraperFactory.get_scraper(request.url)
    saved_directory, item_name = scraper.scrape_images(request.url, base_directory)
    garment_image_path = save_first_image_without_person(saved_directory, save_directory)
    return {"saved_directory": saved_directory, "item_name": item_name, "garment_image_path": garment_image_path}


@app.post("/classify-item/")
async def classify_item(request: ClassifyRequest):
    classifier = ClothesClassifier()
    category = classifier.classify_item(request.item_name)
    return {"item_name": request.item_name, "category": category}


@app.post("/process-image/")
async def process_image(request: ProcessRequest):
    try:
        ModelProcessor.process_image(request.model_image_path, request.garment_image_path, request.category)
        return {"message": "Image processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
