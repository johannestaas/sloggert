'''
sloggert.level
==============

Log levels
'''
from enum import Enum


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

    @classmethod
    def from_int(cls, n):
        try:
            return REVERSE_MAP[n]
        except KeyError:
            raise LogLevelError('Log level {!r} does not exist.'.format(n))


LEVEL_MAP = {
    'debug': Level.DEBUG,
    'info': Level.INFO,
    'warning': Level.WARNING,
    'error': Level.ERROR,
    'critical': Level.CRITICAL,
}

REVERSE_MAP = {
    10: 'debug',
    20: 'info',
    30: 'warning',
    40: 'error',
    50: 'critical',
}
