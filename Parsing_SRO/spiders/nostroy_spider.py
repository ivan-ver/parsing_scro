# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from Parsing_SRO.items import SRO_member
from bs4 import BeautifulSoup as bs
import logging


class SroSpiderSpider(scrapy.Spider):
    name = 'nostroy_spider'
    main_url = 'http://reestr.nostroy.ru'
    start_urls = ['http://reestr.nostroy.ru/reestr']
    logging.basicConfig(filename='logogo.log',
                        level=logging.INFO)

    def start_requests(self):
        yield Request(url=self.start_urls[0],
                      callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//tbody/tr/@rel').extract()
        for url in urls:
            yield Request(url=self.main_url + url, callback=self.main_info_parse)
        # next_page = response.xpath("//div[@class='pagination-wrapper']/ul/li/a/@href").extract()[-2]
        # if next_page:
        #     yield Request(url=self.main_url + next_page, callback=self.parse)

    def main_info_parse(self, response):
        company = SRO_member()
        company['url'] = response.url
        company['sro'] = response.xpath("//nav[@id='navigation-block']/ul[@class='nav nav-pills']"
                                        "/li[@class='active']/a/text()").get()
        # .split(' ')[-1]
        table = response.xpath("//table[@class='items table']/tbody/tr").extract()[4:-2]
        table_values = dict()
        for row in table:
            key = bs(row).find('th').text.strip().split(' ')[0] + " " + bs(row).find('th').text.strip().split(' ')[1]
            value = bs(row).find('td').text.strip()
            table_values[key] = value

        company['short_title'] = table_values['Сокращенное наименование']
        company['status'] = table_values['Статус члена']
        company['reg_date'] = table_values['Дата регистрации']
        company['inn'] = table_values['Идентификационный номер']
        company['ogrn'] = table_values['Основной государственный']
        company['address'] = table_values['Адрес места']
        company['fio'] = table_values['Фамилия, имя,'].split(' ')[-3] + " " \
                         + table_values['Фамилия, имя,'].split(' ')[-2] + " " \
                         + table_values['Фамилия, имя,'].split(' ')[-1]

        yield Request(url=response.url + '/insurance',
                      callback=self.insurance_parse,
                      cb_kwargs=dict(company=company))

    def insurance_parse(self, response, company):
        if len(response.xpath("//table[@class='items table']/tbody/tr").extract()) == 3:
            company['end_insurance_date'] = None
            company['insurance_amount'] = None
            company['insurance_company_title'] = None
        else:
            table = response.xpath("//table[@class='items table']/tbody/tr[4]/td/text()").extract()
            company['end_insurance_date'] = table[2]
            company['insurance_amount'] = table[4]
            company['insurance_company_title'] = table[5]

        if len(response.xpath("//table[@class='items table']/tbody/tr").extract()) > 4:
            logging.info('Warning! company ' + company['url'] + ' has more then one insurance company')

        yield company

