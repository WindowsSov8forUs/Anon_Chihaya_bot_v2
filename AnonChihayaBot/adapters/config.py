'''Anon Chihaya 框架适配器
配置类型定义
'''
import abc
from typing import Literal
from pydantic import BaseModel

# 配置基类
class Config(abc.ABC, BaseModel):
    '''配置基类'''
    host_id: str
    '''主人 ID'''
    protocol: str
    '''使用的协议'''
    ip: str
    '''与协议连接的 IP'''
    port: int
    '''与协议连接的端口'''
    # 获取文件内配置
    @classmethod
    @abc.abstractmethod
    def from_yaml(cls, serve: Literal['WebSocket', 'WebHook', 'Dev']='WebSocket') -> list['Config']:
        '''从 `config.yml` 中读取配置'''
        raise NotImplementedError
