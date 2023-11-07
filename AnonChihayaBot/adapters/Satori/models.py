'''Anon Chihaya 框架 Satori 协议适配器
Satori 模型定义
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from enum import IntEnum
from datetime import datetime
from pydantic.generics import GenericModel
from pydantic import BaseModel, root_validator, validator
from typing import Optional, Generic, Literal, TypeVar, Union, Any

from .utils import Element, parse

# 信令类型类型定义
class SignalingType(IntEnum):
    '''信令类型'''
    EVENT = 0
    '''事件'''
    PING = 1
    '''心跳'''
    PONG = 2
    '''心跳回复'''
    IDENTIFY = 3
    '''鉴权'''
    READY = 4
    '''鉴权回复'''

# 信令类型定义
class Signaling(BaseModel):
    '''信令'''
    op: SignalingType
    '''信令类型'''
    body: Optional[dict[str, Any]]=None
    '''信令数据'''

# 频道类型类型定义
class ChannelType(IntEnum):
    '''频道类型'''
    TEXT = 0
    '''文本频道'''
    VOICE = 1
    '''语音频道'''
    CATEGORY = 2
    '''分类频道'''
    DIRECT = 3
    '''私聊频道'''

# 频道类型定义
class Channel(BaseModel, extra='allow'):
    '''频道'''
    id: str
    '''频道 ID'''
    type: ChannelType
    '''频道类型'''
    name: Optional[str]=None
    '''频道名称'''
    parent_id: Optional[str]=None
    '''父频道 ID'''

# 群组类型定义
class Guild(BaseModel):
    '''群组'''
    id: str
    '''群组 ID'''
    name: Optional[str]=None
    '''群组名称'''
    avatar: Optional[str]=None
    '''群组头像'''

# 用户类型定义
class User(BaseModel):
    '''用户类型定义'''
    id: str
    '''用户 ID'''
    name: Optional[str]=None
    '''用户名称'''
    nick: Optional[str]=None
    '''用户昵称'''
    avatar: Optional[str]=None
    '''用户头像'''
    is_bot: Optional[bool]=None
    '''是否为机器人'''

# 群组成员类型定义
class GuildMember(BaseModel):
    '''群组成员'''
    user: Optional[User]=None
    '''用户对象'''
    nick: Optional[str]=None
    '''用户在群组中的名称'''
    avatar: Optional[str]=None
    '''用户在群组中的头像'''
    joined_at: Optional[datetime]=None
    '''加入时间'''
    # 重定义 joined_at 验证方法
    @validator('joined_at', pre=True)
    def parse_joined_at(cls, value: Optional[Union[datetime, Any]]=None) -> Optional[datetime]:
        '''`joined_at` 验证方法'''
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            timestamp = int(value)
        except ValueError as exception:
            raise ValueError(f'不合法的时间戳：{value}') from exception
        return datetime.fromtimestamp(timestamp / 1000)

# 群组角色类型定义
class GuildRole(BaseModel):
    '''群组角色'''
    id: str
    '''角色 ID'''
    name: Optional[str]=None
    '''角色名称'''

# 登录状态类型定义
class Status(IntEnum):
    '''登录状态'''
    OFFLINE = 0
    '''离线'''
    ONLINE = 1
    '''在线'''
    CONNECT = 2
    '''连接中'''
    DISCONNECT = 3
    '''断开连接'''
    RECONNECT = 4
    '''重新连接'''

# 登录信息类型定义
class Login(BaseModel):
    '''登录信息'''
    user: Optional[User]=None
    '''用户对象'''
    self_id: Optional[str]=None
    '''平台账号'''
    platform: Optional[str]=None
    '''平台名称'''
    status: Status
    '''登录状态'''

# 消息类型定义
class Message(BaseModel):
    '''消息'''
    id: str
    '''消息 ID'''
    quote: Optional['Message']=None
    '''引用消息'''
    content: list[Element]
    '''消息内容'''
    channel: Optional[Channel]=None
    '''频道对象'''
    guild: Optional[Guild]=None
    '''群组对象'''
    member: Optional[GuildMember]=None
    '''成员对象'''
    user: Optional[User]=None
    '''用户对象'''
    created_at: Optional[datetime]=None
    '''消息发送的时间戳'''
    updated_at: Optional[datetime]=None
    '''消息修改的时间戳'''
    # 验证是否存在 content 字段
    @root_validator(pre=True)
    def ensure_content(cls, values: Union[dict[str, Any], str]) -> dict[str, Any]:
        '''验证是否存在 `content` 字段'''
        if isinstance(values, str): # 这种情况下，只会收到 Message.id
            return {'id': values, 'content': 'Unknown'}
        if (quote := values.get('quote', None)) is not None:
            # 如果有引用消息
            if not isinstance(content := values.get('content', None), list):
                # 表明未进行过验证
                if (id_ := quote.get('id', None)) is not None:
                    values['content'] = (
                        f'<quote id="{id_}" forward/>' + (
                            content if content is not None else ''
                        )
                    )
        if 'content' in values: # 如果存在
            return values
        print('收到一个不存在 content 的消息。')
        return {**values, 'content': 'Unknown'}
    
    # 重定义 content 验证方法
    @validator('content', pre=True)
    def parse_content(cls, value: Any) -> Optional[list[Element]]:
        '''`content` 验证方法'''
        if isinstance(value, list):
            return value
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError('content 字段必须为字符串')
        return parse(value)
    
    # 重定义 created_at 验证方法
    @validator('created_at', pre=True)
    def parse_created_at(cls, value: Optional[Union[datetime, Any]]=None) -> Optional[datetime]:
        '''`created_at` 验证方法'''
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            timestamp = int(value)
        except ValueError as exception:
            raise ValueError(f'不合法的时间戳：{value}') from exception
        return datetime.fromtimestamp(timestamp / 1000)

    # 重定义 updated_at 验证方法
    @validator('updated_at', pre=True)
    def parse_updated_at(cls, value: Optional[Union[datetime, Any]]=None) -> Optional[datetime]:
        '''`updated_at` 验证方法'''
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            timestamp = int(value)
        except ValueError as exception:
            raise ValueError(f'不合法的时间戳：{value}') from exception
        return datetime.fromtimestamp(timestamp / 1000)

# 事件类型定义
class Event(BaseModel):
    '''事件'''
    id: int
    '''事件 ID'''
    type: str
    '''事件类型'''
    platform: str
    '''接受者的平台名称'''
    self_id: str
    '''接收者的平台账号'''
    timestamp: datetime
    '''事件的时间戳'''
    channel: Optional[Channel]=None
    '''事件所属的频道'''
    guild: Optional[Guild]=None
    '''事件所属的群组'''
    login: Optional[Login]=None
    '''事件的登录信息'''
    member: Optional[GuildMember]=None
    '''事件的目标成员'''
    message: Optional[Message]=None
    '''事件的消息'''
    operator: Optional[User]=None
    '''事件的操作者'''
    role: Optional[GuildRole]=None
    '''事件的目标角色'''
    user: Optional[User]=None
    '''事件的目标用户'''
    # 重定义 timestamp 验证方法
    @validator('timestamp', pre=True)
    def parse_timestamp(cls, value: Optional[Union[datetime, Any]]=None) -> Optional[datetime]:
        '''`timestamp` 验证方法'''
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            timestamp = int(value)
        except ValueError as exception:
            raise ValueError(f'不合法的时间戳：{value}') from exception
        return datetime.fromtimestamp(timestamp / 1000)

# 鉴权信令数据定义
class IdentifyBody(BaseModel):
    '''鉴权信令数据'''
    token: Optional[str]=None
    '''鉴权令牌'''
    sequence: Optional[int]=None
    '''序列号'''

# 鉴权信令定义
class Identify(Signaling):
    '''鉴权信令'''
    op: Literal[SignalingType.IDENTIFY]=SignalingType.IDENTIFY
    '''信令类型'''
    body: IdentifyBody
    '''信令数据'''

# 鉴权回复信令数据定义
class ReadyBody(BaseModel):
    '''鉴权回复信令数据'''
    logins: list[Login]
    '''登录信息'''

# 鉴权回复信令定义
class Ready(Signaling):
    '''鉴权回复信令'''
    op: Literal[SignalingType.READY]=SignalingType.READY
    '''信令类型'''
    body: ReadyBody
    '''信令数据'''

# 心跳信令定义
class Ping(Signaling):
    '''心跳信令'''
    op: Literal[SignalingType.PING]=SignalingType.PING
    '''信令类型'''

# 心跳回复信令定义
class Pong(Signaling):
    '''心跳回复信令'''
    op: Literal[SignalingType.PONG]=SignalingType.PONG
    '''信令类型'''

# 事件信令定义
class EventSignaling(Signaling):
    '''事件信令'''
    op: Literal[SignalingType.EVENT]=SignalingType.EVENT
    '''信令类型'''
    body: Event
    '''信令数据'''

# 定义泛型分页类型
T = TypeVar('T', bound=BaseModel)

# 分页列表定义
class Pagination(GenericModel, Generic[T], extra='allow'):
    '''分页列表'''
    data: list[T]
    '''数据'''
    next: Optional[str]=None
    '''下一页的令牌'''
    # 创建一个分页列表对象
    @classmethod
    def pagination(
        cls,
        data_cls: type[T],
        **data: Union[list[dict[str, Any]], str]
    ) -> 'Pagination[T]':
        '''创建一个分页列表对象

        参数:
            data_cls (type[T]): 数据类型
            **data (Union[list[dict[str, Any]], str]): 分页列表数据
                `data` (list[dict[str, Any]]): 数据
                `next` (str): 下一页的令牌

        返回:
            Pagination[T]: 一个 `分页列表`
        '''
        pagination = cls(
            data=[data_cls.model_validate(d) for d in data.get('data', [])],
            next=data.get('next', None)
        )
        return pagination
