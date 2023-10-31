'''Anon Chihaya 框架
内部插件功能
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from typing import TypeVar

from AnonChihayaBot._plugin import plugins
from AnonChihayaBot.adapters import Bot as BaseBot
from AnonChihayaBot.adapters import Event as BaseEvent

from .plugin_admin import Admin
from .plugin_ban_manager import BanManager as Ban

# 创建类型对象
Bot = TypeVar('Bot', bound=BaseBot)
Event = TypeVar('Event', bound=BaseEvent)

# 管理员操作函数 (只会处理 /admin 或 /deadmin 开头且由 host_id 发送消息)
def admin_process(bot: Bot, event: Event) -> None:
    '''管理员操作函数

    参数:
        bot (Bot): 机器人实例
        event (Event): 事件对象
    '''
    # 获取事件消息
    try:
        message = event.get_message()
    except:
        return
    if message[-1].is_text() and message[-1].data['text'].strip() == '':
        del message[-1]
    # 判断消息内容
    if message[0].is_text() and len(message) <= 2:
        # 第一个消息段必须为字符串且只能有小于等于两段
        if str(message).startswith('/admin '):
            message[0].data['text'] = message[0].data['text'][7:].strip()
            if message[0].data['text'] == '':
                del message[0]
            if not message: return
            if len(message) == 1: # 如果只剩一个消息段
                print(message[0])
                if message[0].is_text(): # 如果是字符串
                    if message.extract_plain_text() == 'show': # 如果是列出管理员
                        admin_list = Admin._get_list()
                        if len(admin_list) <= 0: # 如果没有管理员
                            bot.send(event, '<!> Bot 没有管理员。')
                            return
                        else:
                            reply = '<!> 拥有管理员权限的用户有：'
                            for admin in admin_list:
                                reply += f'\n{admin}'
                            bot.send(event, reply)
                            return
                    elif (user_id := message.extract_plain_text()).isdigit(): # 如果是数字表示用户 ID
                        # 添加指定用户为管理员
                        reply = Admin.add(user_id)
                        bot.send(event, reply)
                        return
                elif message[0].type == 'at': # 如果是提及某用户
                    print('yes')
                    user_id = message[0].data['id']
                    if isinstance(user_id, str) and user_id.isdigit(): # 是合法 ID
                        # 添加指定用户为管理员
                        reply = Admin.add(user_id)
                        bot.send(event, reply)
                        return
        elif message.extract_plain_text().startswith('/deadmin '):
            message[0].data['text'] = message[0].data['text'][9:].strip()
            if message[0].data['text'] == '':
                del message[0]
            if not message: return
            if len(message) == 1: # 如果只剩一个消息段
                if message[0].is_text(): # 如果是字符串
                    if (user_id := message.extract_plain_text()).isdigit(): # 如果是数字表示用户 ID
                        # 删除指定用户的管理员
                        reply = Admin.add(user_id)
                        bot.send(event, reply)
                        return
                elif message[0].type == 'at': # 如果是提及某用户
                    user_id = message[0].data['id']
                    if isinstance(user_id, str) and user_id.isdigit(): # 是合法 ID
                        # 添加指定用户为管理员
                        reply = Admin.add(user_id)
                        bot.send(event, reply)
                        return

# 屏蔽操作函数 (只会处理 /ban 或 /unban 开头且由管理员发送消息)
def ban_process(bot: Bot, event: Event) -> None:
    '''屏蔽操作函数

    参数:
        bot (Bot): 机器人实例
        event (Event): 事件对象
    '''
    # 获取事件消息
    try:
        message = event.get_message()
    except:
        return
    if message[-1].is_text() and message[-1].data['text'].strip() == '':
        del message[-1]
    # 判断消息内容
    if message[0].is_text() and len(message) <= 2:
        # 第一个消息段必须为字符串且只能有小于等于两段
        if message.extract_plain_text().startswith('/ban '):
            message[0].data['text'] = message[0].data['text'][5:].strip()
            if message[0].data['text'] == '':
                del message[0]
            if not message: return
            if len(message) == 1: # 如果只剩一个消息段
                if message[0].is_text(): # 如果是字符串
                    if (shows := message.extract_plain_text()).startswith('show'): # 如果是列出屏蔽项
                        if shows[4:].strip() == '':
                            ban_info = Ban._get_info()
                            reply = ''
                            if len(ban_info.platform) > 0: # 有针对平台的屏蔽
                                reply += '\n屏蔽的平台有：\n'
                                reply += '\n'.join(pf for pf in ban_info.platform)
                            if len(ban_info.guild) > 0: # 有针对群组的屏蔽
                                reply += '\n屏蔽的群组有：\n'
                                reply += '\n'.join(gid for gid in ban_info.guild)
                            if len(ban_info.user) > 0: # 有针对用户的屏蔽
                                reply += '\n屏蔽的用户有：\n'
                                reply += '\n'.join(uid for uid in ban_info.user)
                            # 尝试获取群组 ID
                            try:
                                guild_id = event.get_guild_id()
                                if len(ban_info.plugin[guild_id]) > 0:
                                    reply += '\n本群屏蔽的插件有：\n'
                                    reply += '\n'.join(p for p in ban_info.plugin[guild_id])
                            except:
                                pass
                            if len(reply) <= 0:
                                reply = '<!> 当前没有屏蔽设置。'
                            else:
                                reply = '<i> ' + reply.strip()
                            bot.send(event, reply)
                            return
                        else: # 分选项
                            reply = ''
                            ban_info = Ban._get_info()
                            for show_item in shows.split(' '):
                                if show_item in ['u', 'U']: # 用户
                                    if len(ban_info.user) > 0: # 有针对用户的屏蔽
                                        reply += '\n屏蔽的用户有：\n'
                                        reply += '\n'.join(uid for uid in ban_info.user)
                                    else:
                                        reply += '\n当前无屏蔽的用户。\n'
                                elif show_item in ['g', 'G']: # 群组
                                    if len(ban_info.guild) > 0: # 有针对群组的屏蔽
                                        reply += '\n屏蔽的群组有：\n'
                                        reply += '\n'.join(gid for gid in ban_info.guild)
                                    else:
                                        reply += '\n当前无屏蔽的群组。\n'
                                elif show_item in ['p', 'P']: # 平台
                                    if len(ban_info.platform) > 0: # 有针对平台的屏蔽
                                        reply += '\n屏蔽的平台有：\n'
                                        reply += '\n'.join(pf for pf in ban_info.platform)
                                    else:
                                        reply += '\n当前无屏蔽的平台。\n'
                                elif show_item in ['f', 'F']: # 插件
                                    # 尝试获取群组 ID
                                    try:
                                        guild_id = event.get_guild_id()
                                        if len(ban_info.plugin[guild_id]) > 0:
                                            reply += '\n本群屏蔽的插件有：\n'
                                            reply += '\n'.join(
                                                p for p in ban_info.plugin[guild_id]
                                            )
                                        else:
                                            reply += '\n本群无屏蔽的插件。\n'
                                    except:
                                        pass
                                else:
                                    continue
                            reply = '<i> ' + reply.strip()
                            bot.send(event, reply)
                            return
                    else:
                        item = message.extract_plain_text().strip()
                        # 分情况判断
                        if item in ['p', 'P']: # 屏蔽当前平台
                            try:
                                platform = event.get_platform()
                            except Exception as exception:
                                reply = f'<×> 获取平台信息失败: {type(exception).__name__}: {exception}'
                                bot.send(event, reply)
                                return
                            reply = Ban.ban_target('platform', platform)
                        elif item.startswith(('p ', 'P ')): # 屏蔽指定平台
                            platform = item[2:].strip()
                            if platform != '':
                                reply = Ban.ban_target('platform', platform)
                            else:
                                reply = '<×> 请输入要屏蔽的平台。'
                        elif item in ['g', 'G']: # 屏蔽当前群组
                            try:
                                guild = event.get_guild_id()
                            except Exception as exception:
                                reply = f'<×> 获取群组信息失败: {type(exception).__name__}: {exception}'
                                bot.send(event, reply)
                                return
                            reply = Ban.ban_target('guild', guild)
                        elif item.startswith(('g ', 'G ')): # 屏蔽指定群组
                            guild = item[2:].strip()
                            reply = Ban.ban_target('guild', guild)
                        elif item.startswith(('u ', 'U ')): # 屏蔽指定用户
                            user = item[2:].strip()
                            reply = Ban.ban_target('user', user)
                        else:
                            if item.isdigit(): # 如果是数字则作为用户 ID
                                reply = Ban.ban_target('user', item)
                            else: # 屏蔽指定插件
                                plugin = item.strip()
                                # 获取群组 ID
                                try:
                                    guild = event.get_guild_id()
                                except:
                                    return
                                reply = Ban.ban(guild, plugin)
                    bot.send(event, reply)
                    return
                elif message[0].type == 'at': # 如果是提及某用户
                    # 屏蔽指定用户
                    user_id = message[0].data['id']
                    if isinstance(user_id, str) and user_id.isdigit(): # 是合法 ID
                        # 屏蔽指定用户
                        reply = Ban.ban_target('user', user_id)
                        bot.send(event, reply)
                        return
            else: # 只会出现 'u @user' 的情况
                if message[0].is_text() and message[1].type == 'at':
                    if message[0].data['text'].strip() in ['u', 'U']:
                        # 屏蔽指定用户
                        user_id = message[1].data['id']
                        reply = Ban.ban_target('user', user_id)
                        bot.send(event, reply)
                        return
        elif message.extract_plain_text().startswith('/unban '):
            message[0].data['text'] = message[0].data['text'][7:].strip()
            if message[0].data['text'] == '':
                del message[0]
            if not message: return
            if len(message) == 1: # 如果只剩一个消息段
                if message[0].is_text(): # 如果是字符串
                    item = message.extract_plain_text().strip()
                    # 分情况判断
                    if item in ['p', 'P']: # 解除当前平台屏蔽
                        try:
                            platform = event.get_platform()
                        except Exception as exception:
                            reply = f'<×> 获取平台信息失败: {type(exception).__name__}: {exception}'
                            bot.send(event, reply)
                            return
                        reply = Ban.unban_target('platform', platform)
                    elif item.startswith(('p ', 'P ')): # 解除指定平台屏蔽
                        platform = item[2:].strip()
                        if platform != '':
                            reply = Ban.unban_target('platform', platform)
                        else:
                            reply = '<×> 请输入要解除屏蔽的平台。'
                    elif item in ['g', 'G']: # 解除当前群组屏蔽
                        try:
                            guild = event.get_guild_id()
                        except Exception as exception:
                            reply = f'<×> 获取群组信息失败: {type(exception).__name__}: {exception}'
                            bot.send(event, reply)
                            return
                        reply = Ban.unban_target('guild', guild)
                    elif item.startswith(('g ', 'G ')): # 解除指定群组屏蔽
                        guild = item[2:].strip()
                        reply = Ban.unban_target('guild', guild)
                    elif item.startswith(('u ', 'U ')): # 解除指定用户屏蔽
                        user = item[2:].strip()
                        reply = Ban.unban_target('user', user)
                    else:
                        if item.isdigit(): # 如果是数字则作为用户 ID
                            reply = Ban.unban_target('user', item)
                        else: # 解除指定插件屏蔽
                            plugin = item.strip()
                            # 获取群组 ID
                            try:
                                guild = event.get_guild_id()
                            except:
                                return
                            reply = Ban.unban(guild, plugin)
                    bot.send(event, reply)
                    return
                elif message[0].type == 'at': # 如果是提及某用户
                    # 解除指定用户屏蔽
                    user_id = message[0].data['id']
                    if isinstance(user_id, str) and user_id.isdigit(): # 是合法 ID
                        # 解除指定用户屏蔽
                        reply = Ban.unban_target('user', user_id)
                        bot.send(event, reply)
                        return
            else: # 只会出现 'u @user' 的情况
                if message[0].is_text() and message[1].type == 'at':
                    if message[0].data['text'].strip() in ['u', 'U']:
                        # 解除指定用户屏蔽
                        user_id = message[1].data['id']
                        reply = Ban.unban_target('user', user_id)
                        bot.send(event, reply)
                        return

# 事件过滤器
def event_filter(bot: Bot, event: Event) -> bool:
    '''事件过滤器

    参数:
        bot (Bot): 机器人实例
        event (Event): 事件对象

    返回:
        bool: 是否被过滤
    '''
    # 获取屏蔽信息
    ban_info = Ban._get_info()
    # 判断平台
    try:
        platform = event.get_platform()
        if platform in ban_info.platform:
            return False
    except Exception as exception:
        print(f'获取平台时出错：{type(exception).__name__}: {exception}')
    # 判断群组
    try:
        guild = event.get_guild_id()
        if guild in ban_info.guild:
            return False
    except Exception as exception:
        print(f'获取群组时出错：{type(exception).__name__}: {exception}')
    # 判断用户
    try:
        user = event.get_user_id()
        if user in ban_info.user:
            return False
    except Exception as exception:
        print(f'获取用户时出错：{type(exception).__name__}: {exception}')
    return True
