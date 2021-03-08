# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class ReadTheDocsSpider(CrawlSpider):
    name = 'readthedocs'
    allowed_domains = ['docs.scrapy.org']
    start_urls = [
        'https://docs.scrapy.org/en/latest/index.html',
    ]

    rules = (
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(), callback='parse_item'),
    )
    
    def parse_item(self, response):

        yield {
            'title': response.xpath("//title//text()").extract(),
            'url': response.urljoin(''),
            'text': ''.join(response.xpath("//body//text()").extract()).strip()
            }

