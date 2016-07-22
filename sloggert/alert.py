'''
sloggert.alert
==============

Handles alerting logic and aggregation from rules.
'''
import json
from .db import MessageDB


class Alerter(MessageDB):

    def __init__(self, *args, **kwargs):
        super(Alerter, self).__init__(*args, **kwargs)
        self.selections = {}

    def add_selection(self, name, field):
        self.selections[name] = field

    def query(self, name=None):
        if name is not None:
            return self.select(self.selections[name])
        else:
            messages = {}
            for name, field in self.selections.items():
                messages[name] = self.select(field)
            return messages

    def print(self, name=None):
        if name is None:
            for name in self.selections:
                print('=== {} ==='.format(name))
                for msg in self.query(name=name):
                    msg['_id'] = str(msg['_id'])
                    msg['_datetime_'] = msg['_datetime_'].isoformat()
                    print('  {}'.format(json.dumps(msg)))
        else:
            for msg in self.query(name=name):
                msg['_id'] = str(msg['_id'])
                msg['_datetime_'] = msg['_datetime_'].isoformat()
                print(json.dumps(msg))
