import os
import re
import requests
from datetime import datetime
from selenium.webdriver.firefox.options import Options
from .base_scraper import BaseScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ZaraScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # Setup Selenium WebDriver options
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=firefox_options)

    def handle_policy_text(self):
        try:
            # Wait for the policy text to appear
            policy_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.onetrust-close-btn-handler"))
            )
            # Click the accept button
            policy_element.click()
            print("Policy text handled.")
        except Exception as e:
            print(f"Policy text not found or could not be handled: {e}")

    def scrape_images(self, url, base_directory):
        try:
            self.driver.get(url)
            # Add a print to indicate the URL has been opened
            print(f"Opened URL: {url}")

            # Handle policy text if it appears
            self.handle_policy_text()

            # Wait for the images to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "button.product-detail-images__image-action-wrapper picture"))
            )
            print("Located image elements.")

            # Find all picture elements
            picture_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                         "button.product-detail-images__image-action-wrapper picture")
            print(f"Found {len(picture_elements)} images on the page")

            # Find the item's name
            item_name_element = self.driver.find_element(By.CSS_SELECTOR, "h1.product-detail-info__header-name")
            item_name = item_name_element.text
            print(f"Item's name: {item_name}")

            image_urls = []
            for picture in picture_elements:
                # Get the highest resolution URL from the srcset attribute
                sources = picture.find_elements(By.TAG_NAME, 'source')
                high_res_url = None
                if sources:
                    max_width = 0
                    for source in sources:
                        srcset = source.get_attribute('srcset')
                        urls = srcset.split(',')
                        for url in urls:
                            url = url.strip()
                            match = re.search(r'(\d+)w', url)
                            if match:
                                width = int(match.group(1))
                                if width > max_width:
                                    max_width = width
                                    high_res_url = url.split(' ')[0]

                if not high_res_url or 'transparent-background' in high_res_url:
                    # Fallback to the img src attribute if high_res_url is not found or is a placeholder
                    img = picture.find_element(By.TAG_NAME, 'img')
                    img_src = img.get_attribute('src')
                    if 'transparent-background' not in img_src:
                        high_res_url = img_src.split('?')[0]

                if high_res_url and 'transparent-background' not in high_res_url:
                    # print(f"Adding image URL: {high_res_url}")
                    image_urls.append(high_res_url)

            # Create a unique directory for each run
            timestamp = datetime.now().strftime('%Y_%m_%d-%H_%M')
            save_directory = os.path.join(base_directory, f'zara_images_{timestamp}')
            print(f"Downloading {len(image_urls)} images to {save_directory}")

            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            for idx, img_url in enumerate(image_urls):
                filename = os.path.join(save_directory, f"image_{idx}.jpg")
                self.download_image(img_url, filename)

            save_directory = save_directory.replace("./", "")
            relative_path = save_directory
            return relative_path, item_name

        except Exception as e:
            print(f"Exception occurred: {e}")

        finally:
            # Close the driver
            self.driver.quit()

    def download_image(self, url, save_path):
        try:
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(8192):
                        file.write(chunk)
                print("Downloaded image successfully")
            else:
                print(f"Failed to download image from {url}")
        except Exception as e:
            print(f"Exception occurred while downloading image from {url}: {e}")
