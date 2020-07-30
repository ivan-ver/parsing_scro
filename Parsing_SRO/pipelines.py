# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from Parsing_SRO.utils_.db_company import Database


class ParsingSroPipeline(object):
    companies = set()
    flush_count = 10
    db = Database()

    def open_spider(self, spider):
        self.db.connect()

    def close_spider(self, spider):
        self.db.save_items(self.companies)
        self.db.disconnect()

    def process_item(self, item, spider):
        self.companies.add(item)
        if len(self.companies) == self.flush_count:
            self.db.save_items(self.companies)
            self.companies.clear()
        return item
