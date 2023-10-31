'''Anon Chihaya 框架 Satori 协议适配器
机器人定义
'''
import time
from httpx import Response
from threading import Thread
from typing_extensions import override
from typing import Optional, Union, TYPE_CHECKING, Any

import AnonChihayaBot._plugin as plugin
from AnonChihayaBot.adapters import logger
from AnonChihayaBot.adapters import Bot as BaseBot
from AnonChihayaBot.adapters.utils import _schedule_run, _schedule_kill
from AnonChihayaBot.inner_plugin import (
    Admin, Ban,
    admin_process, ban_process, event_filter
)

from .config import Config
from .event import MessageEvent, Event
from .models import Message as SatoriMessage
from .message import MessageSegment, Message
from .models import GuildMember, Pagination, GuildRole, Channel, Guild, Login, User

if TYPE_CHECKING:
    from .adapter import Adapter

# 检查是否存在回复消息
def _check_reply(bot: 'Bot', event: MessageEvent) -> None:
    '''检查是否存在回复消息，并对 `event.reply` 赋值'''
    message = event.get_message() # 获取消息对象
    # 获取引用消息类型
    try:
        index = message.index('quote')
    except ValueError:
        return
    
    message_segment = message[index]
    event.reply = message_segment # type: ignore
    del message[index]
    
    # 处理消息
    if (
        len(message) > index
        and message[index].type == 'at'
        and message[index].data.get('id') == str(bot.self_info.id)
    ):
        del message[index]
    if len(message) > index and message[index].type == 'text':
        message[index].data['text'] = message[index].data['text'].lstrip()
        if message[index].data['index'] == '':
            del message[index]
    if not message:
        message.append(MessageSegment.text(''))

# 检查是否提及机器人
def _check_at_me(bot: 'Bot', event: MessageEvent) -> None:
    '''检查是否提及机器人，并对 `event.to_me` 赋值'''
    # 检查消息段是否为提及机器人
    def _is_at_me(segment: MessageSegment) -> bool:
        '''检查消息段是否为提及机器人'''
        return segment.type == 'at' and segment.data.get('id') == str(bot.self_info.id)
    
    message = event.get_message()
    
    # 确保消息不为空
    if not message:
        message.append(MessageSegment.text(''))
    
    delete_flag = False
    if _is_at_me(message[0]):
        message.pop(0)
        event.to_me = True
        delete_flag = True
        if message and message[0].type == 'text':
            message[0].data['text'] = message[0].data['text'].lstrip('\xa0').lstrip()
            if not message[0].data['text']:
                del message[0]
    
    # 若首位没有检查到则检查末位
    if not delete_flag:
        index = -1
        last_segment = message[index]
        if (
            last_segment.type == 'text'
            and last_segment.data['text'].strip() == ''
            and len(message) >= 2
        ):
            index -= 1
            last_segment = message[index]
        
        if _is_at_me(last_segment):
            event.to_me = True
            del message[index:]
    
    if not message:
        message.append(MessageSegment.text(''))

# Satori 机器人
class Bot(BaseBot):
    '''Satori 机器人

    参数:
        adapter (Adapter): `Satori.Adapter` 对象
        self_id (str): 机器人 ID
        platform (str): 机器人所在的平台
        config (Config): 机器人配置信息
    '''
    adapter: 'Adapter'
    '''Satori 协议适配器'''
    # 初始化方法
    @override
    def __init__(self, adapter: 'Adapter', self_id: str, platform: str, config: Config) -> None:
        '''Satori 机器人

        参数:
            adapter (Adapter): `Satori.Adapter` 对象
            self_id (str): 机器人 ID
            platform (str): 机器人所在的平台
            config (Config): 机器人配置信息
        '''
        super().__init__(adapter, self_id)
        
        # Bot 配置信息
        self.config: Config = config
        '''Bot 配置信息'''
        self.platform: str = platform
        '''Bot 所在平台'''
        self._info: Optional[User] = None
        '''Bot 自身信息'''
    
    # Bot 是否已连接
    @property
    def ready(self) -> bool:
        '''Bot 是否已连接'''
        return self._info is not None
    
    # Bot 自身信息
    @property
    def self_info(self) -> User:
        '''Bot 自身信息，若未完成鉴权则不可用'''
        if self._info is None:
            raise RuntimeError(f'机器人 {self.self_id} 未连接至平台 {self.platform}')
        return self._info
    
    # 处理响应
    def _handle_response(self, response: Response) -> Any:
        '''处理响应'''
        if 200 <= response.status_code < 300: # 响应正常
            return response.json()
        # 错误响应
        elif response.status_code == 400:
            raise Exception('请求格式错误。(400 Bad Request)')
        elif response.status_code == 401:
            raise Exception('缺失鉴权。(401 Unauthorized)')
        elif response.status_code == 403:
            raise Exception('权限不足。(403 Forbidden)')
        elif response.status_code == 404:
            raise Exception('资源不存在。(404 Not Found)')
        elif response.status_code == 405:
            raise Exception('请求方法不支持。(405 Method Not Allowed)')
        elif 500 <= response.status_code < 600:
            raise Exception(f'服务器错误。({response.status_code} Server Error)')
        else:
            raise Exception(f'未知错误。({response.status_code})')
    
    # 验证并返回 Bot 实例
    @classmethod
    def verify(cls, adapter: 'Adapter', self_id: str, platform: str, config: Config) -> 'Bot':
        '''验证并返回 Bot 实例

        参数:
            adapter (Adapter): `Satori.Adapter` 对象
            self_id (str): 机器人 ID
            platform (str): 机器人所在的平台
            config (Config): 机器人配置信息

        返回:
            Bot: 验证后的 Bot 实例
        '''
        bot = cls(adapter, self_id, platform, config)
        # 获取机器人登录信息
        try:
            login = bot.login_get()
        except Exception as exception:
            raise exception
        # 确认 Bot 已连接
        if login.user is not None:
            bot.get_ready(login.user)
            login_info = (
                f'[{adapter.get_name()}|{login.self_id}] {login.user.name} 已连接到平台 {login.platform}'
            )
            print(login_info)
            logger.info(login_info)
            return bot
        else:
            raise ValueError(f'机器人 [{self_id}|{platform}] 验证失败：未成功获取用户对象。')
    
    # 确认 Bot 已连接
    def get_ready(self, user: User) -> None:
        '''确认 Bot 已连接

        参数:
            user (User): 机器人的 `Satori.User` 信息
        '''
        self._info = user
    
    # 获取 Bot 鉴权信息
    def get_authorization_header(self) -> dict[str, str]:
        '''获取 Bot 鉴权信息'''
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.config.token}',
            'X-Self-ID': self.self_id,
            'X-Platform': self.platform
        }
    
    # 处理接收到的事件
    def handle_event(self, event: Event) -> None:
        '''处理接收到的事件

        参数:
            event (Event): 接收到的事件
        '''
        if plugin._in_reloading(): # 如果正在重载插件
            while plugin._in_reloading():
                time.sleep(0.1)
        if len(plugin.plugins) <= 0: # 若无插件被加载
            try:
                plugin._plugin_reload()
                _schedule_run(self)
            except Exception as exception:
                print(f'{type(exception).__name__}: {exception}')
        logger.info(event.get_log())
        print(event.get_log())
        if isinstance(event, MessageEvent):
            _check_reply(self, event)
            _check_at_me(self, event)
            # 判断是否是 Admin 或 Ban 操作
            if (
                str(event.get_message()).startswith(('/admin', '/deadmin'))
                and event.get_user_id() == self.config.host_id
            ):
                try:
                    admin_process(self, event)
                except Exception as exception:
                    print(f'{type(exception).__name__}: {exception}')
                return
            elif (
                str(event.get_message()).startswith(('/ban', '/unban'))
                and (
                    event.get_user_id() == self.config.host_id,
                    Admin.is_admin(event.get_user_id())
                )
            ):
                ban_process(self, event)
                return
        if event_filter(self, event):
            # 判断是否为帮助
            if (message := str(event.get_message())).startswith('/help'):
                if message == '/help':
                    reply = 'Bot 可用的插件有：'
                    plugin_bans = Ban._get_info().plugin.get(event.get_guild_id(), [])
                    for plg in plugin.plugins:
                        if plg.package_name in plugin_bans:
                            reply += '\n>> [BANNED] '
                        else:
                            reply += '\n>> '
                        reply += f'{plg.name}: {plg.doc}'
                    self.send(event, reply + '\n发送 /help + 名称 获取对应帮助。')
                    return
                else:
                    plugin_name = message[5:].strip()
                    try: # 查找插件
                        plg = plugin.find_plugin(plugin_name)
                        reply = f'[{plg.name}]\n{plg.doc}'
                        for function in plg.functions:
                            reply += f'\n>> {function.name}: {function.desc}'
                        self.send(event, reply + '\n发送 /help + 名称 获取对应帮助。')
                        return
                    except ValueError:
                        # 创建帮助任务
                        tasks: list[Thread] = []
                        for plg in plugin.plugins:
                            for func in plg.functions:
                                tasks.append(
                                    Thread(target=func.function, args=(self, event), daemon=True)
                                )
                        
                        for task in tasks:
                            task.start()
                        return
                    
            if (
                str(event.get_message()).lower() == '/reload'
                and event.get_user_id() == self.config.host_id
            ):
                try:
                    _schedule_kill()
                    plugin._plugin_reload()
                    _schedule_run(self)
                    self.send(event, '<√> 插件已更新。')
                except Exception as exception:
                    self.send(event, f'<×> 插件更新失败：\n{type(exception).__name__}: {exception}')
                return
            # 创建任务列表
            tasks: list[Thread] = []
            for plg in plugin.plugins:
                if not Ban.is_plugin_banned(event.get_guild_id(), plg.package_name):
                    for func in plg.functions:
                        if not Ban.is_function_banned(event.get_guild_id(), func.inner_name):
                            tasks.append(
                                Thread(target=func.function, args=(self, event), daemon=True)
                            )
            
            for task in tasks:
                task.start()
            return
    
    # 发送消息
    @override
    def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        at_sender: bool=False,
        reply: bool=False
    ) -> list[SatoriMessage]:
        '''发送消息

        参数:
            event (Event): 要回复的事件
            message (Union[str, Message, MessageSegment]): 要发送的内容
            at_sender (bool, optional): 是否提及发送者
            reply (bool, optional): 是否回复该消息

        返回:
            list[SatoriMessage]: 一个 `Satori.SatoriMessage` 对象构成的数组
        '''
        if event.channel is None: # 如果没有频道
            raise TypeError(f'该事件 {type(event).__name__} 无法被回复。')
        if at_sender:
            try:
                user_id = event.get_user_id()
                message += MessageSegment.at(user_id)
            except:
                raise ValueError(f'该事件 {type(event).__name__} 没有发送者。')
        if reply:
            if event.message is not None:
                message = MessageSegment.quote(event.message.id) + message
            else:
                raise ValueError(f'该事件 {type(event).__name__} 不存在可回复的消息。')
        return self.message_create(event.channel.id, str(message))
    
    # 判断是否为主人
    @override
    def is_host(self, user_id: str) -> bool:
        return user_id == self.config.host_id
    
    # 发送 API 请求
    def request(self, api: str, **data: Any) -> Any:
        '''发送 API 请求

        参数:
            api (str): API 名称

        返回:
            Any: API 响应数据
        '''
        response = self.adapter._call_api(self, api, **data)
        return self._handle_response(response)
    
    # 获取群组频道
    def channel_get(self, channel_id: str) -> Channel:
        '''根据 ID 获取频道。

        参数:
            channel_id (str): 频道 ID

        返回:
            Channel: 一个 `Satori.Channel` 对象
        '''
        response = self.request(
            'channel.get',
            channel_id=channel_id
        )
        return Channel.model_validate(response)
    
    # 获取群组频道列表
    def channel_list(self, guild_id: str, next: str) -> Pagination[Channel]:
        '''获取群组中的全部频道。

        参数:
            guild_id (str): 群组 ID
            next (str): 分页令牌

        返回:
            Pagination[Channel]: 一个 `Satori.Channel` 的 `分页列表`
        '''
        response = self.request(
            'channel.list',
            guild_id=guild_id, next=next
        )
        return Pagination.pagination(Channel, **response)
    
    # 创建群组频道
    def channel_create(self, guild_id: str, data: Channel) -> Channel:
        '''创建群组频道。

        参数:
            guild_id (str): 群组 ID
            data (Channel): 频道数据

        返回:
            Channel: 一个 `Satori.Channel` 对象
        '''
        response = self.request(
            'channel.create',
            guild_id=guild_id, data=data
        )
        return Channel.model_validate(response)
    
    # 修改群组频道
    def channel_update(self, channel_id: str, data: Channel) -> None:
        '''修改群组频道。

        参数:
            channel_id (str): 频道 ID
            data (Channel): 频道数据
        '''
        self.request(
            'channel.update',
            channel_id=channel_id, data=data
        )
        return
    
    # 删除群组频道
    def channel_delete(self, channel_id: str) -> None:
        '''删除群组频道。

        参数:
            channel_id (str): 频道 ID
        '''
        self.request(
            'channel.delete',
            channel_id=channel_id
        )
        return
    
    # 创建私聊频道
    def user_channel_create(self, user_id: str, guild_id: Optional[str]=None) -> Channel:
        '''创建一个私聊频道。

        参数:
            user_id (str): 用户 ID
            guild_id (Optional[str], optional): 群组 ID

        返回:
            Channel: 一个 `Satori.Channel` 对象
        '''
        response = self.request(
            'user.channel.create',
            user_id=user_id, guild_id=guild_id
        )
        return Channel.model_validate(response)
    
    # 获取群组
    def guild_get(self, guild_id: str) -> Guild:
        '''根据 ID 获取。

        参数:
            guild_id (str): 群组 ID

        返回:
            Guild: 一个 `Satori.Guild` 对象
        '''
        response = self.request(
            'guild.get',
            guild_id=guild_id
        )
        return Guild.model_validate(response)
    
    # 获取群组列表
    def guild_list(self, next: str) -> Pagination[Guild]:
        '''获取当前用户加入的全部群组。

        参数:
            next (str): 分页令牌

        返回:
            Pagination[Guild]: 一个 `Satori.Guild` 的 `分页列表`
        '''
        response = self.request(
            'guild.list',
            next=next
        )
        return Pagination.pagination(Guild, **response)
    
    # 处理群组邀请
    def guild_approve(self, message_id: str, approve: bool, comment: str) -> None:
        '''处理来自群组的邀请。

        参数:
            message_id (str): 请求 ID
            approve (bool): 是否通过请求
            comment (str): 备注信息
        '''
        self.request(
            'guild.approve',
            message_id=message_id, approve=approve, comment=comment
        )
        return
    
    # 获取群组成员
    def guild_member_get(self, guild_id: str, user_id: str) -> GuildMember:
        '''获取群成员信息。

        参数:
            guild_id (str): 群组 ID
            user_id (str): 用户 ID

        返回:
            GuildMember: 一个 `Satori.GuildMember` 对象
        '''
        response = self.request(
            'guild.member.get',
            guild_id=guild_id, user_id=user_id
        )
        return GuildMember.model_validate(response)
    
    # 获取群组成员列表
    def guild_member_list(self, guild_id: str, next: str) -> Pagination[GuildMember]:
        '''获取群成员列表。

        参数:
            guild_id (str): 群组 ID
            next (str): 分页令牌

        返回:
            Pagination[GuildMember]: 一个 `Satori.GuildMember` 的 `分页列表`
        '''
        response = self.request(
            'guild.member.list',
            guild_id=guild_id, next=next
        )
        return Pagination.pagination(GuildMember, **response)
    
    # 踢出群组成员
    def guild_member_kick(
        self,
        guild_id: str,
        user_id: str,
        permanent: Optional[bool]=None
    ) -> None:
        '''将某个用户踢出群组。

        参数:
            guild_id (str): 群组 ID
            user_id (str): 用户 ID
            permanent (Optional[bool], optional): 是否永久踢出 (无法再次加入群组)
        '''
        self.request(
            'guild.member.kick',
            guild_id=guild_id, user_id=user_id, permanent=permanent
        )
        return
    
    # 通过群组成员申请
    def guild_member_approve(
        self,
        message_id: str,
        approve: bool,
        comment: Optional[str]=None
    ) -> None:
        '''处理加群请求。

        参数:
            message_id (str): 请求 ID
            approve (bool): 是否通过请求
            comment (Optional[str], optional): 备注信息
        '''
        self.request(
            'guild.member.approve',
            message_id=message_id, approve=approve, comment=comment
        )
        return
    
    # 设置群组成员角色
    def guild_member_role_set(
        self,
        guild_id: str,
        user_id: str,
        role_id: str
    ) -> None:
        '''设置群组内用户的角色。

        参数:
            guild_id (str): 群组 ID
            user_id (str): 用户 ID
            role_id (str): 角色 ID
        '''
        self.request(
            'guild.member.role.set',
            guild_id=guild_id, user_id=user_id, role_id=role_id
        )
        return
    
    # 取消群组成员角色
    def guild_member_role_unset(
        self,
        guild_id: str,
        user_id: str,
        role_id: str
    ) -> None:
        '''取消群组内用户的角色。

        参数:
            guild_id (str): 群组 ID
            user_id (str): 用户 ID
            role_id (str): 角色 ID
        '''
        self.request(
            'guild.member.role.unset',
            guild_id=guild_id, user_id=user_id, role_id=role_id
        )
        return
    
    # 获取群组角色列表
    def guild_role_list(self, guild_id: str, next: Optional[str]=None) -> Pagination[GuildRole]:
        '''获取群组角色列表。

        参数:
            guild_id (str): 群组 ID
            next (Optional[str], optional): 分页令牌

        返回:
            Pagination[GuildRole]: 一个 `Satori.GuildRole` 的 `分页列表`
        '''
        response = self.request(
            'guild.role.list',
            guild_id=guild_id, next=next
        )
        return Pagination.pagination(GuildRole, **response)
    
    # 创建群组角色
    def guild_role_create(self, guild_id: str, role: GuildRole) -> GuildRole:
        '''创建群组角色。

        参数:
            guild_id (str): 群组 ID
            role (GuildRole): 角色数据

        返回:
            GuildRole: 一个 `Satori.GuildRole` 对象
        '''
        response = self.request(
            'guild.role.create',
            guild_id=guild_id, role=role
        )
        return GuildRole.model_validate(response)
    
    # 修改群组角色
    def guild_role_update(
        self,
        guild_id: str,
        role_id: str,
        role: GuildRole
    ) -> None:
        '''修改群组角色。

        参数:
            guild_id (str): 群组 ID
            role_id (str): 角色 ID
            role (GuildRole): 角色数据
        '''
        self.request(
            'guild.role.update',
            guild_id=guild_id, role_id=role_id, role=role
        )
        return
    
    # 删除群组角色
    def guild_role_delete(self, guild_id: str, role_id: str) -> None:
        '''删除群组角色。

        参数:
            guild_id (str): 群组 ID
            role_id (str): 角色 ID
        '''
        self.request(
            'guild.role.delete',
            guild_id=guild_id, role_id=role_id
        )
        return
    
    # 获取登录信息
    def login_get(self) -> Login:
        '''获取登录信息。

        返回:
            Login: 一个 `Satori.Login` 对象
        '''
        response = self.request('login.get')
        return Login.model_validate(response)
    
    # 发送消息
    def message_create(self, channel_id: str, content: str) -> list[SatoriMessage]:
        '''发送消息。

        参数:
            channel_id (str): 频道 ID
            content (str): 消息内容

        返回:
            list[SatoriMessage]: 一个 `Satori.SatoriMessage` 对象构成的数组
        '''
        response: list[Any] = self.request(
            'message.create',
            channel_id=channel_id, content=content
        )
        return [SatoriMessage.model_validate(data) for data in response]
    
    # 获取消息
    def message_get(self, channel_id: str, message_id: str) -> SatoriMessage:
        '''获取特定消息。

        参数:
            channel_id (str): 频道 ID
            message_id (str): 消息 ID

        返回:
            SatoriMessage: 一个 `Satori.SatoriMessage` 对象
        '''
        response = self.request(
            'message.get',
            channel_id=channel_id, message_id=message_id
        )
        return SatoriMessage.model_validate(response)
    
    # 撤回消息
    def message_delete(self, channel_id: str, message_id: str) -> None:
        '''撤回特定消息。

        参数:
            channel_id (str): 频道 ID
            message_id (str): 消息 ID
        '''
        self.request(
            'message.delete',
            channel_id=channel_id, message_id=message_id
        )
        return
    
    # 编辑消息
    def message_update(
        self,
        channel_id: str,
        message_id: str,
        content: str
    ) -> None:
        '''编辑特定消息。

        参数:
            channel_id (str): 频道 ID
            message_id (str): 消息 ID
            content (str): 消息内容
        '''
        self.request(
            'message.update',
            channel_id=channel_id, message_id=message_id, content=content
        )
        return
    
    # 获取消息列表
    def message_list(self, channel_id: str, next: str) -> Pagination[SatoriMessage]:
        '''获取频道消息列表。

        参数:
            channel_id (str): 频道 ID
            next (str): 分页令牌

        返回:
            Pagination[SatoriMessage]: 一个 `Satori.SatoriMessage` 的 `分页列表`
        '''
        response = self.request(
            'message.list',
            channel_id=channel_id, next=next
        )
        return Pagination.pagination(SatoriMessage, **response)
    
    # 获取用户信息
    def user_get(self, user_id: str) -> User:
        '''获取用户信息。

        参数:
            user_id (str): 用户 ID

        返回:
            User: 一个 `Satori.User` 对象
        '''
        response = self.request(
            'user.get',
            user_id=user_id
        )
        return User.model_validate(response)
    
    # 获取好友列表
    def friend_list(self, next: Optional[str]=None) -> Pagination[User]:
        '''获取好友列表。

        参数:
            next (Optional[str], optional): 分页令牌

        返回:
            Pagination[User]: 一个 `Satori.User` 的 `分页列表`
        '''
        response = self.request(
            'friend.list',
            next=next
        )
        return Pagination.pagination(User, **response)
    
    # 处理好友申请
    def friend_approve(
        self,
        message_id: str,
        approve: bool,
        comment: Optional[str]=None
    ) -> None:
        '''处理好友申请。

        参数:
            message_id (str): 请求 ID
            approve (bool): 是否通过请求
            comment (Optional[str], optional): 备注信息
        '''
        self.request(
            'friend.approve',
            message_id=message_id, approve=approve, comment=comment
        )
        return

    # 内部 API
    def internal(self, method: str, **data: Any) -> Any:
        '''内部 API

        参数:
            method (str): 内部 API 方法

        返回:
            Any: 内部 API 响应数据
        '''
        response = self.request(
            f'internal/{method}',
            **data
        )
        return response
