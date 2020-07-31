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
    proxy_list = [
        'http://95.38.14.16:8080',
        'http://105.27.238.166:80',
        'http://105.27.237.25:80',
        'http://60.51.170.27:80',
        'http://196.27.119.131:80',
        'http://54.38.218.213:6582',
        'http://82.81.169.142:80',
        'http://91.67.240.45:3128',
        'http://139.5.71.70:23500',
        'http://185.222.59.86:5836',
        'http://200.85.169.18:47548',
        'http://175.139.179.65:42580',
        'http://41.190.95.20:56167',
        'http://41.190.95.20:56167',
        'http://208.96.137.130:47744',
        'http://41.190.92.84:48515',
        'http://41.75.123.29:59922',
        'http://41.217.219.49:40310',
        'http://41.75.123.49:41263',
        'http://77.28.97.78:50359',
        'http://104.244.75.218:8080',
        'http://165.98.53.38:35332',
        'http://211.24.105.19:47615',
        'http://85.147.153.34:80',
        'http://41.190.147.158:54018',
        'http://103.81.114.182:53281',
        'http://124.158.88.56:54555',
        'http://202.131.234.142:39330',
        'http://43.228.131.115:59874',
        'http://202.166.216.249:23500',
        'http://202.179.21.49:23500',
        'http://37.26.136.181:52271',
        'http://93.117.72.27:43631',
        'http://124.41.240.126:31984',
        'http://95.65.73.200:38956',
        'http://197.231.186.148:45578',
        'http://41.72.203.66:38057',
        'http://82.135.148.201:8081',
        'http://78.60.203.75:47385',
        'http://154.73.109.129:53281',
        'http://13.230.39.33:60088',
        'http://109.73.188.225:23500',
        'http://192.117.146.110:80',
        'http://217.219.31.210:38073'
    ]

    current_proxy = None

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
        # Called with the response returned from the downloader.

        # # Must either;
        return response
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.
        print('proxy is change')
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

