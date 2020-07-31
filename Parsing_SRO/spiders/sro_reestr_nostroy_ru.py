# -*- coding: utf-8 -*-
import scrapy
import scrapy
from scrapy import Request
from Parsing_SRO.items import sro_reestr_nostroy_ru


class SroReestrNostroyRuSpider(scrapy.Spider):
    name = 'sro_reestr_nostroy_ru'
    start_urls = ['http://reestr.nostroy.ru']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url,
                          callback=self.parse,
                          dont_filter=True)

    def parse(self, response):
        for row in response.xpath("//table/tbody/tr"):
            company = sro_reestr_nostroy_ru()
            company['reg_number'] = row.xpath('td[1]/text()').get()
            company['title'] = row.xpath('td[2]/text()').get()
            company['address'] = row.xpath('td[3]/text()').get()
            company['status'] = row.xpath('td[6]/span/text()').get().strip()
            link = row.xpath('@rel').get()
            yield Request(url=self.start_urls[0] + link,
                          callback=self.parse_main_info,
                          cb_kwargs={'company': company},
                          dont_filter=True)

        next_ = response.xpath("//ul[@class='pagination']/li/a[text()='>']/@href").get()
        if next_:
            yield Request(url=self.start_urls[0] + next_,
                          callback=self.parse,
                          dont_filter=True)

    def parse_main_info(self, response, company):
        company['url'] = response.url
        company['ogrn'] = response.xpath("//div[@class='col-md-9 block-content-open-client-data-wrapper']"
                                         "/div[5]/div[2]/text()").get()
        company['inn'] = response.xpath("//div[@class='col-md-9 block-content-open-client-data-wrapper']"
                                        "/div[6]/div[2]/text()").get()
        company['telephone'] = response.xpath("//div[@class='col-md-9 block-content-open-client-data-wrapper']"
                                              "/div[8]/div[2]/text()").get()
        company['email'] = response.xpath("//div[@class='col-md-9 block-content-open-client-data-wrapper']"
                                          "/div[9]/div[2]/text()").get()
        company['email'] = response.xpath("//div[@class='col-md-9 block-content-open-client-data-wrapper']"
                                          "/div[9]/div[2]/a/text()").get()
        company['web_site'] = response.xpath("//div[@class='col-md-9 block-content-open-client-data-wrapper']"
                                             "/div[10]/div[2]/a/text()").get()
        yield company

