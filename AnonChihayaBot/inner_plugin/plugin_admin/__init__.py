'''机器人管理员管理'''
import os
from typing import Literal

from AnonChihayaBot.utils import Json

# 获取管理员存储文件路径
ADMIN_DIR = os.path.dirname(__file__) + '/admin.json'

# 管理员操作类
class Admin:
    '''管理员操作类'''
    in_use: bool = False
    '''正在处理中'''
    # 获取管理员列表
    @classmethod
    def _get_list(cls) -> list[str]:
        '''获取管理员列表'''
        # 获取管理员列表信息
        admin_list = Json.read_to_list(ADMIN_DIR)
        return admin_list
    
    # 保存管理员列表
    @classmethod
    def _save_list(cls, admin_list: list[str]) -> None:
        '''保存管理员列表'''
        # 保存管理员列表
        Json.write(ADMIN_DIR, admin_list)
        return
    
    # 检测是否为管理员
    @classmethod
    def is_admin(cls, user_id: str) -> bool:
        '''检测是否为管理员

        参数:
            user_id (str): 用户 ID

        返回:
            bool: 判断结果
        '''
        # 检测是否正在被使用
        while cls.in_use: continue
        cls.in_use = True
        # 获取管理员列表
        admin_list = cls._get_list()
        cls.in_use = False
        return user_id in admin_list
    
    # 添加管理员
    @classmethod
    def add(cls, user_id: str) -> str:
        '''添加管理员

        参数:
            user_id (str): 用户 ID

        返回:
            str: 处理结果
        '''
        # 判断是否已是管理员
        if cls.is_admin(user_id):
            return f'<!> 用户 {user_id} 已经是管理员了。'
        else:
            # 添加管理员并保存
            cls.in_use = True
            admin_list = cls._get_list()
            admin_list.append(user_id)
            try:
                cls._save_list(admin_list)
                return f'<√> 已将用户 {user_id} 设置为管理员。'
            except Exception as exception:
                return f'<×> 设置 {user_id} 为管理员时出错：\n{type(exception).__name__}: {exception}'
            finally:
                cls.in_use = False
    
    # 删除管理员
    @classmethod
    def remove(cls, user_id: str) -> str:
        '''删除管理员

        参数:
            user_id (str): 用户 ID

        返回:
            str: 处理结果
        '''
        # 判断是否已是管理员
        if not cls.is_admin(user_id):
            return f'<!> 用户 {user_id} 不是管理员。'
        else:
            # 删除管理员并保存
            cls.in_use = True
            admin_list = cls._get_list()
            admin_list.remove(user_id)
            try:
                cls._save_list(admin_list)
                return f'<√> 已将用户 {user_id} 管理员权限移除。'
            except Exception as exception:
                return f'<×> 移除 {user_id} 管理权限时出错：\n{type(exception).__name__}: {exception}'
            finally:
                cls.in_use = False
