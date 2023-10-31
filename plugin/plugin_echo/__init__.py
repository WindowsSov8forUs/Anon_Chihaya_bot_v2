'''回声
重复所发送的内容'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from AnonChihayaBot.adapters import plugin_register
from AnonChihayaBot.adapters.Satori import Bot, Event

# 回声功能
@plugin_register(name='echo', desc='重复所发送的内容。', command='/echo ')
def echo(bot: Bot, event: Event) -> None:
    '''重复所发送的内容
    /echo <内容>
    '''
    bot.send(event, event.get_message())
    return