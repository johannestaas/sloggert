'''
sloggert.alert
==============

Handles alerting logic and aggregation from rules.
'''
from .db import MessageDB
from .util import make_daystr, make_hourstr, make_datetime
from .level import Level


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
            raise ValueError('Please specify comparison to query with first.')


class Alert(MessageDB):
    pass
