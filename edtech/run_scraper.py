from edtech.edtech.spiders.zaoju import ZaojuSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
import os, sys
from scrapy import signals
from crochet import setup
setup()

class Scraper:
    def __init__(self):
        settings_file_path = 'edtech.edtech.settings' # The path seen from root, ie. from main.py
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerRunner(get_project_settings())
        self.spider = ZaojuSpider # The spider you want to crawl

    def run_spiders(self,searchKeys):
        self.process.crawl(self.spider, searchKeys=searchKeys)
        # d.addBoth(lambda _: reactor.stop())
        # reactor.run()

        # self.process.signals.connect(reactor.stop, signal=signals.spider_closed)
        # self.process.crawl(self.spider)
        # self.process.start()  # the script will block here until the crawling is finished