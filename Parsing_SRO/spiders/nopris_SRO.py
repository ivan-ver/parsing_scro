# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from Parsing_SRO.items import sro_reestr_nopriz_ru


class NoprisSrpSpider(scrapy.Spider):
    name = 'nopris_SRO'
    start_urls = ['http://reestr.nopriz.ru']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        statuses = response.xpath(
            "//table[@class='table b-table-index table-selectable-row table-status']/tbody/tr/td[1]/span/@title")\
            .extract()
        reg_nums = response.xpath(
            "//table[@class='table b-table-index table-selectable-row table-status']/tbody/tr/td[2]/text()").extract()
        titles = response.xpath(
            "//table[@class='table b-table-index table-selectable-row table-status']/tbody/tr/td[3]/text()").extract()
        addressys = response.xpath(
            "//table[@class='table b-table-index table-selectable-row table-status']/tbody/tr/td[4]/text()").extract()
        links = response.xpath(
            "//table[@class='table b-table-index table-selectable-row table-status']/tbody/tr/@rel").extract()
        for i in range(len(statuses)):
            company = sro_reestr_nopriz_ru()
            company['status'] = 'ИСКЛЮЧЕНА' if statuses[i] == 'СРО исключена' else "ЯВЛЯЕТСЯ ЧЛЕНОМ"
            company['reg_number'] = reg_nums[i]
            company['title'] = titles[i]
            company['address'] = addressys[i]
            yield Request(url=self.start_urls[0] + links[i],
                          callback=self.parse_main_info,
                          cb_kwargs={'company': company})

        next = response.xpath("//ul[@class='pagination']/li/a[text()='>']/@href").get()
        if next:
            yield Request(url=self.start_urls[0] + next,
                          callback=self.parse)


    def parse_main_info(self, response, company):
        company['url'] = response.url
        company['inn'] = response.xpath("//table[@class='table b-table-sro']//tr[2]/td[2]/text()").get()
        company['ogrn'] = response.xpath("//table[@class='table b-table-sro']//tr[3]/td[2]/text()").get()
        company['telephone'] = response.xpath("//table[@class='table b-table-sro']//tr[5]/td[2]/text()").get()
        company['email'] = response.xpath("//div[@class='col-xs-5 col-xs-offset-1']/table[@class='table b-table-sro']//tr[1]/td[2]/a/text()").get()
        company['web_site'] = response.xpath("//div[@class='col-xs-5 col-xs-offset-1']/table[@class='table b-table-sro']//tr[2]/td[2]/a/text()").get()
        yield company









