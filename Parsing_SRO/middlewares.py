# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from Parsing_SRO.utils_.db_proxy import DB_proxy
from scrapy import signals


class ParsingSroSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        print('process_spider_output' + str(response.status))

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        print('process_spider_exception')
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ParsingSroDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    proxy_list = None
    current_proxy = None

    def __init__(self):
        with DB_proxy() as db:
            self.proxy_list = db.get_all_proxy()
            print()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        request.meta['proxy'] = self.current_proxy
        request.meta['dont_redirect'] = True
        request.meta['download_timeout'] = 2
        print('proxy')
        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader
        print(response.status)
        if response.status != 200:
            print('proxy is changed 2')
            self.proxy_list.append(self.current_proxy)
            self.current_proxy = self.proxy_list.pop(0)
            request.meta['proxy'] = self.current_proxy
            request.meta['dont_redirect'] = True
            request.meta['download_timeout'] = 2
            return request
        else:
        # # Must either;
            return response
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.
        print('proxy is changed')
        self.proxy_list.append(self.current_proxy)
        self.current_proxy = self.proxy_list.pop(0)
        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        return request

    def spider_opened(self, spider):
        self.current_proxy = self.proxy_list.pop(0)
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware(object):
    __proxy_current = set()     # Проки, использующиеся для ротации
    __proxy_active = set()      # Прокси, задействованные в подлючениях
    __current_index = -1        # Курсор последнего взятого прокси из общего списка
    __proxy_all = None          # Общий список прокси

    def __init__(self):
        with DB_proxy() as db:
            self.__proxy_all = db.get_all_proxy()

    def process_request(self, request, spider):
        proxy = self.__get_and_activate_proxy()
        print("request", proxy)
        self.__set_proxy_to_request(request, proxy)
        return None

    def process_response(self, request, response, spider):
        proxy = self.__get_proxy_from_request(request)
        print("response", proxy)
        self.__deactivate_proxy(proxy)
        if response.status // 100 != 2:
            return request
        return response

    def process_exception(self, request, exception, spider):
        proxy = self.__get_proxy_from_request(request)
        print("exception", proxy)
        self.__deactivate_proxy(proxy)
        self.__shift_proxy(proxy)
        return request

    def __get_next_proxy(self):
        while True:
            self.__current_index += 1
            if self.__current_index >= len(self.__proxy_all):
                self.__current_index = 0
            proxy = self.__proxy_all[self.__current_index]
            if proxy not in self.__proxy_current:
                return proxy

    def __get_and_activate_proxy(self):
        inactive = self.__proxy_current - self.__proxy_active
        if len(inactive) == 0:
            proxy = self.__get_next_proxy()
            self.__proxy_current.add(proxy)
        else:
            proxy = inactive.pop()
        self.__proxy_active.add(proxy)
        print("activate", proxy)
        print("active", len(self.__proxy_active), self.__proxy_active)
        return proxy

    def __deactivate_proxy(self, proxy):
        self.__proxy_active.remove(proxy)
        print("deactivate", proxy)

    def __shift_proxy(self, proxy):
        self.__proxy_current.remove(proxy)
        print("shift", proxy)

    @staticmethod
    def __get_proxy_from_request(request):
        return request.meta['proxy']

    @staticmethod
    def __set_proxy_to_request(request, proxy):
        request.meta['proxy'] = proxy
        request.meta['dont_retry'] = True
        request.meta['dont_redirect'] = True

