'''
sloggert.util
=============

Simple utilities for date logic, etc.
'''
from datetime import datetime, date, timedelta


def make_daystr(day):
    if isinstance(day, date):
        return day.isoformat()
    elif isinstance(day, datetime):
        return day.isoformat()[:10]
    elif isinstance(day, timedelta):
        return (date.today() - day).isoformat()
    elif day in ('today', 'now'):
        return date.today().isoformat()
    elif day == 'yesterday':
        return (date.today() - timedelta(days=1)).isoformat()
    else:
        return day


def make_hourstr(hour):
    if isinstance(hour, datetime):
        return hour.isoformat()[:13]
    elif isinstance(hour, timedelta):
        return (datetime.now() - hour).isoformat()[:13]
    elif hour == 'now':
        return datetime.now().isoformat()[:13]
    else:
        return hour.replace(' ', 'T')


def make_datetime(val):
    if isinstance(val, datetime):
        return val
    elif isinstance(val, timedelta):
        return datetime.now() - val
    elif val == 'now':
        return datetime.now()
    elif val == 'today':
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        val = val.replace(' ', 'T')
        val = val.replace('/', '-')
        if len(val) == 4:
            return datetime.strptime(val, '%Y')
        elif len(val) == 7:
            return datetime.strptime(val, '%Y-%m')
        elif len(val) == 10:
            return datetime.strptime(val, '%Y-%m-%d')
        elif len(val) == 13:
            return datetime.strptime(val, '%Y-%m-%dT%H')
        elif len(val) == 16:
            return datetime.strptime(val, '%Y-%m-%dT%H:%M')
        elif len(val) == 19:
            return datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
        elif len(val) > 19:
            return datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            return datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
