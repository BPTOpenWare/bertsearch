# -*- coding: utf-8 -*-
import scrapy

class ToScrapeSpiderXPath(scrapy.Spider):
    name = 'githubreadme'
    allowed_domains = ['github.com']
    start_urls = [
        'https://github.com/scrapy-plugins/scrapy-splash/blob/master/README.rst',
        'https://github.com/scrapinghub/scrapyrt/blob/master/README.rst',
    ]

    def parse(self, response):
    
       yield {
            'title': ''.join(response.xpath("//title//text()").extract()).strip(),
            'url': response.urljoin(''),
            'text': ''.join(response.xpath("//article//text()").extract()).strip()
            }

