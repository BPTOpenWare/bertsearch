# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class ARCoreSpider(CrawlSpider):
    name = 'arcore'
    allowed_domains = ['developers.google.com']
    start_urls = [
        'https://developers.google.com/ar/develop',
        'https://developers.google.com/ar/discover',
        'https://developers.google.com/ar/distribute',
        'https://developers.google.com/ar/reference'
    ]

    rules = (
        # limit links to just those under augmented reality path
        Rule(LinkExtractor(allow=r'/ar/'), callback='parse_item'),
    )
    
    def parse_item(self, response):

        yield {
            'title': response.xpath("//title//text()").extract(),
            'url': response.urljoin(''),
            'text': ''.join(response.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), 'devsite-article-body')]//text()").extract()).strip()
            }

