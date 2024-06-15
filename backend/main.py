from fastapi import FastAPI
from model_processor import ModelProcessor
import uvicorn
import os
import shutil
from scrapers.zara_scraper import ZaraScraper
from scrapers.scraper_factory import ScraperFactory
from scrapers.zara_scraper import ZaraScraper
from detection.person_detector import save_first_image_without_person
from classification.clothes_classifier import ClothesClassifier

app = FastAPI()


def main():
    zara_url ="https://www.zara.com/il/en/satin-midi-dress-with-foil-detail-p02180217.html?v1=368742147&v2=2352823"
    # zara_url= 'https://www.zara.com/il/en/short-gabardine-dress-with-ties-p03515211.html?v1=362609455&v2=2352910'
    # hm_url = 'https://www2.hm.com/en_us/productpage.0927047002.html'

    # base_directory = ".\\backend\\scrapers\\scraped_images" # nofar's path
    base_directory = ".\\scrapers\\scraped_images"  # Idan's path
    save_directory = ".\\garmentsImages"

    scraper = ScraperFactory.get_scraper(zara_url)
    saved_directory, item_name = scraper.scrape_images(zara_url, base_directory)
    print(f"Saved directory: {saved_directory}")

    image_path = save_first_image_without_person(saved_directory, save_directory)
    # image_path = save_first_image_without_person("./scrapers/scraped_images/zara_images_2024_06_14-21_15", save_directory)
    # image_path = save_first_image_without_person(".\\backend\\scrapers\\scraped_images\\zara_images_2024_06_14-21_15", save_directory) # nofar's path
    print(f"The new location of the image: {image_path}")

    # item_name = "COTTON AND MODAL CROP TOP"
    classifier = ClothesClassifier()
    category = classifier.classify_item(item_name)
    print(f"Item '{item_name}' is classified as: {category}")

    # ModelProcessor.process_image()


if __name__ == "__main__":
    main()
    # uvicorn.run(app, host="0.0.0.0", port=8000)


