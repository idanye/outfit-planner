from fastapi import FastAPI
from model_processor import ModelProcessor
import uvicorn
import os
import shutil
from scrapers.scraper_factory import ScraperFactory
from detection.person_detector import PersonDetector

app = FastAPI()


def main():
    zara_url = 'https://www.zara.com/il/en/linen-blend-shirt-with-buckle-p04764110.html?v1=365948358&v2=2352910'
    # hm_url = 'https://www2.hm.com/en_us/productpage.0927047002.html'

    save_directory = './images'
    result_directory = './no_model_images'

    scraper = ScraperFactory.get_scraper(zara_url)
    person_detector = PersonDetector()

    scraper.scrape_images(zara_url, save_directory)

    if not os.path.exists(result_directory):
        os.makedirs(result_directory)

    for image_file in os.listdir(save_directory):
        image_path = os.path.join(save_directory, image_file)

        if not person_detector.detect_person_in_image(image_path):
            print(f"No person detected in {image_file}, saving...")
            shutil.copy(image_path, os.path.join(result_directory, image_file))

    ModelProcessor.process_image()


if __name__ == "__main__":
    main()
    # uvicorn.run(app, host="0.0.0.0", port=8000)
