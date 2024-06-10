from zara_scraper import ZaraScraper
# from hm_scraper import HmScraper


class ScraperFactory:
    @staticmethod
    def get_scraper(url):
        if 'zara.com' in url:
            return ZaraScraper()
        # elif 'hm.com' in url:
        #     return HmScraper()
        else:
            raise ValueError("No scraper available for the given URL")
