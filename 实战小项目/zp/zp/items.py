# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZpItem(scrapy.Item):
    job_name = scrapy.Field()
    job_news = scrapy.Field()
    job_city = scrapy.Field()
    job_ex=scrapy.Field()
    job_edu = scrapy.Field()
    job_company = scrapy.Field()
    c_info = scrapy.Field()
    c_num = scrapy.Field()
    c_tag = scrapy.Field()