'''
sloggert.alert
==============

Handles alerting logic and aggregation from rules.
'''
import json
from .db import MessageDB
from pymongo.cursor import Cursor


class Selection:

    def __init__(self, field, **kwargs):
        self.kwargs = kwargs
        self.field = field


class Alerter(MessageDB):

    def __init__(self, *args, **kwargs):
        super(Alerter, self).__init__(*args, **kwargs)
        self.selections = {}

    def add_selection(self, name, field, **kwargs):
        self.selections[name] = Selection(field, **kwargs)

    def query(self, name=None):
        if name is not None:
            sel = self.selections[name]
            return self.select(sel.field, **sel.kwargs)
        else:
            messages = {}
            for name, sel in self.selections.items():
                messages[name] = self.select(sel.field, **sel.kwargs)
            return messages

    def print(self, name=None):
        if name is None:
            for name in self.selections:
                print('=== {} ==='.format(name))
                query = self.query(name=name)
                if isinstance(query, Cursor):
                    for msg in query:
                        msg['_id'] = str(msg['_id'])
                        msg['_datetime_'] = msg['_datetime_'].isoformat()
                        print(json.dumps(msg))
                else:
                    print(query)
        else:
            query = self.query(name=name)
            if isinstance(query, Cursor):
                for msg in query:
                    msg['_id'] = str(msg['_id'])
                    msg['_datetime_'] = msg['_datetime_'].isoformat()
                    print(json.dumps(msg))
            else:
                print(query)
