# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from Parsing_SRO.items import reestr_nopriz_ru
import logging


class NoprizSpiderSpider(scrapy.Spider):
    name = 'reestr_nopriz_ru'
    main_url = 'http://reestr.nopriz.ru'
    start_urls = ['http://reestr.nopriz.ru/reestr']
    page = 0
    logging.basicConfig(filename='logogo.log',
                        level=logging.INFO)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        self.page += 1
        table_info = response.xpath("//table[@class='table b-table-organizations']/tbody//tr")
        for row in table_info:
            try:
                company = reestr_nopriz_ru()
                info_ = row.xpath("td/text()").extract()
                company['sro'] = info_[0]
                company['status'] = info_[2].strip()
                company['reg_date'] = info_[5]
                yield Request(url=self.main_url + row.xpath("td/a/@href").get(),
                              callback=self.parse_main_info,
                              cb_kwargs={'company': company}, dont_filter=True)

            except BaseException:
                logging.warning("Spider URL:" + self.main_url + row.xpath('@rel').get() + " exept: " + str(BaseException))

        next_page = response.xpath("//div[@class='col-xs-6']/ul/li/a/@href").extract()[-2]
        logging.info("page # " + str(self.page))
        if next_page:
            try:
                yield Request(url=self.main_url + next_page, callback=self.parse)
            except BaseException:
                logging.warning("Next_page_error:" + self.main_url + next_page + ",page # " + str(self.page))

    def parse_main_info(self, response, company):
        company['url'] = response.url
        table = [i.strip() for i in response.xpath("//table[@class='table']/tr/td/text()").extract()]
        keys = [i.split(' ')[0] for i in table[::2]]
        values = table[1::2]
        table_info = dict(zip(keys, values))


        company['title'] = table_info['Полное']
        company['reg_number'] = table_info['Регистрационный'].split(' ')[0]
        company['inn'] = table_info['ИНН:']
        company['ogrn'] = table_info['ОГРН:']
        company['fio'] = table_info['ФИО,'].split(' ')[-3] + ' ' \
                        + table_info['ФИО,'].split(' ')[-2] + ' ' \
                        + table_info['ФИО,'].split(' ')[-1]
        company['address'] = table_info['Адрес']
        company['telephone'] = table_info['Номер']


        yield Request(url=response.url + '/insurance',
                      callback=self.parse_insurance_info,
                      cb_kwargs={'company': company}, dont_filter=True)

    def parse_insurance_info(self, response, company):
        table = response.xpath("//table[@class='table b-table-insurance']/tbody/tr")[3:]
        main_res = set()
        for row in table:
            a = row.xpath("td/text()").extract()[2].strip()
            t = row.xpath("td/text()").extract()[3].strip()
            tel = row.xpath("td/text()").extract()[6].strip()
            main_res.add(a + '!' + t + '!' + tel)
        company['insurance_amount'] = ','.join([i.split("!")[0] for i in main_res])
        company['insurance_company_title'] = ','.join([i.split("!")[1] for i in main_res])
        company['insurance_telephone'] = ','.join([i.split("!")[2] for i in main_res])
        yield company
