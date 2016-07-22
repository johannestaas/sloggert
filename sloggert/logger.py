'''
sloggert.logger
===============

Database and models for log messages.
'''
from datetime import datetime
from .db import MessageDB
from .level import Level


__all__ = ('Logger', 'Level')


class Logger(MessageDB):

    def __init__(self, name, host='127.0.0.1', port=27017, hostname=None):
        super(Logger, self).__init__(name, host=host, port=port,
                                     hostname=hostname)

    def _log(self, args, level_num, tags, **kwargs):
        dt = datetime.now()
        day = dt.date()
        kwargs.update({
            '_day_': day.isoformat(),
            '_hour_': dt.isoformat()[:13],
            '_datetime_': dt,
            '_level_': level_num,
            '_tags_': tags,
            '_host_': self.hostname,
        })
        if args:
            kwargs['_msg_'] = args[0]
        self.coll.insert_one(kwargs)

    def debug(self, *args, tags=None, **kwargs):
        self._log(args, Level.DEBUG.value, tags or [], **kwargs)

    def info(self, *args, tags=None, **kwargs):
        self._log(args, Level.INFO.value, tags or [], **kwargs)

    def warning(self, *args, tags=None, **kwargs):
        self._log(args, Level.WARNING.value, tags or [], **kwargs)

    def error(self, *args, tags=None, **kwargs):
        self._log(args, Level.ERROR.value, tags or [], **kwargs)

    def critical(self, *args, tags=None, **kwargs):
        self._log(args, Level.CRITICAL.value, tags or [], **kwargs)
