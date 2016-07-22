'''
sloggert.alert
==============

Handles alerting logic and aggregation from rules.
'''
import json
from .db import MessageDB


class Alerter(MessageDB):

    def __init__(self, **kwargs):
        super(Alerter, self).__init__(**kwargs)
        self.selections = {}
        self._select = self.select

    def add_selection(self, name, field):
        self.selections[name] = field

    def select(self, name=None):
        if name is not None:
            return self._select(self.selections[name].build_query())
        else:
            messages = {}
            for name, field in self.selections.items():
                messages[name] = self._select(field.build_query())
            return messages

    def print(self, name=None):
        if name is None:
            for name in self.selections:
                print('=== {} ==='.format(name))
                for msg in self.select(name=name):
                    print('  {}'.format(json.dumps(msg)))
        else:
            for msg in self.select(name=name):
                print(json.dumps(msg))
