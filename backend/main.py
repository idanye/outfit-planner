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
    zara_url = "https://www.zara.com/il/en/cropped-shirt-with-cutwork-embroidery-p03564079.html?v1=365453566&v2=2352910"
    # zara_url = 'https://www.zara.com/il/en/thin-stripe-oxford-shirt-p08372130.html?v1=364107803&v2=2352910'
    # hm_url = 'https://www2.hm.com/en_us/productpage.0927047002.html'

    # base_directory = ".\\backend\\scrapers\\scraped_images" # nofar's path
    base_directory = ".\\scrapers\\scraped_images"  # Idan's path
    save_directory = ".\\garmentsImages"

    scraper = ScraperFactory.get_scraper(zara_url)
    saved_directory, item_name = scraper.scrape_images(zara_url, base_directory)
    print(f"Saved directory: {saved_directory}")

    garment_garment_image_path = save_first_image_without_person(saved_directory, save_directory)
    # garment_garment_image_path = save_first_image_without_person("./scrapers/scraped_images/zara_images_2024_06_14-21_15", save_directory)
    # garment_garment_image_path = save_first_image_without_person(".\\backend\\scrapers\\scraped_images\\zara_images_2024_06_14-21_15", save_directory) # nofar's path
    print(f"The new location of the image: {garment_garment_image_path}")

    # item_name = "COTTON AND MODAL CROP TOP"
    classifier = ClothesClassifier()
    category = classifier.classify_item(item_name)
    print(f"Item '{item_name}' is classified as: {category}")

    model_image_path = ".\\modelsImages\\model_2.jpg"
    ModelProcessor.process_image(model_image_path, garment_garment_image_path, category)


if __name__ == "__main__":
    main()
    # uvicorn.run(app, host="0.0.0.0", port=8000)
