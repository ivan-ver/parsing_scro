import configparser
import pymysql
from pymysql.cursors import DictCursor
# noinspection SqlNoDataSourceInspection,SqlResolve


class DB_proxy():
    _connection = None
    _cursor = None
    protocols = {
        1: 'http://',
        2: 'https://',
        0: 'http://'
    }

    def __init__(self):
        self.connect()

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

    def get_all_proxy(self):
        self._cursor.execute("""
            SELECT type, host, port FROM `proxy`.`proxy_checked` WHERE type < 3
        """)
        df = self._cursor.fetchall()
        return [self.protocols[i['type']] + i['host'] + ':' + str(i['port']) for i in df]
