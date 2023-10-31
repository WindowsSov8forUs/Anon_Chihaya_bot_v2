'''Anon Chihaya 框架适配器
基础机器人类型定义
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
import abc
from typing import Union, TYPE_CHECKING, Any

from .event import Event
from .message import Message, MessageSegment

if TYPE_CHECKING: # 导入类只供进行类型检查使用
    from .adapter import Adapter

# Bot 基类
class Bot(abc.ABC):
    '''Bot 基类

    参数:
        adapter (Adapter): 协议适配器实例
        self_id (str): 机器人 ID
    '''
    # 初始化方法
    def __init__(self, adapter: 'Adapter', self_id: str) -> None:
        '''Bot 基类

        参数:
            adapter (Adapter): 协议适配器实例
            self_id (str): 机器人 ID
        '''
        self.adapter: 'Adapter' = adapter
        '''协议适配器实例'''
        self.self_id: str = self_id
        '''机器人 ID'''
    
    # 协议适配器名称
    @property
    def type(self) -> str:
        '''协议适配器名称'''
        return self.adapter.get_name()
    
    # 对外输出方法
    def __repr__(self) -> str:
        '''对外输出方法'''
        return f'Bot：[{self.type}] ID：{self.self_id}'
    
    # 发送消息
    @abc.abstractmethod
    def send(
        self,
        event: Event,
        message: Union[str, 'Message', 'MessageSegment'],
        at_sender: bool=False,
        reply: bool=False
    ) -> Any:
        '''发送消息

        参数:
            event (Event): 要回复的事件
            message (Union[str, Message, MessageSegment]): 要发送的内容
            at_sender (bool, optional): 是否提及发送者
            reply (bool, optional): 是否回复该消息

        返回:
            Any: 消息发送后返回的数据
        '''
        raise NotImplementedError
    
    # 判断是否为主人
    @abc.abstractmethod
    def is_host(self, user_id: str) -> bool:
        '''判断是否为主人

        参数:
            user_id (str): 用户 ID

        返回:
            bool: 判断结果
        '''
        raise NotImplementedError
    
    # 调用机器人 API 接口
    def call_api(self, api: str, **data: Any) -> Any:
        '''调用机器人 API 接口

        参数:
            api (str): API 名称
            **data (Any): API 数据

        返回:
            Any: API 响应数据
        '''
        return self.adapter._call_api(self, api, **data)
