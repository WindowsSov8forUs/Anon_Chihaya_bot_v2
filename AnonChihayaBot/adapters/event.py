'''Anon Chihaya 框架适配器
基础事件类型定义
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
import abc
from pydantic import BaseModel
from typing import TypeVar, Any

from .message import Message

# 定义类型变量
E = TypeVar('E', bound='Event')

# 事件基类
class Event(abc.ABC, BaseModel):
    '''事件基类'''
    # 获取事件类型方法
    @abc.abstractmethod
    def get_type(self) -> str:
        '''获取事件类型，通常为 `notice`, `request`, `message`, `meta_event` 四种'''
        raise NotImplementedError
    
    # 获取事件接收平台
    @abc.abstractmethod
    def get_platform(self) -> str:
        '''获取事件接收平台'''
        raise NotImplementedError
    
    # 获取事件名称方法
    @abc.abstractmethod
    def get_event_name(self) -> str:
        '''获取事件名称'''
        raise NotImplementedError
    
    # 获取事件描述方法
    @abc.abstractmethod
    def get_event_desc(self) -> str:
        '''获取事件描述'''
        raise NotImplementedError
    
    # 获取事件日志信息方法
    def get_log(self) -> str:
        '''获取事件日志信息'''
        return f'[{self.get_event_name()}]{self.get_event_desc()}'
    
    # 获取事件用户 ID
    @abc.abstractmethod
    def get_user_id(self) -> str:
        '''获取事件用户 ID'''
        raise NotImplementedError
    
    # 获取群组 ID
    @abc.abstractmethod
    def get_guild_id(self) -> str:
        '''获取群组 ID，判断当前事件属于哪一个群组'''
        raise NotImplementedError
    
    # 获取消息内容
    @abc.abstractmethod
    def get_message(self) -> Message:
        '''获取消息内容'''
        raise NotImplementedError
    
    # 获取消息纯文本内容
    def get_plaintext(self) -> str:
        '''获取消息纯文本内容'''
        return self.get_message().extract_plain_text()
    
    # 获取事件是否与机器人有关
    @abc.abstractmethod
    def is_tome(self) -> bool:
        '''获取事件是否与机器人有关'''
        raise NotImplementedError

    # 类型配置
    class Config:
        extra = 'allow'
