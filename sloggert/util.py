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
        return date.now().isoformat()[:13]
    else:
        return hour.replace(' ', 'T')
