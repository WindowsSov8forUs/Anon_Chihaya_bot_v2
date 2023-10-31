'''机器人屏蔽管理'''
import os
from typing import Literal
from pydantic import BaseModel

from AnonChihayaBot.utils import Json
from AnonChihayaBot._plugin import find_plugin, find_function

# 获取屏蔽词条存储文件路径
BAN_DIR = os.path.dirname(__file__) + '/ban_info.json'

# 屏蔽信息类
class BanInfo(BaseModel):
    '''屏蔽信息类'''
    platform: list[str]=[]
    '''平台屏蔽项'''
    user: list[str]=[]
    '''用户屏蔽项'''
    guild: list[str]=[]
    '''群组屏蔽项'''
    plugin: dict[str, list[str]]={}
    '''插件屏蔽项'''
    function: dict[str, list[str]]={}
    '''功能屏蔽项'''

# 屏蔽管理类
class BanManager():
    '''屏蔽管理类'''
    in_use: bool = False
    '''正在处理中'''
    # 获取屏蔽信息
    @classmethod
    def _get_info(cls) -> BanInfo:
        '''获取屏蔽信息'''
        return BanInfo.model_validate(Json.read_to_dict(BAN_DIR))
    
    # 保存屏蔽信息
    @classmethod
    def _save_info(cls, info: BanInfo) -> None:
        '''保存屏蔽信息'''
        # 保存屏蔽信息
        Json.write(BAN_DIR, info.model_dump())
        return
    
    # 判断插件是否被屏蔽
    @classmethod
    def is_plugin_banned(cls, guild: str, plugin: str) -> bool:
        '''判断插件是否被屏蔽

        参数:
            guild (str): 群组号
            plugin (str): 插件名

        返回:
            bool: 是否被屏蔽
        '''
        # 检查是否正在被使用
        while cls.in_use: continue
        cls.in_use = True
        # 获取屏蔽信息
        ban_info = cls._get_info()
        cls.in_use = False
        # 判断是否有对应群组插件屏蔽信息
        if not guild in ban_info.plugin.keys():
            return False
        else:
            # 判断是否在对应群组被屏蔽
            if plugin in ban_info.plugin[guild]:
                return True
            else:
                return False
    
    # 判断功能是否被屏蔽
    @classmethod
    def is_function_banned(cls, guild: str, function: str) -> bool:
        '''判断插件是否被屏蔽

        参数:
            guild (str): 群组号
            function (str): 功能名

        返回:
            bool: 是否被屏蔽
        '''
        # 检查是否正在被使用
        while cls.in_use: continue
        cls.in_use = True
        # 获取屏蔽信息
        ban_info = cls._get_info()
        cls.in_use = False
        # 判断是否有对应群组插件屏蔽信息
        if not guild in ban_info.function.keys():
            return False
        else:
            # 判断是否在对应群组被屏蔽
            if function in ban_info.function[guild]:
                return True
            else:
                return False
    
    # 判断对象是否被屏蔽
    @classmethod
    def is_target_banned(
        cls,
        type_: Literal['platform', 'guild', 'user'],
        target: str
    ) -> bool:
        '''判断对象是否被屏蔽

        参数:
            type_ (Literal[&#39;platform&#39;, &#39;guild&#39;, &#39;user&#39;]): 对象种类
            target (str): 对象数据 (平台名称/用户 ID/群组 ID)

        返回:
            bool: 是否被屏蔽
        '''
        # 检查是否正在被使用
        while cls.in_use: continue
        cls.in_use = True
        # 获取屏蔽信息
        ban_info = cls._get_info()
        cls.in_use = False
        # 根据 type_ 分类判断
        if type_ == 'platform': # 平台
            return target in ban_info.platform
        elif type_ == 'user': # 用户
            return target in ban_info.user
        elif type_ == 'guild': # 群组
            return target in ban_info.guild
    
    # 屏蔽指定插件或功能
    @classmethod
    def ban(cls, guild: str, name: str) -> str:
        '''屏蔽指定插件或功能

        参数:
            guild (str): 群组 ID
            name (str): 插件或功能名
        返回:
            str: 处理结果
        '''
        # 查找对应的插件
        try:
            plugin = find_plugin(name)
            # 判断插件是否已被屏蔽
            if cls.is_plugin_banned(guild, plugin.package_name):
                return f'<!> 插件 {plugin.name} 已在该群被屏蔽。'
            # 检查是否正被使用
            while cls.in_use: continue
            cls.in_use = True
            # 获取屏蔽信息
            ban_info = cls._get_info()
            if ban_info.plugin.get(guild) is None:
                ban_info.plugin[guild] = []
            ban_info.plugin[guild].append(plugin.package_name)
            # 尝试保存屏蔽信息
            try:
                cls._save_info(ban_info)
                return f'<√> 插件 {plugin.name} 已被屏蔽。'
            except Exception as exception:
                return f'<×> 插件 {plugin.name} 屏蔽失败：\n{type(exception).__name__}: {exception}'
            finally:
                cls.in_use = False
        except ValueError: # 尝试查找对应功能
            try:
                function = find_function(name)
                # 判断功能是否已被屏蔽
                if cls.is_function_banned(guild, function.inner_name):
                    return f'<!> 功能 {function.name} 已在该群被屏蔽。'
                # 检查是否正被使用
                while cls.in_use: continue
                cls.in_use = True
                # 获取屏蔽信息
                ban_info = cls._get_info()
                if ban_info.function.get(guild) is None:
                    ban_info.function[guild] = []
                ban_info.function[guild].append(function.inner_name)
                # 尝试保存屏蔽信息
                try:
                    cls._save_info(ban_info)
                    return f'<√> 功能 {function.name} 已被屏蔽。'
                except Exception as exception:
                    return f'<×> 功能 {function.name} 屏蔽失败：\n{type(exception).__name__}: {exception}'
                finally:
                    cls.in_use = False
            except ValueError:
                return f'<×> 插件或功能 {name} 未找到。'
        except Exception as exception:
            return f'<×> 尝试屏蔽 {name} 时出错：\n{type(exception).__name__}: {exception}'
    
    # 解除指定插件或功能屏蔽
    @classmethod
    def unban(cls, guild: str, name: str) -> str:
        '''解除指定插件或功能屏蔽

        参数:
            guild (str): 群组 ID
            name (str): 插件或功能名
        返回:
            str: 处理结果
        '''
        # 查找对应的插件
        try:
            plugin = find_plugin(name)
            # 判断插件是否已被屏蔽
            if not cls.is_plugin_banned(guild, plugin.package_name):
                return f'<!> 插件 {plugin.name} 未在该群被屏蔽。'
            # 检查是否正被使用
            while cls.in_use: continue
            cls.in_use = True
            # 获取屏蔽信息
            ban_info = cls._get_info()
            ban_info.plugin[guild].remove(plugin.package_name)
            # 尝试保存屏蔽信息
            try:
                cls._save_info(ban_info)
                return f'<√> 已解除插件 {plugin.name} 的屏蔽。'
            except Exception as exception:
                return f'<×> 插件 {plugin.name} 屏蔽解除失败：\n{type(exception).__name__}: {exception}'
            finally:
                cls.in_use = False
        except ValueError: # 尝试查找对应的功能
            try:
                function = find_function(name)
                # 判断功能是否已被屏蔽
                if not cls.is_function_banned(guild, function.inner_name):
                    return f'<!> 功能 {function.name} 未在该群被屏蔽。'
                # 检查是否正被使用
                while cls.in_use: continue
                cls.in_use = True
                # 获取屏蔽信息
                ban_info = cls._get_info()
                ban_info.function[guild].remove(function.inner_name)
                # 尝试保存屏蔽信息
                try:
                    cls._save_info(ban_info)
                    return f'<√> 已解除功能 {function.name} 的屏蔽。'
                except Exception as exception:
                    return f'<×> 功能 {function.name} 屏蔽解除失败：\n{type(exception).__name__}: {exception}'
                finally:
                    cls.in_use = False
            except ValueError:
                return f'<×> 插件或功能 {name} 未找到。'
        except Exception as exception:
            return f'<×> 尝试解除 {name} 屏蔽时出错：\n{type(exception).__name__}: {exception}'
    
    # 屏蔽指定对象
    @classmethod
    def ban_target(
        cls,
        type_: Literal['platform', 'user', 'guild'],
        target: str
    ) -> str:
        '''屏蔽指定对象

        参数:
            type_ (Literal[&#39;platform&#39;, &#39;guild&#39;, &#39;user&#39;]): 对象种类
            target (str): 对象数据 (平台名称/用户 ID/群组 ID)
        返回:
            str: 处理结果
        '''
        if type_ == 'guild': type_name = '群组'
        elif type_ == 'platform': type_name = '平台'
        elif type_ == 'user': type_name = '用户'
        # 判断是否已被屏蔽
        if cls.is_target_banned(type_, target):
            return f'<×> {type_name} {target} 已经被屏蔽。'
        # 检查是否正被使用
        while cls.in_use: continue
        cls.in_use = True
        # 获取屏蔽信息
        ban_info = cls._get_info()
        # 根据 type_ 分类操作
        if type_ == 'platform':
            ban_info.platform.append(target)
        elif type_ == 'user':
            if not target.isdigit():
                return f'<×> {target} 不是一个合法的{type_name}。'
            ban_info.user.append(target)
        elif type_ == 'guild':
            if not target.isdigit():
                return f'<×> {target} 不是一个合法的{type_name}。'
            ban_info.guild.append(target)
        # 尝试保存屏蔽信息
        try:
            cls._save_info(ban_info)
            return f'<√> {type_name} {target} 已屏蔽。'
        except Exception as exception:
            return f'<×> 屏蔽{type_name} {target} 时出现错误：\n{type(exception).__name__}: {exception}'
        finally:
            cls.in_use = False
    
    # 解除指定对象屏蔽
    @classmethod
    def unban_target(
        cls,
        type_: Literal['platform', 'user', 'guild'],
        target: str
    ) -> str:
        '''解除指定对象屏蔽

        参数:
            type_ (Literal[&#39;platform&#39;, &#39;guild&#39;, &#39;user&#39;]): 对象种类
            target (str): 对象数据 (平台名称/用户 ID/群组 ID)
        返回:
            str: 处理结果
        '''
        if type_ == 'guild': type_name = '群组'
        elif type_ == 'platform': type_name = '平台'
        elif type_ == 'user': type_name = '用户'
        # 判断是否已被屏蔽
        if not cls.is_target_banned(type_, target):
            return f'<×> {type_name} {target} 未被屏蔽。'
        # 检查是否正被使用
        while cls.in_use: continue
        cls.in_use = True
        # 获取屏蔽信息
        ban_info = cls._get_info()
        # 根据 type_ 分类操作
        if type_ == 'platform':
            ban_info.platform.remove(target)
        elif type_ == 'user':
            if not target.isdigit():
                return f'<×> {target} 不是一个合法的{type_name}。'
            ban_info.user.remove(target)
        elif type_ == 'guild':
            if not target.isdigit():
                return f'<×> {target} 不是一个合法的{type_name}。'
            ban_info.guild.remove(target)
        # 尝试保存屏蔽信息
        try:
            cls._save_info(ban_info)
            return f'<√> 已解除{type_name} {target} 的屏蔽。'
        except Exception as exception:
            return f'<×> 解除{type_name} {target} 的屏蔽时出现错误：\n{type(exception).__name__}: {exception}'
        finally:
            cls.in_use = False
