import configparser

import pymysql


# noinspection SqlNoDataSourceInspection,SqlResolve
class Database:
    _connection = None
    _cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _get_conn(self):
        config = configparser.ConfigParser()
        config.read('config/proxy_db.cfg')
        if 'db_conn' not in config:
            print('db config error')  # TODO correct handling
            exit(1)
        props = dict(config.items('db_conn'))
        return pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **props)

    def connect(self):
        if self._connection is None:
            self._connection = self._get_conn()
            self._cursor = self._connection.cursor()
            print('connected')

    def disconnect(self):
        if self._connection is not None:
            self._connection.commit()
            self._connection.close()
            print('disconnected')

    def get_dict(self, item):
        res = dict()
        res['url'] = item['url']
        res['sro'] = item['sro']
        res['short_title'] = item['short_title']
        res['status'] = item['status']
        res['reg_date'] = item['reg_date']
        res['inn'] = item['inn']
        res['ogrn'] = item['ogrn']
        res['address'] = item['address']
        res['fio'] = item['fio']
        res['end_insurance_date'] = item['end_insurance_date']
        res['insurance_amount'] = item['insurance_amount']
        res['insurance_company_title'] = item['insurance_company_title']
        return res

    def save_items(self, items):
        for item in items:
            item_dict = self.get_dict(item)
            item_dict = dict((k, v) for k, v in item_dict.items() if v!=None)
            _columns = ', '.join(item_dict.keys())
            values = ", ".join("'{}'".format(k) for k in item_dict.values())
            sql = "INSERT INTO parsing.reestr_nostroy_ru ({}) VALUES ({})".format(_columns, values)
            self._cursor.execute(sql)
        self._connection.commit()
