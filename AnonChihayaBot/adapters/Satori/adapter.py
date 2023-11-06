'''Anon Chihaya 框架 Satori 协议适配器
机器人定义
'''
import json
import httpx
import websocket
from time import sleep
from httpx import Response
from threading import Thread
from typing import Literal, cast, Any
from typing_extensions import override

from AnonChihayaBot.adapters import logger
from AnonChihayaBot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .config import Config
from .models import Event as SatoriEvent
from .event import (
    Event,
    LoginEvent, LoginAddedEvent, LoginRemovedEvent, LoginUpdatedEvent,
    EVENT_CLASSES
)
from .models import (
    Identify, IdentifyBody,
    Ping, Ready, EventSignaling, Pong,
    Login
)

# 适配器类型
class Adapter(BaseAdapter):
    '''Satori 适配器

    参数:
        config (Config): 适配器配置
    '''
    ws: websocket.WebSocketApp
    '''WebSocket 客户端'''
    http: httpx.Client
    '''HTTP 客户端'''
    webhook_client: httpx.Client
    '''Webhook 客户端'''
    sequence: int = 0
    '''最后一次接收到的 `EVENT` 信令的 `id` 字段'''
    config: Config
    '''机器人配置'''
    # 初始化方法
    def __init__(self, config: Config) -> None:
        '''Satori 适配器

        参数:
            config (Config): 适配器配置
        '''
        super().__init__(config)
        self.bots: dict[str, Bot] = {}
    
    # 发送鉴权信令
    def _identify(self, ws: websocket.WebSocketApp, sequence: int=0) -> None:
        '''发送鉴权信令

        参数:
            ws (websocket.WebSocketApp): WebSocket 客户端
            sequence (int, optional): 上一次连接中最后一个接收到的 `EVENT` 信令的 `id` 字段
        '''
        # 构建 IDENTIFY 信令
        singaling = Identify(
            body=IdentifyBody(
                token=self.config.token,
                sequence=sequence
            )
        )
        try:
            ws.send(singaling.model_dump_json())
        except Exception as exception:
            info = f'鉴权信令发送失败: {type(exception).__name__}: {exception}'
            print(info)
            logger.error(exception)
            ws.close()
        return
    
    # 发送心跳信令
    def _ping(self) -> None:
        '''发送心跳信令'''
        # 构建 PING 信令
        singaling = Ping()
        self.ws.send(singaling.model_dump_json())
        return
    
    # 进行心跳活动
    def _heartbeat(self) -> None:
        '''进行心跳活动'''
        max_failure = 0 # 当失败超过 5 次后关闭连接
        while True:
            if self.manual_close: # 主动关闭
                self.ws.close()
                break
            if max_failure >= 5: # 断连自动重连
                self.ws.close()
                self._reconnect()
                break
            # 尝试发送心跳包
            try:
                sleep(self.config.heartbeat_interval)
                self._ping()
            except:
                print('本次心跳发送失败。')
                max_failure += 1
                continue
            max_failure = 0
    
    # 连接 Bot 对象
    def _bot_connect(self, logins: list[Login]) -> None:
        '''连接 Bot 对象'''
        for login in logins:
            if login.self_id is None:
                continue
            if login.user is None:
                continue
            # 过滤来自平台 'qq' 的消息
            if login.platform == 'qq':
                continue
            self.bots[login.self_id] = Bot(
                self,
                login.self_id,
                login.platform if login.platform is not None else '',
                self.config
            )
            if login.user is not None: # 记录登录信息
                self.bots[login.self_id].get_ready(login.user)
            login_info = (
                f'[{self.get_name()}|{login.self_id}] {login.user.name} 已连接到平台 {login.platform}'
            )
            print(login_info)
            logger.info(login_info)
    
    # 处理接收到的 payload 对象
    def _handle_payload(self, payload: dict[str, Any]) -> None:
        '''处理接收到的 payload 对象

        参数:
            payload (dict[str, Any]): 接收到的 payload 对象
        '''
        if payload['op'] == 0: # 事件信令
            try:
                signaling = EventSignaling.model_validate(payload)
            except Exception as exception:
                print(payload)
                print(f'{type(exception).__name__}: {exception}')
                return
        elif payload['op'] == 2: # 心跳回复信令
            signaling = Pong.model_validate(payload)
        elif payload['op'] == 4: # 鉴权回复信令
            signaling = Ready.model_validate(payload)
        else:
            print('未知的信令类型：{}'.format(payload['op']))
            return
        # 分情况处理信令
        if isinstance(signaling, Pong):
            pass
        elif isinstance(signaling, Ready):
            logins = signaling.body.logins
            self._bot_connect(logins)
        else:
            try:
                event = self.payload_to_event(signaling.body)
            except Exception as exception:
                print(f'{type(exception).__name__}: {exception}')
                logger.warning(f'将 payload 转换为事件时出错：{type(exception).__name__}: {exception}')
                logger.error(exception)
                return
            # 处理 LoginEvent
            if isinstance(event, LoginEvent):
                self._handle_login(event)
                return
            # 获取接收事件对应的机器人实例
            if event.self_id in self.bots.keys():
                bot = self.bots[event.self_id]
                # 创建并运行一个子线程，处理事件（既然没有返回值那就不需要等待了罢！
                Thread(target=bot.handle_event, args=(event,), daemon=True).start()
        return
    
    # 处理接收到的 LoginEvent
    def _handle_login(self, event: LoginEvent) -> None:
        '''处理接收到的 LoginEvent'''
        print(event.get_log())
        logger.info(event.get_log())
        login = event.login
        if isinstance(event, LoginAddedEvent):
            # 登录信息添加
            if login.user is not None:
                if login.user.id not in self.bots.keys():
                    self._bot_connect([login])
        elif isinstance(event, LoginUpdatedEvent):
            # 登录信息更新
            if login.user is not None:
                if login.user.id not in self.bots.keys():
                    self._bot_connect([login])
        elif isinstance(event, LoginRemovedEvent):
            # 登录信息删除
            if login.user is not None:
                if login.user.id in self.bots.keys():
                    del self.bots[login.user.id]
    
    # 连接建立时的回调函数
    def _on_open(self, ws: websocket.WebSocketApp) -> None:
        '''连接建立时的回调函数'''
        info = f'[{self.get_connection}] 正在连接 WebSocket 服务器...'
        logger.info(info)
        print(info)
        self._identify(ws)
        return
    
    # 收到消息时的回调函数
    def _on_message(self, ws: websocket.WebSocketApp, message: Any) -> None:
        '''收到消息时的回调函数'''
        payload: dict[str, Any] = json.loads(message) # 转换为字典类型
        # 内部直接过滤来自平台 'qq' 的事件
        if payload['body'].get('platform', None) == 'qq':
            return
        if self.config.webhook_url is not None:
            try:
                self.webhook_client.post(
                    self.config.webhook_path,
                    json=json.dumps(payload, ensure_ascii=False)
                )
            except Exception as exception:
                print(f'本次 Webhook 推送失败：{type(exception).__name__}: {exception}')
            return
        else:
            self._handle_payload(payload)
            return
    
    # 连接关闭时的回调函数
    def _on_close(self, ws: websocket.WebSocketApp) -> None:
        '''连接关闭时的回调函数'''
        if self.manual_close:
            info = f'[{self.get_connection}] 与 WebSocket 服务器的连接已被关闭。'
            logger.info(info)
            print(info)
        else:
            warning = f'[{self.get_connection}] 与 WebSocket 服务器的连接已断开，正在尝试重新连接...'
            logger.warning(warning)
            print(warning)
            self._reconnect()
        
    # 连接关闭后调用的自动重连函数
    def _reconnect(self) -> None:
        '''连接关闭后调用的自动重连函数'''
        interval = 5 # 重试时间间隔
        self.retrys -= 1
        if self.retrys < 0: # 不再有重试次数
            print(f'[{self.get_connection}] 与 WebSocket 的连接已超时。')
            logger.warning(f'[{self.get_connection}] 与 WebSocket 的连接已超时。')
            self.ws.close()
            return
        while interval > 0:
            print(f'{interval} s 后尝试重新连接...')
            sleep(1)
            interval -= 1
        print(f'尝试重新连接 WebSocket 服务器，剩余重试次数：{self.retrys}')
        logger.info(f'尝试重新连接 WebSocket 服务器，剩余重试次数：{self.retrys}')
        self._connect()
    
    # 连接 WebSocket 服务器
    def _connect(self) -> None:
        '''连接 WebSocket 服务器'''
        # 创建并运行线程发送心跳保活
        Thread(target=self._heartbeat, daemon=True).start()
        # 运行 WebSocketApp 对象
        try:
            self.ws.run_forever()
        except Exception as exception:
            info = f'连接 WebSocket 服务器时失败: {type(exception).__name__}: {exception}'
            print(info)
            logger.error(exception)
    
    # 创建 Adapter
    @classmethod
    def setup(
        cls,
        config: Config,
        serve: Literal['WebSocket', 'WebHook', 'Dev']='WebSocket'
    ) -> 'Adapter':
        '''创建 Adapter

        参数:
            config (Config): 机器人配置
            serve (Literal[&#39;WebSocket&#39;, &#39;WebHook&#39;, &#39;Dev&#39;], optional): 服务类型

        返回:
            Adapter: Satori 适配器
        '''
        adapter = cls(config)
        # 创建 HTTP 客户端实例
        adapter.http = httpx.Client(verify=True)
        # 如果需要创建 WebSocket 客户端
        if serve in ('WebSocket', 'Dev'):
            # 创建 WebSocket 客户端
            adapter.ws = websocket.WebSocketApp(
                'ws://{}{}/v{}/events'.format(
                    adapter.api_base,
                    adapter.config.path,
                    adapter.config.version
                ),
                on_open=adapter._on_open,
                on_message=adapter._on_message,
                on_close=adapter._on_close
            )
            Thread(target=adapter._connect).start()
        elif serve == 'WebHook': # 配置 WebHook 机器人对象
            if config.webhook_url is not None:
                # 创建 Webhook 客户端实例
                adapter.webhook_client = httpx.Client(
                    base_url='{}'.format(
                        config.webhook_url
                    )
                )
            return adapter
        if serve == 'Dev':
            if config.webhook_url is not None:
                # 创建 Webhook 客户端实例
                adapter.webhook_client = httpx.Client(
                    base_url='{}'.format(
                        config.webhook_url
                    )
                )
        return adapter
    
    # 处理从 flask.request 接收的 json 信息
    @override
    def handle_request(self, request: str) -> None:
        payload: dict[str, Any] = json.loads(request)
        if payload['op'] == 0: # 事件信令
            try:
                signaling = EventSignaling.model_validate(payload)
            except Exception as exception:
                print(f'{type(exception).__name__}: {exception}')
                return
        elif payload['op'] == 2: # 心跳回复信令
            signaling = Pong.model_validate(payload)
        elif payload['op'] == 4: # 鉴权回复信令
            signaling = Ready.model_validate(payload)
        else:
            print('未知的信令类型：{}'.format(payload['op']))
            return
        # 分情况处理信令
        if isinstance(signaling, Pong):
            pass
        elif isinstance(signaling, Ready):
            logins = signaling.body.logins
            self._bot_connect(logins)
        else:
            try:
                event = self.payload_to_event(signaling.body)
            except Exception as exception:
                print(f'{type(exception).__name__}: {exception}')
                logger.warning(f'将 payload 转换为事件时出错：{type(exception).__name__}: {exception}')
                logger.error(exception)
                return
            # 处理 LoginEvent
            if isinstance(event, LoginEvent):
                self._handle_login(event)
                return
            # 获取接收事件对应的机器人实例
            if event.self_id in self.bots.keys():
                bot = self.bots[event.self_id]
            # 如果没有则创建一个机器人并添加
            else:
                try:
                    bot = Bot.verify(
                        self,
                        event.self_id,
                        event.platform,
                        self.config
                    )
                    self.bots[event.self_id] = bot
                except Exception as exception:
                    print(f'机器人 {event.self_id} 验证失败：{type(exception).__name__}: {exception}')
                    return
            # 创建并运行一个子线程，处理事件（既然没有返回值那就不需要等待了罢！
            Thread(target=bot.handle_event, args=(event,), daemon=True).start()
        return
    
    # 当前适配器名称
    @classmethod
    @override
    def get_name(cls) -> str:
        return 'Satori'
    
    # 将信令转换为事件对象
    @staticmethod
    def payload_to_event(payload: SatoriEvent) -> Event:
        '''将信令转换为事件对象

        参数:
            payload (SatoriEvent): 信令数据

        返回:
            Event: 事件对象
        '''
        EventClass = EVENT_CLASSES.get(payload.type, None)
        if EventClass is None:
            print(f'未知的事件类型：{payload.type}')
            return Event.model_validate(payload)
        event = EventClass.model_validate(payload.model_dump())
        return event
    
    # Adapter 调用 API 实现
    @override
    def _call_api(self, bot: Bot, api: str, **data: Any) -> Response:
        headers = bot.get_authorization_header()
        url = f'http://{self.api_base}{self.config.path}/v{self.config.version}/{api}'
        response = self.http.post(url, data=cast(dict, json.dumps(data)), headers=headers)
        return response
