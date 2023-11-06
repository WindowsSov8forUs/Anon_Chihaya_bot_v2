'''Anon Chihaya 框架 Satori 协议适配器
事件类型定义
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from enum import Enum
from copy import deepcopy
from pydantic import root_validator
from typing_extensions import override
from typing import Optional, Type, TYPE_CHECKING, Any

from AnonChihayaBot.adapters import Event as BaseEvent

from .models import Event as SatoriEvent
from .message import Message, RenderMessage
from .models import Message as SatoriMessage
from .models import Guild, Login, Channel, GuildMember, GuildRole, User

# 事件类型枚举类
class EventType(str, Enum):
    '''事件类型'''
    GUILD_ADDED = "guild-added"
    '''加入群组'''
    GUILD_UPDATED = "guild-updated"
    '''群组被修改'''
    GUILD_REMOVED = "guild-removed"
    '''退出群组'''
    GUILD_REQUEST = "guild-request"
    '''接收到新的入群邀请'''
    GUILD_MEMBER_ADDED = "guild-member-added"
    '''群组成员增加'''
    GUILD_MEMBER_UPDATED = "guild-member-updated"
    '''群组成员信息更新'''
    GUILD_MEMBER_REMOVED = "guild-member-removed"
    '''群组成员移除'''
    GUILD_MEMBER_REQUEST = "guild-member-request"
    '''接收到新的加群请求'''
    GUILD_ROLE_CREATED = "guild-role-created"
    '''群组角色被创建'''
    GUILD_ROLE_UPDATED = "guild-role-updated"
    '''群组角色被修改'''
    GUILD_ROLE_DELETED = "guild-role-deleted"
    '''群组角色被删除'''
    LOGIN_ADDED = "login-added"
    '''登录被创建'''
    LOGIN_REMOVED = "login-removed"
    '''登录被删除'''
    LOGIN_UPDATED = "login-updated"
    '''登录信息更新'''
    MESSAGE_CREATED = "message-created"
    '''消息被创建'''
    MESSAGE_UPDATED = "message-updated"
    '''消息被编辑'''
    MESSAGE_DELETED = "message-deleted"
    '''消息被删除'''
    REACTION_ADDED = "reaction-added"
    '''表态被添加'''
    REACTION_REMOVED = "reaction-removed"
    '''表态被移除'''
    FRIEND_REQUEST = "friend-request"
    '''接收到新的好友申请'''
    INTERNAL = 'internal'
    '''内部事件'''

# 基础事件类
class Event(BaseEvent, SatoriEvent):
    '''基础事件类'''
    __type__: EventType
    '''事件类型'''
    # 获取类型方法
    @override
    def get_type(self) -> str:
        return ''
    
    # 获取事件接收平台
    @override
    def get_platform(self) -> str:
        return self.platform
    
    # 获取事件名称
    @override
    def get_event_name(self) -> str:
        return self.type
    
    # 获取事件描述
    @override
    def get_event_desc(self) -> str:
        return str(self.model_dump_json(indent=4))
    
    # 获取消息内容
    @override
    def get_message(self) -> Message:
        raise ValueError('该事件没有消息内容。')
    
    # 获取事件用户 ID
    @override
    def get_user_id(self) -> str:
        raise ValueError('该事件没有用户 ID。')
    
    # 获取群组 ID，判断当前事件属于哪一个群组
    @override
    def get_guild_id(self) -> str:
        raise ValueError('该事件没有群组 ID。')
    
    # 获取事件是否与机器人有关
    @override 
    def is_tome(self) -> bool:
        return False

# 注册可用事件类型
EVENT_CLASSES: dict[str, Type[Event]] = {}

def register_event_class(event_class: Type[Event]) -> Type[Event]:
    '''注册可用事件类型

    参数:
        event_class (Type[Event]): 注册的事件类

    返回:
        Type[Event]: 注册的事件类
    '''
    EVENT_CLASSES[event_class.__type__.value] = event_class
    return event_class

# 提示事件
class NoticeEvent(Event):
    '''提示事件'''
    # 获取类型方法
    @override
    def get_type(self) -> str:
        return 'notice'

# 好友事件
class FriendEvent(NoticeEvent):
    '''好友事件'''
    user: User
    '''事件的目标用户'''
    # 获取用户 ID
    @override
    def get_user_id(self) -> str:
        return self.user.id

# 好友申请事件
@register_event_class
class FriendRequestEvent(FriendEvent):
    __type__ = EventType.FRIEND_REQUEST
    '''事件类型'''

# 群组事件
class GuildEvent(NoticeEvent):
    '''群组事件'''
    guild: Guild
    '''事件所属的群组'''
    # 获取群组 ID
    @override
    def get_guild_id(self) -> str:
        return self.guild.id

# 加入群组事件
@register_event_class
class GuildAddedEvent(GuildEvent):
    '''加入群组事件'''
    __type__ = EventType.GUILD_ADDED
    '''事件类型'''

# 群组被修改事件
@register_event_class
class GuildUpdatedEvent(GuildEvent):
    '''群组被修改事件'''
    __type__ = EventType.GUILD_UPDATED
    '''事件类型'''

# 退出群组事件
@register_event_class
class GuildRemovedEvent(GuildEvent):
    '''退出群组事件'''
    __type__ = EventType.GUILD_REMOVED
    '''事件类型'''

# 接收到群组邀请事件
@register_event_class
class GuildRequestEvent(GuildEvent):
    '''接收到群组邀请事件'''
    __type__ = EventType.GUILD_REQUEST
    '''事件类型'''

# 群组成员事件
class GuildMemberEvent(GuildEvent):
    '''群组成员事件'''
    member: GuildMember
    '''事件的目标成员'''
    user: User
    '''事件的目标用户'''
    
    @override
    def get_user_id(self) -> str:
        return self.user.id

# 群组成员增加事件
@register_event_class
class GuildMemberAddedEvent(GuildMemberEvent):
    '''群组成员增加事件'''
    __type__ = EventType.GUILD_MEMBER_ADDED
    '''事件类型'''

# 群组成员信息更新事件
@register_event_class
class GuildMemberUpdatedEvent(GuildMemberEvent):
    '''群组成员信息更新事件'''
    __type__ = EventType.GUILD_MEMBER_UPDATED
    '''事件类型'''

# 群组成员移除事件
@register_event_class
class GuildMemberRemovedEvent(GuildMemberEvent):
    '''群组成员移除事件'''
    __type__ = EventType.GUILD_MEMBER_REMOVED
    '''事件类型'''

# 接收到加群请求事件
@register_event_class
class GuildMemberRequestEvent(GuildMemberEvent):
    '''接收到加群请求事件'''
    __type__ = EventType.GUILD_MEMBER_REQUEST
    '''事件类型'''

# 群组角色事件
class GuildRoleEvent(GuildEvent):
    '''群组角色事件'''
    role: GuildRole
    '''事件的目标角色'''

# 群组角色被创建事件
@register_event_class
class GuildRoleCreatedEvent(GuildRoleEvent):
    '''群组角色被创建事件'''
    __type__ = EventType.GUILD_ROLE_CREATED
    '''事件类型'''

# 群组角色被修改事件
@register_event_class
class GuildRoleUpdatedEvent(GuildRoleEvent):
    '''群组角色被修改事件'''
    __type__ = EventType.GUILD_ROLE_UPDATED
    '''事件类型'''

# 群组角色被删除事件
@register_event_class
class GuildRoleDeletedEvent(GuildRoleEvent):
    '''群组角色被删除事件'''
    __type__ = EventType.GUILD_ROLE_DELETED
    '''事件类型'''

# 登录事件
class LoginEvent(NoticeEvent):
    '''登录事件'''
    login: Login
    '''事件的登录信息'''
    # 获取事件日志信息
    @override
    def get_log(self) -> str:
        log = f'[{self.__type__}]机器人 '
        if self.login.user is not None:
            log += f'{self.login.user.name} ({self.login.user.id})'
        else:
            log += 'None'
        log += f' 在平台 {self.login.platform} 上的状态发生更新：{self.login.status.name}'
        return log

# 登录被创建事件
@register_event_class
class LoginAddedEvent(LoginEvent):
    '''登录被创建事件'''
    __type__ = EventType.LOGIN_ADDED
    '''事件类型'''

# 登录被删除事件
@register_event_class
class LoginRemovedEvent(LoginEvent):
    '''登录被删除事件'''
    __type__ = EventType.LOGIN_REMOVED
    '''事件类型'''

# 登录信息更新事件
@register_event_class
class LoginUpdatedEvent(LoginEvent):
    '''登录信息更新事件'''
    __type__ = EventType.LOGIN_UPDATED
    '''事件类型'''

# 消息事件
class MessageEvent(Event):
    '''消息事件'''
    channel: Channel
    '''事件所属的频道'''
    user: User
    '''事件的目标用户'''
    message: SatoriMessage
    '''事件的消息'''
    to_me: bool=False
    '''是否与机器人有关'''
    reply: Optional[RenderMessage]=None
    '''是否存在回复'''
    if TYPE_CHECKING:
        _message: Message
        '''事件的消息数组'''
        original_message: Message
        '''事件的原始消息数组'''
    # 获取事件类型
    @override
    def get_type(self) -> str:
        return "message"

    # 获取消息数组
    @override
    def get_message(self) -> Message:
        return self._message
    
    # 获取事件是否与机器人有关
    @override
    def is_tome(self) -> bool:
        return self.to_me

    @root_validator(pre=False, skip_on_failure=True)
    def generate_message(cls, values: dict[str, Any]) -> dict[str, Any]:
        values['_message'] = Message.from_satori_element(values['message'].content)
        values['original_message'] = deepcopy(values['_message'])
        return values

    # 获取事件群组 ID
    @override
    def get_guild_id(self) -> str:
        return self.channel.id
    
    # 获取事件用户 ID
    @override
    def get_user_id(self) -> str:
        return self.user.id

    # 获取事件日志信息
    @override
    def get_log(self) -> str:
        log = ''
        if self.guild is not None: # 有群组
            log += f'[来自群组 {self.guild.name} ({self.guild.id})]'
        if self.member is not None: # 是群组消息
            if self.member.nick is not None: # 有群昵称
                log += f'{self.member.nick}'
            else:
                if self.user.name != '': # 如果名称不为空
                    log += f'{self.user.name}'
                else:
                    log += f'QQ用户{self.user.id}'
        else:
            log += f'{self.user.name}'
        log += f': {self.get_message().log}'
        return log
    
    # 获取消息 ID
    @property
    def message_id(self) -> str:
        '''消息 ID'''
        return self.message.id

# 消息被创建事件
@register_event_class
class MessageCreatedEvent(MessageEvent):
    '''消息被创建事件'''
    __type__ = EventType.MESSAGE_CREATED
    '''事件类型'''
    # 获取事件日志信息
    @override
    def get_log(self) -> str:
        return super().get_log()

# 消息被编辑事件
@register_event_class
class MessageUpdatedEvent(MessageEvent):
    '''消息被编辑事件'''
    __type__ = EventType.MESSAGE_UPDATED
    '''事件类型'''

# 消息被删除事件
@register_event_class
class MessageDeletedEvent(MessageEvent):
    '''消息被删除事件'''
    __type__ = EventType.MESSAGE_DELETED
    '''事件类型'''

# 内部事件
@register_event_class
class InternalEvent(Event):
    '''内部事件'''
    __type__ = EventType.INTERNAL
    '''事件类型'''
    _type: str
    '''内部事件类型'''
    _data: Any
    '''内部事件数据'''
