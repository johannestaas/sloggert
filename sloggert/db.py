'''
sloggert.db
===========

Abstract class to handle mongo db and collection logic
'''
import socket
import pymongo
from .level import Level
from .util import make_daystr, make_hourstr


class MessageDB:
    CLIENT = None
    DBS = {}

    def __init__(self, name, host='127.0.0.1', port=27017, hostname=None,
                 **kwargs):
        self.name = name
        self.hostname = hostname or socket.gethostname()
        if MongoMixin.CLIENT is None:
            client_str = 'mongodb://{host}:{port}/'.format(host=host, port=port)
            MongoMixin.CLIENT = pymongo.MongoClient(client_str)
        if not MongoMixin.DBS.get(name):
            db_name = 'sloggert_{name}'.format(name=name)
            MongoMixin.DBS[name] = MongoMixin.CLIENT[db_name]
        self.db = MongoMixin.DBS[name]
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
            query['_day_'] = make_daystr(day)
        if hour is not None:
            query['_hour_'] = make_hourstr(hour)
        return self.coll.find(query)

    def get_day(self, day):
        daystr = make_daystr(day)
        return self.coll.find({'_day_': daystr})

    def get_hour(self, hour):
        hourstr = make_hourstr(hour)
        return self.coll.find({'_hour_': hourstr})
