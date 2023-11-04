'''Anon Chihaya 框架
主程序入口
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from typing import Literal
from threading import Thread, Event

from AnonChihayaBot.adapters import Adapter
from AnonChihayaBot.adapters.Satori import Config as SatoriConfig
from AnonChihayaBot.adapters.Satori import Adapter as SatoriAdapter

# AnonChihayaBot 类
class AnonChihayaBot():
    '''AnonChihayaBot 类'''
    # 初始化方法
    def __init__(self, serve: Literal['WebSocket', 'WebHook', 'Dev']) -> None:
        '''初始化方法'''
        self.serve: Literal['WebSocket', 'WebHook', 'Dev'] = serve
        '''实例所启用的服务种类'''
        self.adapters: list[Adapter] = []
        '''实例所包括的所有 Bot 线程'''
        return
    # AnonChihayaBot 运行方法
    @classmethod
    def run(
        cls,
        protocol: Literal['Satori']='Satori',
        serve: Literal['WebSocket', 'WebHook', 'Dev']='WebSocket'
    ) -> 'AnonChihayaBot':
        '''AnonChihayaBot 运行方法

        参数:
            protocol (Literal[&#39;Satori&#39;], optional): 运行采用的协议
            serve (Literal[&#39;WebSocket&#39;, &#39;WebHook&#39;, &#39;Dev&#39;], optional): 运行时采用的服务种类
                `WebSocket` : 采用 `WebSocket` 服务连接 Satori 协议
                `WebHook` : 采用 `WebHook` 服务连接 Satori 协议
                `Dev` : 采用 `WebSocket` 服务连接 Satori 协议，并由框架进行 HTTP POST 推送

        返回:
            AnonChihayaBot: AnonChihayaBot 实例
        '''
        anon_app = cls(serve)
        anon_app.serve = serve
        if protocol == 'Satori': # 使用 Satori 协议
            config = SatoriConfig.from_yaml(serve)
        
            # 遍历 config 创建 Adapter
            for cfg in config:
                if cfg.protocol == 'Satori':
                    anon_app.adapters.append(SatoriAdapter.setup(cfg, serve))
        
        return anon_app
    
    # 处理 request
    def handle(self, request: str) -> None:
        '''处理 request
            示例：
            ```python
            AnonChohayaBot.handle(request.get_json())
            ```

        参数:
            request (str): 从`flask.request` 接收到的 `json` 字符串
        '''
        if self.serve != 'WebHook':
            print(f'该 AnonChihayaBot 实例所启动的是 {self.serve} 服务，不可使用该方法。')
            return
        for adapter in self.adapters:
            Thread(target=adapter.handle_request, args=(request,), daemon=True).start()
        return
    
    # 停止运行 AnonChihayaBot
    def stop(self) -> None:
        '''停止运行 AnonChihayaBot'''
        for adapter in self.adapters:
            adapter.manual_close = True
