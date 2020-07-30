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

    @staticmethod
    def __clean_dict(item_dict):
        dict((k, ','.join(v)) for k, v in item_dict.items() if isinstance(v, (list, set)))
        return dict((k, v) for k, v in item_dict.items() if v)

    def save_items(self, items):
        for item in items:
            try:
                table_name = item.__class__.__name__
                item_dict = ItemAdapter(item).asdict()
                item_dict = self.__clean_dict(item_dict)
                _columns = ', '.join(item_dict.keys())
                values = ", ".join("'{}'".format(k) for k in item_dict.values())
                sql = "INSERT INTO parsing.{} ({}) VALUES ({})".format(table_name, _columns, values)
                self._cursor.execute(sql)
            except pymysql.err.DataError:
                logging.info("DataError_URL " + str(item['url']))
        self._connection.commit()


