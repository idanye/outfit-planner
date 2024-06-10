from abc import ABC, abstractmethod


class BaseScraper(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def scrape_images(self, url, save_directory):
        pass
