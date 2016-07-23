'''
sloggert

serialized logger with alerting
'''
import re
from .db import Field
from .logger import Logger
from .alert import Alerter
from .level import Level

__title__ = 'sloggert'
__version__ = '0.0.1'
__all__ = ('Logger', 'Alerter', 'Field', 'Level')
__author__ = 'Johan Nestaas <johannestaas@gmail.com>'
__license__ = 'GPLv3+'
__copyright__ = 'Copyright 2016 Johan Nestaas'


def main():
    import sys
    import json
    re_kwarg = re.compile(r'--([\w_-]+)([=\s]*)(\S*)')
    name = sys.argv[1]
    kwargs = {}
    sys_kwargs = re_kwarg.findall(' '.join(sys.argv))
    for kwarg, _, val in sys_kwargs:
        if val.isdigit():
            val = int(val)
        kwargs[kwarg.replace('-', '_')] = val
    log = Logger(name)
    for msg in log.find(**kwargs):
        msg['_id'] = str(msg['_id'])
        msg['_datetime_'] = msg['_datetime_'].isoformat()
        print(json.dumps(msg))
