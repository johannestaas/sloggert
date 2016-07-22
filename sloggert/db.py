'''
sloggert.db
===========

Abstract class to handle mongo db and collection logic
'''
import socket
import pymongo
from .level import Level
from .util import make_daystr, make_hourstr, make_datetime


class MessageDB:
    CLIENT = None
    DBS = {}

    def __init__(self, name, host='127.0.0.1', port=27017, hostname=None,
                 **kwargs):
        self.name = name
        self.hostname = hostname or socket.gethostname()
        if MessageDB.CLIENT is None:
            client_str = 'mongodb://{host}:{port}/'.format(host=host, port=port)
            MessageDB.CLIENT = pymongo.MongoClient(client_str)
        if not MessageDB.DBS.get(name):
            db_name = 'sloggert_{name}'.format(name=name)
            MessageDB.DBS[name] = MessageDB.CLIENT[db_name]
        self.db = MessageDB.DBS[name]
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
        return self.coll.find(query).sort('_datetime_', 1)

    def select(self, field):
        return self.coll.find(field.build_query()).sort('_datetime_', 1)

    def get_day(self, day):
        daystr = make_daystr(day)
        return self.coll.find({'_day_': daystr}).sort('_datetime_', 1)

    def get_hour(self, hour):
        hourstr = make_hourstr(hour)
        return self.coll.find({'_hour_': hourstr}).sort('_datetime_', 1)


class DeltaValue:

    def __init__(self, value, converter):
        self.converter = converter
        self.value = value

    def __call__(self):
        return self.converter(self.value)


class Field:

    def remap(self, field):
        if field == 'level':
            self._converter = Level.from_str
            return '_level_'
        elif field == 'day':
            self._converter = make_daystr
            return '_day_'
        elif field == 'hour':
            self._converter = make_hourstr
            return '_hour_'
        elif field == 'datetime':
            self._converter = make_datetime
            return '_datetime_'
        elif field == 'msg':
            return '_msg_'
        elif field == 'hostname':
            return '_host_'
        elif field in ('tag', 'tags'):
            return '_tags_'
        else:
            return field

    def __init__(self, field):
        self.field = field
        self._converter = None
        self._field = self.remap(field)
        self._query = None
        self._has_delta = False

    def __eq__(self, other):
        if self._converter is not None:
            other = DeltaValue(other, self._converter)
            self._has_delta = True
        self._query = {self._field: other}
        return self

    def _op(self, other, op):
        if self._query:
            raise ValueError('Comparison already used for {s.field}, please '
                             'use | (OR) or & (AND) for additional logic')
        if self._converter is not None:
            other = DeltaValue(other, self._converter)
            self._has_delta = True
        self._query = {self._field: {op: other}}
        return self

    def __gt__(self, other):
        return self._op(other, '$gt')

    def __lt__(self, other):
        return self._op(other, '$lt')

    def __ne__(self, other):
        return self._op(other, '$ne')

    def __ge__(self, other):
        return self._op(other, '$gte')

    def __le__(self, other):
        return self._op(other, '$lte')

    def __or__(self, other):
        if not (self._query and other._query):
            raise ValueError('Cannot OR together fields without comparisons. '
                             'eg: use (Field("foo") == True) | (Field("bar") '
                             '== 5)\ndont use (Field("foo") | Field("bar"))')
        self._query = {'$or': [self._query, other._query]}
        self._converter = None
        return self

    def __and__(self, other):
        if not (self._query and other._query):
            raise ValueError('Cannot AND together fields without comparisons. '
                             'eg: use (Field("foo") == True) | (Field("bar") '
                             '== 5)\ndont use (Field("foo") | Field("bar"))')
        self._query = {'$and': [self._query, other._query]}
        self._converter = None
        return self

    def _recurse_deltas(self, query):
        if isinstance(query, dict):
            d = {}
            for k, v in query.items():
                d[k] = self._recurse_deltas(v)
            return d
        elif isinstance(query, list):
            new = []
            for i in query:
                new.append(self._recurse_deltas(i))
            return new
        elif isinstance(query, DeltaValue):
            return query()
        else:
            return query

    def build_query(self):
        if self._query:
            if not self._has_delta:
                return self._query
            return self._recurse_deltas(self._query)
        else:
            return self._field
