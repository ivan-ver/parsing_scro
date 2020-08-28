from Parsing_SRO.utils_.db_proxy import DB_proxy


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
        self.__set_proxy_to_request(request, proxy)
        return None

    def process_response(self, request, response, spider):
        proxy = self.__get_proxy_from_request(request)
        self.__deactivate_proxy(proxy)
        if response.status // 100 != 2:
            return request
        return response

    def process_exception(self, request, exception, spider):
        proxy = self.__get_proxy_from_request(request)
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
        return proxy

    def __deactivate_proxy(self, proxy):
        self.__proxy_active.remove(proxy)


    def __shift_proxy(self, proxy):
        self.__proxy_current.remove(proxy)

    @staticmethod
    def __get_proxy_from_request(request):
        return request.meta['proxy']

    @staticmethod
    def __set_proxy_to_request(request, proxy):
        request.meta['proxy'] = proxy
        request.meta['dont_retry'] = True
        request.meta['dont_redirect'] = True

