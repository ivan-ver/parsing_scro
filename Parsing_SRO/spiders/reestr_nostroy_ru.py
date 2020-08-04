# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from Parsing_SRO.items import reestr_nostroy_ru
import logging
from Parsing_SRO.utils_.db_company import Database


class SroSpiderSpider(scrapy.Spider):
    page = 0
    name = 'reestr_nostroy_ru'
    main_url = 'http://reestr.nostroy.ru'
    start_urls = ['http://reestr.nostroy.ru/reestr']
    logging.basicConfig(filename='logogo.log',
                        level=logging.INFO)
    all_urls = None

    def __init__(self):
        with Database() as db:
            self.all_urls = db.get_all_urls(self.name)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        self.page += 1
        table = response.xpath("//table[@class='items table table-selectable-row table-striped']/tbody/tr")
        for row in table:
            try:
                company = reestr_nostroy_ru()
                company['sro'] = row.xpath("td[7]/text()").get()
                company['ogrn'] = row.xpath("td[4]/text()").get()
                company['inn'] = row.xpath("td[3]/text()").get()
                company['status'] = row.xpath("td[5]/text()").extract()[1].strip()
                company_url = self.main_url + row.xpath('@rel').get()
                if company_url not in self.all_urls:
                    yield Request(url=company_url, callback=self.main_info_parse,
                                  dont_filter=True,
                                  cb_kwargs={'company': company})
            except BaseException:
                logging.warning("Spider URL:" + self.main_url + row.xpath('@rel').get() + " exept: "+str(BaseException))

        next_page = response.xpath("//div[@class='pagination-wrapper']/ul/li/a/@href").extract()[-2]
        logging.info("page # " + str(self.page))
        if next_page:
            try:
                yield Request(url=self.main_url + next_page, callback=self.parse, dont_filter=True)
            except BaseException:
                logging.warning("Next_page_error:" + self.main_url + next_page + ",page # " + str(self.page))

    def main_info_parse(self, response, company):
        company['url'] = response.url
        table = response.xpath("//table[@class='items table']/tbody/tr")
        table_values = dict()
        for row in table[3:-1]:
            text_list = row.xpath('th/text()').get().strip().split(' ')
            key = text_list[0] + " " + text_list[1]
            value = row.xpath('td/text()').get()
            table_values[key] = value

        company['title'] = table_values['Полное наименование']
        company['reg_date'] = table_values['Дата регистрации']
        company['reg_number'] = table_values['Регистрационный номер']
        company['address'] = table_values['Адрес места']
        company['telephone'] = table_values['Номер контактного']
        fio = table_values['Фамилия, имя,'].split(' ')
        company['fio'] = fio[-3] + " " + fio[-2] + " " + fio[-1]

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

