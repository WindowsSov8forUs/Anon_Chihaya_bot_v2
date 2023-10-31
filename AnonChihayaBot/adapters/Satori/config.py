'''Anon Chihaya 框架 Satori 协议适配器
配置类型定义
'''
import os
import yaml
from typing_extensions import override
from typing import Optional, Literal, Any
from pydantic import BaseModel, root_validator

from AnonChihayaBot.adapters import Config as BaseConfig

# 获取配置文件所在目录
CONFIG_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )
)

# Bot 账号配置类
class Account(BaseModel):
    '''Bot 账号配置类'''
    id: str
    '''Bot 账号'''
    platform: str
    '''Bot 平台'''

# Satori 协议配置类
class Config(BaseConfig):
    '''Satori 协议配置类'''
    version: Literal[1]
    '''Satori 协议版本'''
    path: str
    '''进行连接的路径'''
    token: str
    '''进行鉴权需要的 `token`'''
    heartbeat_interval: int=5
    '''心跳时间间隔'''
    webhook_url: Optional[str]=None
    '''框架自主反向 HTTP POST 通信 URL'''
    webhook_path: str='/'
    '''框架自主反向 HTTP POST 通信路径'''
    accounts: list[Account]=[]
    '''Bot 账号配置'''
    # 转换字典内容
    @root_validator(pre=True)
    def get_config(cls, values: dict[str, Any]) -> dict[str, Any]:
        '''转换字典内容

        参数:
            values (dict[str, Any]): 转换前内容

        返回:
            dict[str, Any]: 转换后内容
        '''
        post_values: dict[str, Any] = {}
        post_values['protocol'] = 'Satori'
        post_values['host_id'] = values['host_id']
        post_values['version'] = values['version']
        if values['serve'] == 'WebSocket': # 如果使用 WebSocket 服务
            if 'WebSocket' in values.keys():
                post_values['ip'] = values['WebSocket']['ip']
                post_values['port'] = values['WebSocket']['port']
                post_values['path'] = values['WebSocket']['path']
                post_values['token'] = values['WebSocket']['token']
                post_values['heartbeat_interval'] = values['WebSocket']['heartbeat_interval']
            else:
                raise ValueError(f'没有配置 WebSocket 服务配置。')
        elif values['serve'] == 'WebHook': # 如果使用 WebHook 服务
            if 'WebHook_Server' in values.keys():
                post_values['ip'] = values['WebHook_Server']['ip']
                post_values['port'] = values['WebHook_Server']['port']
                post_values['path'] = values['WebHook_Server']['path']
                post_values['token'] = values['WebHook_Server']['token']
                post_values['accounts'] = values['WebHook_Server']['accounts']
            else:
                raise ValueError(f'没有配置 WebHook 服务配置。')
        elif values['serve'] == 'Dev': # 如果使用框架 WebSocket 转发 HTTP 服务
            if 'WebSocket' in values.keys():
                post_values['ip'] = values['WebSocket']['ip']
                post_values['port'] = values['WebSocket']['port']
                post_values['path'] = values['WebSocket']['path']
                post_values['token'] = values['WebSocket']['token']
                post_values['heartbeat_interval'] = values['WebSocket']['heartbeat_interval']
            else:
                raise ValueError(f'没有配置 WebSocket 服务配置。')
            if 'WebHook_Client' in values.keys():
                post_values['webhook_url'] = 'http://{}:{}'.format(
                    values['WebHook_Client']['ip'],
                    values['WebHook_Client']['port']
                )
                post_values['webhook_path'] = values['WebHook_Client']['path']
            else:
                raise ValueError(f'没有配置反向 HTTP 转发服务配置。')
        
        return post_values
    
    # 获取文件内配置
    @classmethod
    @override
    def from_yaml(cls, serve: Literal['WebSocket', 'WebHook', 'Dev']='WebSocket') -> list['Config']:
        # 打开配置文件，文件为 /config.yml
        if os.path.exists(CONFIG_DIR + '/config.yml'):
            # 如果存在配置文件
            with open(CONFIG_DIR + '/config.yml', 'r+', encoding='utf-8') as file:
                try:
                    config: dict[str, Any] = yaml.safe_load(file)
                except Exception as exception:
                    raise exception
                file.close()
            
            # 检查是否存在 Satori 配置
            if 'Satori' in config.keys():
                cfgs: list[dict[str, Any]] = config['Satori']
                # 创建并返回 Config 对象列表
                configs: list['Config'] = []
                try:
                    for cfg in cfgs: # 遍历
                        cfg['host_id'] = config['host_id']
                        cfg['serve'] = serve
                        configs.append(
                            cls.model_validate(cfg)
                        )
                    return configs
                except Exception as exception:
                    raise exception
            else:
                raise ValueError('配置文件中不存在 Satori 协议配置。')
        else:
            raise FileNotFoundError('AnonChihayaBot 配置文件 config.yml 不存在或不在正确的路径上。')
