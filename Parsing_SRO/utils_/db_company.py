import configparser
from itemadapter import ItemAdapter
import pymysql
import logging


# noinspection SqlNoDataSourceInspection,SqlResolve
class Database:
    _connection = None
    _cursor = None
    logging.basicConfig(filename='dblog.log',
                        level=logging.INFO)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _get_conn(self):
        config = configparser.ConfigParser()
        config.read('config/sro_db.cfg')
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

    @staticmethod
    def __clean_dict(item_dict):
        dict((k, ','.join(v)) for k, v in item_dict.items() if isinstance(v, (list, set)))
        return dict((k, v) for k, v in item_dict.items() if v)

    @staticmethod
    def __check_size(item_dict):
        for key, value in item_dict.items():
            if len(str(value)) > 255:
                print()
                item_dict[key] = value[0:250]
        return item_dict

    def save_items(self, items):
        for item in items:
            table_name = item.__class__.__name__
            item_dict = ItemAdapter(item).asdict()
            item_dict = self.__check_size(item_dict)
            item_dict = self.__clean_dict(item_dict)
            try:
                _columns = ', '.join(item_dict.keys())
                updated_values = ', '.join(i[0]+"='" + i[1]+"'" for i in item_dict.items() if i[0] != 'url')
                values = ", ".join("'{}'".format(k) for k in item_dict.values())
                sql = "INSERT INTO sro.{} ({}) VALUES ({})".format(
                    table_name,
                    _columns,
                    values)
                self._cursor.execute(sql)
                print(sql)
            except:
                url = item_dict.pop('url')
                _columns = ', '.join(item_dict.keys())
                set_str = ", ".join("{}=%s".format(k) for k in item_dict.keys())
                sql = "UPDATE sro.{} SET {} WHERE url = '{}'".format(table_name, set_str, url)
                self._cursor.execute(sql, list(item_dict.values()))
                print(sql)
        self._connection.commit()

    def get_all_urls(self, table_name):
        req = """SELECT url FROM sro.{}""".format(table_name)
        self._cursor.execute(req)
        return [url['url'] for url in self._cursor.fetchall()]

