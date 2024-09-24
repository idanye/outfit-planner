from .zara_scraper import ZaraScraper


class ScraperFactory:
    @staticmethod
    def get_scraper(url):
        if 'zara.com' in url:
            return ZaraScraper()
        else:
            raise ValueError("No scraper available for the given URL")
