import scrapy
import argparse, sys, os
from twisted.internet import reactor
from scrapy.settings import Settings
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from typing import List

class ZaojuSpider(scrapy.Spider):
    name = 'zaoju'
    allowed_domains = ['zaojv.com']
    start_urls = ['http://zaojv.com/']

    def __init__(self, searchKeys:List[str]=["设想"]):
        self.searchKeys = searchKeys

    def parse(self, response):
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6,zh;q=0.5",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://zaojv.com/",
        }
        
        search_url = "https://zaojv.com/wordQueryDo.php"

        for searchKey in self.searchKeys:
            item = {
                'searchKey':searchKey
            }
            data = {"wo":searchKey}
            yield scrapy.FormRequest(
                url=search_url,
                formdata=data,
                headers=headers,
                meta={'item':item},
                callback=self.parse_result,
            )

    def parse_result(self, response):
        item = response.meta['item']
        searchkey = item['searchKey']

        response_texts = response.xpath('//li[@class="dotline"]/a/text()').getall()
        response_url = response.xpath('//li[@class="dotline"]/a/@href').getall()

        if response_texts:
            # find location of the search keyword
            # if cannot find, return the first result
            try:
                ind = response_texts.index(searchkey+"造句")
            except ValueError:
                ind = 0

            sentence_page = "https://zaojv.com"+response_url[ind]

            yield scrapy.Request(
                sentence_page,
                meta={'item':item},
                callback=self.parse_sentences,
            )
        else:
            yield None

    def parse_sentences(self, response):
        item = response.meta['item']
        for sentence in response.xpath('//div[@id="all"]/div').getall():
            item['sentence'] = sentence
            yield item

# parser=argparse.ArgumentParser()
# parser.add_argument('--searchkeys', type=str, help='keywords to be searched')
# args=parser.parse_args()

# # set settings path
# settings_file_path = 'edtech.edtech.settings'
# os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

# configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
# runner = CrawlerRunner(get_project_settings())
# d = runner.crawl(ZaojuSpider)
# d.addBoth(lambda _: reactor.stop())
# reactor.run()

# # close reactor after finishing crawling
# os.execl(sys.executable, *sys.argv)