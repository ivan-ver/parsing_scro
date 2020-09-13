# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from Parsing_SRO.utils_.db_company import Database


class ParsingSroPipeline(object):
    companies = set()
    flush_count = 60
    all_urls = None

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        with Database() as db:
            db.save_items(self.companies)

    def process_item(self, item, spider):
        self.companies.add(item)
        if len(self.companies) == self.flush_count:
            with Database() as db:
                db.save_items(self.companies)
            self.companies.clear()
        return item
