# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Company(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    sro = scrapy.Field()
    short_title = scrapy.Field()
    status = scrapy.Field()
    reg_date = scrapy.Field()
    inn = scrapy.Field()
    ogrn = scrapy.Field()
    address = scrapy.Field()
    fio = scrapy.Field()
    end_insurance_date = scrapy.Field()
    insurance_amount = scrapy.Field()
    insurance_company_title = scrapy.Field()
    pass
