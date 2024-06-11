from fastapi import FastAPI
from model_processor import ModelProcessor
import uvicorn
import os
import shutil
from scrapers.scraper_factory import ScraperFactory
from detection.person_detector import save_first_image_without_person
from classification.clothes_classifier import ClothesClassifier
app = FastAPI()


def main():
    zara_url = 'https://www.zara.com/il/en/draped-open-back-dress-p03152334.html?v1=364113503&v2=2352910'
    # hm_url = 'https://www2.hm.com/en_us/productpage.0927047002.html'

    base_directory = './scraped_images'

    scraper = ScraperFactory.get_scraper(zara_url)
    saved_directory, item_name = scraper.scrape_images(zara_url, base_directory)
    print(f"Saved directory: {saved_directory}")

    image_path = save_first_image_without_person(saved_directory)
    print(f"The new location of the image: {image_path}")

    # item_name = "COTTON AND MODAL CROP TOP"
    classifier = ClothesClassifier()
    category = classifier.classify_item(item_name)
    print(f"Item '{item_name}' is classified as: {category}")

    # ModelProcessor.process_image()


if __name__ == "__main__":
    main()
    # uvicorn.run(app, host="0.0.0.0", port=8000)
