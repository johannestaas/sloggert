'''
sloggert.logger
===============

Database and models for log messages.
'''
import socket
from enum import Enum
from datetime import datetime
import pymongo


__all__ = ('Logger', 'Level')


class Level(Enum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class Logger:
    CLIENT = None
    DBS = {}

    def __init__(self, name, hostname=None, host='127.0.0.1', port=27017):
        self.name = name
        self.hostname = hostname or socket.gethostname()
        if Logger.CLIENT is None:
            client_str = 'mongodb://{host}:{port}/'.format(host=host, port=port)
            Logger.CLIENT = pymongo.MongoClient(client_str)
        if not Logger.DBS.get(name):
            db_name = 'sloggert_{name}'.format(name=name)
            Logger.DBS[name] = Logger.CLIENT[db_name]
        self.db = Logger.DBS[name]
        if 'messages' not in self.db.collection_names():
            self._init_message_collection()
        self.coll = self.db.messages

    def _init_message_collection(self):
        self.db.messages.create_index([
            ('_day_', pymongo.DESCENDING),
            ('_level_', pymongo.DESCENDING),
            ('_tags_', pymongo.ASCENDING),
        ])

    def _log(self, level_num, tags, **kwargs):
        dt = datetime.now()
        day = dt.date()
        kwargs.update({
            '_day_': day.isoformat(),
            '_datetime_': dt,
            '_level_': level_num,
            '_tags_': tags,
            '_host_': self.hostname,
        })

    def debug(self, tags=None, **kwargs):
        self._log(Level.DEBUG.value, tags or [], **kwargs)

    def info(self, tags=None, **kwargs):
        self._log(Level.INFO.value, tags or [], **kwargs)

    def warning(self, tags=None, **kwargs):
        self._log(Level.WARNING.value, tags or [], **kwargs)

    def error(self, tags=None, **kwargs):
        self._log(Level.ERROR.value, tags or [], **kwargs)

    def critical(self, tags=None, **kwargs):
        self._log(Level.CRITICAL.value, tags or [], **kwargs)
