'''计时器
计时器功能'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from time import time
from typing import Any
from AnonChihayaBot.adapters.Satori import Bot, Event
from AnonChihayaBot.adapters import plugin_register, schedule_register

# 计时器列表
timers: list[dict[str, Any]] = []
'''计时器列表'''

# 创建计时器功能
@plugin_register(name='创建计时器', desc='创建一个计时器', command='/timer ')
def timer(bot: Bot, event: Event) -> None:
    '''创建一个计时器，将每隔五秒发送一条消息（仅供测试使用）
    /timer <id> -> 创建一个拥有指定 id 的计时器
    '''
    global timers
    if event.get_message().is_text():
        timers.append(
            {
                'id': event.get_message().extract_plain_text().strip(),
                'guild': event.get_guild_id(),
                'nowstime': int(time())
            }
        )
        bot.send(event, f'已添加计时器 {timers[-1]["id"]}')
    return

# 停止计时器功能
@plugin_register(name='停止计时器', desc='停止一个计时器', command='/stoptimer ')
def stoptimer(bot: Bot, event: Event) -> None:
    '''停止一个计时器，将不再发送消息（仅供测试使用）
    /stoptimer <id> -> 停止一个拥有指定 id 的计时器
    '''
    global timers
    if event.get_message().is_text():
        for timer in timers:
            if timer['id'] == event.get_message().extract_plain_text().strip():
                timers.remove(timer)
                bot.send(event, f'已停止计时器 {timer["id"]}')
                break
    return

# 执行计时器功能
@schedule_register('interval', id='timer_run', max_instance=1, second=1)
def timer_run(bot: Bot) -> None:
    '''执行计时器'''
    nowstime = int(time())
    for timer in timers:
        if nowstime - timer['nowstime'] >= 5:
            timer['nowstime'] = nowstime
            bot.message_create(timer['guild'], '[计时器消息]')
    return
