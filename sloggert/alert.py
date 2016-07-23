'''
sloggert.alert
==============

Handles alerting logic and aggregation from rules.
'''
import json
from .db import MessageDB
from .level import Level
from pymongo.cursor import Cursor


def json_dumps(result):
    return json.dumps(result)


class Selection:

    def __init__(self, field, processor, **kwargs):
        self.kwargs = kwargs
        self.field = field
        self.processor = _processor_decorator(processor)


def _rewrite_del(result, orig, new):
    if orig in result:
        result[new] = result[orig]
    del result[orig]


def _processor_decorator(func):
    def new_func(result):
        if '_id' in result:
            result['id'] = str(result['_id'])
            del result['_id']
        if '_datetime_' in result:
            result['datetime'] = result['_datetime_'].isoformat()
            del result['_datetime_']
        if '_level_' in result:
            result['level'] = Level.from_int(result['_level_'])
            del result['_level_']
        _rewrite_del(result, '_msg_', 'msg')
        _rewrite_del(result, '_day_', 'day')
        _rewrite_del(result, '_hour_', 'hour')
        _rewrite_del(result, '_host_', 'hostname')
        _rewrite_del(result, '_tags_', 'tags')
        return func(result)
    return new_func


class Alerter(MessageDB):

    def __init__(self, *args, **kwargs):
        super(Alerter, self).__init__(*args, **kwargs)
        self.selections = {}

    def add(self, name, field, processor=None, **kwargs):
        if processor is None:
            processor = json_dumps
        elif isinstance(processor, str):
            format_str = processor

            def processor_func(result):
                return format_str.format(**result)

            processor = processor_func
        self.selections[name] = Selection(field, processor, **kwargs)

    def run_all(self):
        messages = {}
        for name, sel in self.selections.items():
            messages[name] = self.select(sel.field, **sel.kwargs)
        return messages

    def run(self, name):
        sel = self.selections[name]
        return self.select(sel.field, **sel.kwargs)

    def process(self, name):
        sel = self.selections[name]
        results = self.run(name=name)
        if isinstance(results, Cursor):
            for msg in results:
                yield sel.processor(msg)
        else:
            yield sel.processor(results)

    def process_all(self):
        for name in self.selections:
            for processed in self.process(name):
                yield processed

    def print(self, name):
        for processed in self.process(name):
            print(processed)

    def print_all(self):
        for processed in self.process_all():
            print(processed)
