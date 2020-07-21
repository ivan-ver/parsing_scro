# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from Parsing_SRO.items import Company


class NoprizSpiderSpider(scrapy.Spider):
    name = 'nopriz-spider'
    main_url = 'http://reestr.nopriz.ru'
    start_urls = ['http://reestr.nopriz.ru/reestr']
    page = 0

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        self.page += 1
        table_info = response.xpath("//table[@class='table b-table-organizations']/tbody//tr")
        for row in table_info:
            company = Company()
            company['status'] = row.xpath("td/text()").extract()[2].strip()
            company['reg_date'] = row.xpath("td/text()").extract()[5]
            url = row.xpath("td/a/@href").get()
            yield Request(url=self.main_url + url,
                          callback=self.parse_main_info,
                          cb_kwargs={'company': company})

        # next = self.main_url + response.xpath("//div[@class='col-xs-6']/ul/li/a/@href").extract()[-2]
        # print("NEXT_PAGE " + str(self.page))
        # if self.page < 2:
        #     yield Request(url=next, callback=self.parse)

    def parse_main_info(self, response, company):
        company['url'] = response.url
        table = [i.strip() for i in response.xpath("//table[@class='table']/tr/td/text()").extract()]
        keys = [i.split(' ')[0] for i in table[::2]]
        values = table[1::2]
        table_info = dict(zip(keys, values))

        company['sro'] = table_info['СРО:']
        company['short_title'] = table_info['Сокращенное']
        company['reg_date'] = table_info['Регистрационный'].split(' ')[-1]
        company['inn'] = table_info['ИНН:']
        company['ogrn'] = table_info['ОГРН:']
        company['fio'] = table_info['ФИО,'].split(' ')[-3] + ' ' \
                        + table_info['ФИО,'].split(' ')[-2] + ' ' \
                        + table_info['ФИО,'].split(' ')[-1]
        company['address'] = table_info['Адрес']

        yield Request(url=response.url + '/insurance',
                      callback=self.parse_insurance_info,
                      cb_kwargs={'company': company})

    def parse_insurance_info(self, response, company):
        table = response.xpath("//table[@class='table b-table-insurance']/tbody/tr")[3:]
        main_res = set()
        for row in table:
            a = row.xpath("td/text()").extract()[2].strip()
            t = row.xpath("td/text()").extract()[3].strip()
            main_res.add(a + '!' + t)
        company['insurance_amount'] = ','.join([i.split("!")[0] for i in main_res])
        company['insurance_company_title'] = ','.join([i.split("!")[1] for i in main_res])
        yield company
