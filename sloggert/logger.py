'''
sloggert.logger
===============

Database and models for log messages.
'''
import socket
from enum import Enum
from datetime import datetime, date
import pymongo


__all__ = ('Logger', 'Level')


class LogLevelError(ValueError):
    pass


class Level(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    @classmethod
    def from_str(cls, s):
        try:
            return LEVEL_MAP[s]
        except KeyError:
            raise LogLevelError('Log level {!r} does not exist. '
                                'Please use one of "debug", "info", "warning", '
                                '"error", or "critical".'.format(s))


LEVEL_MAP = {
    'debug': Level.DEBUG,
    'info': Level.INFO,
    'warning': Level.WARNING,
    'error': Level.ERROR,
    'critical': Level.CRITICAL,
}


class Logger:
    CLIENT = None
    DBS = {}

    def __init__(self, name, host='127.0.0.1', port=27017, hostname=None):
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
            ('_hour_', pymongo.DESCENDING),
            ('_level_', pymongo.DESCENDING),
            ('_tags_', pymongo.ASCENDING),
        ])

    def _log(self, args, level_num, tags, **kwargs):
        dt = datetime.now()
        day = dt.date()
        kwargs.update({
            '_day_': day.isoformat(),
            '_hour_': dt.isoformat()[:13],
            '_datetime_': dt,
            '_level_': level_num,
            '_tags_': tags,
            '_host_': self.hostname,
        })
        if args:
            kwargs['_msg_'] = args[0]
        self.coll.insert_one(kwargs)

    def _make_daystr(self, day):
        if isinstance(day, date):
            return day.isoformat()
        elif isinstance(day, datetime):
            return day.isoformat()[:10]
        else:
            return day

    def _make_hourstr(self, hour):
        if isinstance(hour, datetime):
            return hour.isoformat()[:13]
        else:
            return hour.replace(' ', 'T')

    def debug(self, *args, tags=None, **kwargs):
        self._log(args, Level.DEBUG.value, tags or [], **kwargs)

    def info(self, *args, tags=None, **kwargs):
        self._log(args, Level.INFO.value, tags or [], **kwargs)

    def warning(self, *args, tags=None, **kwargs):
        self._log(args, Level.WARNING.value, tags or [], **kwargs)

    def error(self, *args, tags=None, **kwargs):
        self._log(args, Level.ERROR.value, tags or [], **kwargs)

    def critical(self, *args, tags=None, **kwargs):
        self._log(args, Level.CRITICAL.value, tags or [], **kwargs)

    def get_day(self, day):
        daystr = self._make_daystr(day)
        return self.coll.find({'_day_': daystr})

    def get_hour(self, hour):
        hourstr = self._make_hourstr(hour)
        return self.coll.find({'_hour_': hourstr})

    def find(self, level=None, hostname=None, tag=None, day=None, hour=None,
             **kwargs):
        query = kwargs
        if level is not None:
            query['_level_'] = Level.from_str(level)
        if hostname is not None:
            query['_host'] = hostname
        if tag is not None:
            query['_tags_'] = tag
        if day is not None:
            query['_day_'] = self._make_daystr(day)
        if hour is not None:
            query['_hour_'] = self._make_hourstr(hour)
        return self.coll.find(query)
