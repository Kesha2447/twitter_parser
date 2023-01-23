# -*- coding: utf-8 -*-

from starlette.config import Config

config = Config('.env')

PROXY = config('PROXY', default='', cast=str)
WAITING_LIMIT = config('WAITING_LIMIT', cast=float) #sec

BEARED = config('BEARED', cast=str)