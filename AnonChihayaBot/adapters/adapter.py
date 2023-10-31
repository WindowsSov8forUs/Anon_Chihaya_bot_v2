'''Anon Chihaya 框架适配器
基础适配器类型定义
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
import abc
from typing import Optional, Any

from AnonChihayaBot.adapters.config import Config

from .bot import Bot

# 协议适配器基类
class Adapter(abc.ABC):
    '''协议适配器基类

    参数:
        config (Config): 机器人配置
    '''
    # 初始化方法
    def __init__(self, config: Config) -> None:
        '''协议适配器基类

        参数:
            config (Config): 机器人配置
        '''
        self.config: 'Config' = config
        '''机器人配置'''
        self.bots: dict[str, Bot] = {}
        '''机器人实例'''
        self.manual_close: bool=False
        '''是否被人为关闭'''
        self.retrys = 5
        '''当前适配器的剩余重试次数'''
    
    # 当前适配器名称
    @classmethod
    @abc.abstractmethod
    def get_name(cls) -> str:
        '''当前适配器名称'''
        raise NotImplementedError
    
    # 处理从 flask.request 接收的 json 信息
    def handle_request(self, request: str) -> None:
        '''处理从 `flask.request` 接收的 `json` 信息

        参数:
            request (str): 从 `flask.request` 接收的 `json` 信息
        '''
        raise NotImplementedError
    
    # 输出连接对象
    @property
    def get_connection(self) -> str:
        '''适配器连接对象'''
        return f'{self.config.protocol}|({self.api_base})'
    
    # API 链接基础
    @property
    def api_base(self) -> str:
        '''API 链接基础'''
        return f'{self.config.ip}:{self.config.port}'
    
    # 对外输出方法
    def __repr__(self) -> str:
        '''对外输出方法'''
        return f'适配器：{self.get_name()}'
    
    # API 调用实现函数
    @abc.abstractmethod
    def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        '''`Adapter` 调用 API 实现'''
        raise NotImplementedError
