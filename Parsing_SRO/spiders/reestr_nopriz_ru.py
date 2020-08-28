# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from Parsing_SRO.items import reestr_nopriz_ru
import logging
from Parsing_SRO.utils_.db_company import Database


class NoprizSpiderSpider(scrapy.Spider):
    name = 'reestr_nopriz_ru'

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        # 'DOWNLOAD_TIMEOUT': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 10,
        'CONCURRENT_REQUESTS_PER_IP': 10,
        # 'CONCURRENT_REQUESTS': 10
    }

    main_url = 'http://reestr.nopriz.ru'
    start_urls = [
        # 'http://reestr.nopriz.ru/reestr',
        'http://reestr.nopriz.ru/reestr?sort=us.registrationNumber&direction=asc&page=576'
    ]
    page = 676
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
        table_info = response.xpath("//table[@class='table b-table-organizations']/tbody//tr")
        for row in table_info:
            try:
                company_url = self.main_url + row.xpath("td/a/@href").get()
                if company_url not in self.all_urls:
                    item = reestr_nopriz_ru()
                    info_ = row.xpath("td/text()").extract()
                    item['sro'] = info_[0]
                    item['status'] = info_[2].strip()
                    item['reg_date'] = info_[5]
                    yield Request(url=self.main_url + row.xpath("td/a/@href").get(),
                                  callback=self.parse_main_info,
                                  cb_kwargs={'item': item}, dont_filter=True)
                else:
                    continue
            except BaseException:
                logging.warning(
                    "Spider URL:" + self.main_url + row.xpath('@rel').get() + " exept: " + str(BaseException))

        next_page = None
        try:
            next_page = response.xpath("//div[@class='col-xs-6']/ul/li/a[text()='»']/@href").get()
        except:
            logging.warning("No next page")
        if next_page:
            print("next_page: " + str(self.page))
            try:
                yield Request(url=self.main_url + next_page, callback=self.parse)
            except BaseException:
                logging.warning("Next_page_error:" + self.main_url + next_page + ",page # " + str(self.page))

    def parse_main_info(self, response, item):
        item['url'] = response.url
        content = response.xpath("//table[@class='table']/tr")
        try:
            for row in content:
                if 'Полное наименование:' in row.xpath('td[1]/text()').get():
                    item['title'] = row.xpath('td[2]/text()').get()
                elif 'Регистрационный номер' in row.xpath('td[1]/text()').get():
                    item['reg_number'] = row.xpath('td[2]/text()').get().split(' ')[0]
                elif 'ОГРН:' in row.xpath('td[1]/text()').get():
                    item['ogrn'] = row.xpath('td[2]/text()').get()
                elif 'ИНН:' in row.xpath('td[1]/text()').get():
                    item['inn'] = row.xpath('td[2]/text()').get()
                elif 'Номер контактного телефона' in row.xpath('td[1]/text()').get():
                    item['telephone'] = row.xpath('td[2]/text()').get()
                elif 'Адрес' in row.xpath('td[1]/text()').get():
                    item['address'] = row.xpath('td[2]/text()').get()
                elif 'ФИО' in row.xpath('td[1]/text()').get():
                    item['fio'] = row.xpath('td[2]/text()').get().split(' ')[-3] + ' ' \
                                  + row.xpath('td[2]/text()').get().split(' ')[-2] + ' ' \
                                  + row.xpath('td[2]/text()').get().split(' ')[-1]
        except:
            logging.warning("Item_main_info_error:" + response.url)
        yield Request(url=response.url + '/insurance',
                      callback=self.parse_insurance_info,
                      cb_kwargs={'item': item}, dont_filter=True)

    def parse_insurance_info(self, response, item):
        try:
            table = response.xpath("//table[@class='table b-table-insurance']/tbody/tr")[3:]
            main_res = set()
            for row in table:
                a = row.xpath("td/text()").extract()[2].strip()
                t = row.xpath("td/text()").extract()[3].strip()
                tel = row.xpath("td/text()").extract()[6].strip()
                main_res.add(a + '!' + t + '!' + tel)
            item['insurance_amount'] = ','.join([i.split("!")[0] for i in main_res])
            item['insurance_company_title'] = ','.join([i.split("!")[1] for i in main_res])
            item['insurance_telephone'] = ','.join([i.split("!")[2] for i in main_res])
            self.all_urls.append(item['url'])
            yield item
        except:
            logging.warning("Item_insurance_info_error:" + response.url)
