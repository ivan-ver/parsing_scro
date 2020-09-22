# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from Parsing_SRO.items import reestr_nostroy_ru
import logging
from Parsing_SRO.utils_.db_company import Database


class SroSpiderSpider(scrapy.Spider):
    page = 4685
    name = 'reestr_nostroy_ru'
    main_url = 'http://reestr.nostroy.ru'
    start_urls = [
        # 'http://reestr.nostroy.ru/reestr',
        'http://reestr.nostroy.ru/reestr?sort=m.id&direction=asc&page=',
    ]
    logging.basicConfig(filename='logogo.log',
                        level=logging.INFO)
    all_urls = None

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'DOWNLOAD_TIMEOUT': 10,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 10,
        # 'CONCURRENT_REQUESTS_PER_IP': 10,
        'CONCURRENT_REQUESTS': 10
    }

    def __init__(self):
        with Database() as db:
            self.all_urls = db.get_all_urls(self.name)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url + str(self.page), callback=self.parse, dont_filter=True)

    def parse(self, response):

        print("page # " + str(self.page))
        table = response.xpath("//table[@class='items table table-selectable-row table-striped']/tbody/tr")
        for row in table:
            try:
                company_url = self.main_url + row.xpath('@rel').get()
                if company_url not in self.all_urls:
                    company = reestr_nostroy_ru()
                    company['sro'] = row.xpath("td[7]/text()").get()
                    company['ogrn'] = row.xpath("td[4]/text()").get()
                    company['inn'] = row.xpath("td[3]/text()").get()
                    company['status'] = row.xpath("td[5]/text()").extract()[1].strip()
                    yield Request(url=company_url, callback=self.main_info_parse,
                                  dont_filter=True,
                                  cb_kwargs={'company': company})
                else:
                    continue
            except BaseException:
                logging.warning(
                    "Spider URL:" + self.main_url + row.xpath('@rel').get() + " exept: " + str(BaseException))
        next_page = None
        try:
            next_page = response.xpath("//div[@class='pagination-wrapper']/ul/li/a[text()='>']/@href").get()
        except:
            logging.warning("No nex page")
        logging.info("page # " + str(self.page))
        self.page += 1
        if next_page:
            try:
                yield Request(url=self.main_url + next_page, callback=self.parse, dont_filter=True)
            except BaseException:
                logging.warning("Next_page_error:" + self.main_url + next_page + ",page # " + str(self.page))

    def main_info_parse(self, response, company):
        try:
            company['url'] = response.url
            table = response.xpath("//table[@class='items table']/tbody/tr")
            table_values = dict()
            for row in table[3:-1]:
                text_list = row.xpath('th/text()').get().strip().split(' ')
                key = text_list[0] + " " + text_list[1]
                value = row.xpath('td/text()').get()
                table_values[key] = value
            company['title'] = table_values['Полное наименование'].replace('\n', '')
            company['reg_date'] = table_values['Дата регистрации']
            company['reg_number'] = table_values['Регистрационный номер']
            company['address'] = table_values['Адрес места'].replace('\n', '')
            company['telephone'] = table_values['Номер контактного']
            company['fio'] = table_values['Фамилия, имя,']
        except:
            print('Main_info_ERROR')
        yield Request(url=response.url + '/insurance',
                    callback=self.insurance_parse,
                    cb_kwargs=dict(company=company))

    def insurance_parse(self, response, company):
        if len(response.xpath("//table[@class='items table']/tbody/tr").extract()) == 3:
            company['end_insurance_date'] = None
            company['insurance_amount'] = None
            company['insurance_company_title'] = None
        else:
            head_table = response.xpath("//table[@class='items table']/tbody/tr[2]/th/a/text()").extract()
            head_table.insert(0, "№")
            table = {x: list() for x in head_table}
            for row1 in response.xpath("//table[@class='items table']/tbody/tr")[3:]:
                k = 0
                for i in row1.xpath("td"):
                    if i.xpath("text()").get():
                        table[head_table[k]].append(i.xpath("text()").get())
                    else:
                        table[list(table.keys())[k]].append(' ')
                    k += 1
            company['insurance_amount'] = ', '.join(table['Размер страховой суммы'])
            company['insurance_company_title'] = ', '.join(table['Наименование страховой компании'])
            company['end_insurance_date'] = ', '.join(table['Окончание действия договора'])
            company['insurance_telephone'] = ', '.join(table['Контактные телефоны'])
            self.all_urls.append(company['url'])
        yield company

