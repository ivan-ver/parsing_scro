# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class reestr_nostroy_ru(scrapy.Item):
    url = scrapy.Field()
    sro = scrapy.Field()
    title = scrapy.Field()
    status = scrapy.Field()
    reg_date = scrapy.Field()
    reg_number = scrapy.Field()
    inn = scrapy.Field()
    ogrn = scrapy.Field()
    telephone = scrapy.Field()
    address = scrapy.Field()
    fio = scrapy.Field()
    end_insurance_date = scrapy.Field()
    insurance_amount = scrapy.Field()
    insurance_company_title = scrapy.Field()
    insurance_telephone = scrapy.Field()

class reestr_nopriz_ru(scrapy.Item):
    url = scrapy.Field()
    sro = scrapy.Field()
    title = scrapy.Field()
    status = scrapy.Field()
    reg_date = scrapy.Field()
    reg_number = scrapy.Field()
    inn = scrapy.Field()
    ogrn = scrapy.Field()
    telephone = scrapy.Field()
    address = scrapy.Field()
    fio = scrapy.Field()
    end_insurance_date = scrapy.Field()
    insurance_amount = scrapy.Field()
    insurance_company_title = scrapy.Field()
    insurance_telephone = scrapy.Field()


class sro_reestr_nopriz_ru(scrapy.Item):
    url = scrapy.Field()
    status = scrapy.Field()
    reg_number = scrapy.Field()
    title = scrapy.Field()
    inn = scrapy.Field()
    ogrn = scrapy.Field()
    address = scrapy.Field()
    telephone = scrapy.Field()
    email = scrapy.Field()
    web_site = scrapy.Field()


class sro_reestr_nostroy_ru(scrapy.Item):
    url = scrapy.Field()
    status = scrapy.Field()
    reg_number = scrapy.Field()
    title = scrapy.Field()
    inn = scrapy.Field()
    ogrn = scrapy.Field()
    address = scrapy.Field()
    telephone = scrapy.Field()
    email = scrapy.Field()
    web_site = scrapy.Field()


