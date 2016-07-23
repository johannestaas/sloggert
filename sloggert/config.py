'''
sloggert.config
===============

Configuration management
'''
from confutil import Config

CONF = Config('sloggert')


def load_config(path):
    CONF.read(path)
