# from scraper.scraper.items import ScraperItem
import os
from os import environ, environb
import scrapy
# from scrapy.spiders import CrawlSpider

# from main.models import Quote
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_app.scrapy_app.spiders.icrawler import IcrawlerSpider
import django
django.setup()

# from scrapy.spiders import CrawlSpider
# from scrapy.spiders import Rule
# from scrapy.linkextractors import LinkExtractor
# from scrapy.loader import ItemLoader
# from scrapy.loader.processors import TakeFirst
print('in start spider file main file****************')

process = CrawlerProcess(get_project_settings())
# 'http://quotes.toscrape.com/tag/humor/'
url = 'https://www.filimo.com/movies/'
process.crawl(IcrawlerSpider, url=url)
process.start()
