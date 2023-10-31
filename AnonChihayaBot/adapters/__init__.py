'''Anon Chihaya 框架适配器'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from .bot import Bot as Bot
from .event import Event as Event
from .utils import MyJson as Json
from .config import Config as Config
from .utils import Logging as Logging
from .adapter import Adapter as Adapter
from .message import Message as Message
from .message import MessageSegment as MessageSegment
from .utils import plugin_register as plugin_register
from .utils import schedule_register as schedule_register

logger = Logging()
