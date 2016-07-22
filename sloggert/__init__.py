'''
sloggert

serialized logger with alerting
'''
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
