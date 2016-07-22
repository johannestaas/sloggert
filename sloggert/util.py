'''
sloggert.util
=============

Simple utilities for date logic, etc.
'''
from datetime import datetime, date


def make_daystr(day):
    if isinstance(day, date):
        return day.isoformat()
    elif isinstance(day, datetime):
        return day.isoformat()[:10]
    else:
        return day


def make_hourstr(hour):
    if isinstance(hour, datetime):
        return hour.isoformat()[:13]
    else:
        return hour.replace(' ', 'T')
