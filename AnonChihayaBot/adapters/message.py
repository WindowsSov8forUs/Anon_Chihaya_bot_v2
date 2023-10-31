'''Anon Chihaya 框架适配器
基础消息类型定义
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
import abc
import warnings
from copy import deepcopy
from pydantic import parse_obj_as
from collections.abc import Iterable
from dataclasses import dataclass, asdict, field
from typing import Iterable, Optional, Generic, TypeVar, Union, Type, overload, Any

# 屏蔽可能的警告
warnings.filterwarnings('ignore')

# 定义类型变量
T = TypeVar('T')
TM = TypeVar('TM', bound='Message')
TMS = TypeVar('TMS', bound='MessageSegment')

# 消息段基类
@dataclass
class MessageSegment(abc.ABC, Generic[TM]):
    '''消息段基类

    参数:
        type (str): 消息段类型
        data (dict[str, Any]): 消息段数据
    '''
    type: str
    '''消息段类型'''
    data: dict[str, Any]=field(default_factory=dict)
    '''消息段数据'''
    # 获取消息数组类型
    @classmethod
    @abc.abstractmethod
    def get_message_class(cls) -> Type[TM]:
        '''获取消息数组类型'''
        raise NotImplementedError
    
    # 定义 str(A) 行为
    @abc.abstractmethod
    def __str__(self) -> str:
        '''定义 `str(A)` 行为'''
        raise NotImplementedError
    
    # 定义 len(A) 行为
    def __len__(self) -> int:
        '''定义 `len(A)` 行为'''
        return len(str(self))
    
    # 定义 A != B 行为
    def __ne__(self: T, other: T) -> bool:
        '''定义 `A != B` 行为'''
        return not self == other
    
    # 定义 A + B 行为
    def __add__(self: TMS, other: Union[str, TMS, Iterable[TMS]]) -> TM:
        '''定义 `A + B` 行为'''
        return self.get_message_class()(self) + other
    
    # 定义 B + A 行为
    def __radd__(self: TMS, other: Union[str, TMS, Iterable[TMS]]) -> TM:
        '''定义 `B + A` 行为'''
        return self.get_message_class()(other) + self
    
    # 返回生成器
    @classmethod
    def __get_validators__(cls):
        '''返回生成器'''
        yield cls._validate
    
    # 验证函数
    @classmethod
    def _validate(cls, value: Any):
        '''验证函数'''
        if isinstance(value, cls):
            return value
        if not isinstance(value, dict):
            raise ValueError(f'MessageSegment 需要 dict 对象，而不是 {type(value)}。')
        if 'type' not in value:
            raise ValueError(f'字典中不存在必须的 \'type\' 字段：{value}。')
        return cls(type=value['type'], data=value.get('data', {}))
    
    # 获取对象内数据
    def get(self, key: str, default: Any=None) -> Any:
        '''获取对象内数据'''
        return asdict(self).get(key, default)
    
    # 获取对象键
    def keys(self):
        '''获取对象键'''
        return asdict(self).keys()
    
    # 获取对象值
    def values(self):
        '''获取对象值'''
        return asdict(self).values()
    
    # 获取对象物件
    def items(self):
        '''获取对象物件'''
        return asdict(self).items()
    
    # 重写拷贝方法
    def copy(self: T) -> T:
        '''返回深拷贝对象'''
        return deepcopy(self)

    # 当前消息段是否为纯文本
    @abc.abstractmethod
    def is_text(self) -> bool:
        '''当前消息段是否为纯文本'''
        raise NotImplementedError

    # 日志字符串
    @abc.abstractmethod
    def get_log(self) -> str:
        '''日志字符串'''
        raise NotImplementedError

# 消息数组
class Message(list[TMS], abc.ABC):
    '''消息数组'''
    # 消息数组初始化方法
    def __init__(self, message: Union[str, Iterable[TMS], TMS, None]=None) -> None:
        '''初始化方法'''
        super().__init__()
        if message is None:
            return
        elif isinstance(message, str):
            self.extend(self._construct(message))
        elif isinstance(message, MessageSegment):
            self.append(message)
        elif isinstance(message, Iterable):
            self.extend(message)
        else:
            self.extend(self._construct(message))
    
    # 获取消息段类型
    @classmethod
    @abc.abstractmethod
    def get_segment_class(cls) -> Type[TMS]:
        '''获取消息段类型'''
        raise NotImplementedError
    
    # 定义 str(A) 行为
    def __str__(self) -> str:
        '''定义 `str(A)` 行为'''
        return ''.join(str(segment) for segment in self)
    
    # 返回生成器
    @classmethod
    def __get_validators__(cls):
        '''返回生成器'''
        yield cls._validate
    
    # 验证函数
    @classmethod
    def _validate(cls, value: Any):
        '''验证函数'''
        if isinstance(value, cls):
            return value
        elif isinstance(value, Message):
            raise ValueError(f'{type(value)} 不能被转为 {cls}。')
        elif isinstance(value, str):
            pass
        elif isinstance(value, dict):
            try:
                value = parse_obj_as(cls.get_segment_class()) # type: ignore
            except:
                raise ValueError(f'pydantic.parse_obj_as() 方法在处理 {type(value)} 对象时出错。')
        elif isinstance(value, Iterable):
            try:
                value = [parse_obj_as(cls.get_segment_class(), v) for v in value]
            except:
                raise ValueError(f'pydantic.parse_obj_as() 方法在处理 {type(value)} 对象时出错。')
        else:
            raise ValueError(f'{type(value)} 无法被验证。')
        return cls(value)
    
    # 构造消息数组
    @staticmethod
    @abc.abstractmethod
    def _construct(message: str) -> Iterable[TMS]:
        '''构造消息数组'''
        raise NotImplementedError
    
    # 定义 A + B 行为
    def __add__(self: TM, other: Union[str, TMS, Iterable[TMS]]) -> TM:
        '''定义 `A + B` 行为'''
        result = self.copy()
        result += other
        return result
    
    # 定义 B + A 行为
    def __radd__(self: TM, other: Union[str, TMS, Iterable[TMS]]) -> TM:
        '''定义 `B + A` 行为'''
        result = self.__class__(other)
        return result + self
    
    # 定义 A += B 行为
    def __iadd__(self: TM, other: Union[str, TMS, Iterable[TMS]]) -> TM:
        '''定义 `A += B` 行为'''
        if isinstance(other, str):
            self.extend(self._construct(other))
        elif isinstance(other, MessageSegment):
            self.append(other)
        elif isinstance(other, Iterable):
            self.extend(other)
        else:
            raise TypeError(f'不支持的数据类型：{type(other)}。')
        return self
    
    @overload
    def __getitem__(self: TM, __args: str) -> TM:
        '''索引切片行为

        参数:
            __args (str): 消息段类型

        返回:
            TM: 所有类型为 `__args` 的消息段
        '''
    
    @overload
    def __getitem__(self, __args: tuple[str, int]) -> TMS:
        '''索引切片行为

        参数:
            __args (tuple[str, int]): 消息段类型和索引

        返回:
            TMS: 类型为 `__args[0]` 的消息段第 `__args[1]` 个
        '''
    
    @overload
    def __getitem__(self: TM, __args: tuple[str, slice]) -> TM:
        '''索引切片行为

        参数:
            __args (tuple[str, slice]): 消息段类型和切片

        返回:
            TM: 类型为 `__args` 的消息段切片 `__args[1]`
        '''
    
    @overload
    def __getitem__(self, __args: int) -> TMS:
        '''索引切片行为

        参数:
            __args (int): 索引

        返回:
            TMS: 第 `__args` 个消息段
        '''
    
    @overload
    def __getitem__(self: TM, __args: slice) -> TM:
        '''索引切片行为

        参数:
            __args (slice): 切片

        返回:
            TM: 消息切片 `__args`
        '''
    
    # 定义索引切片行为
    def __getitem__(
        self: TM,
        args: Union[str, tuple[str, int], tuple[str, slice], int, slice]
    ) -> Union[TMS, TM]:
        '''索引切片行为'''
        arg1, arg2 = args if isinstance(args, tuple) else (args, None)
        if isinstance(arg1, int) and arg2 is None:
            return super().__getitem__(arg1)
        elif isinstance(arg1, slice) and arg2 is None:
            return self.__class__(super().__getitem__(arg1))
        elif isinstance(arg1, str) and arg2 is None:
            return self.__class__(segment for segment in self if segment.type == arg1)
        elif isinstance(arg1, str) and isinstance(arg2, int):
            return [segment for segment in self if segment.type == arg1][arg2]
        elif isinstance(arg1, str) and isinstance(arg2, slice):
            return self.__class__([segment for segment in self if segment.type == arg1][arg2])
        else:
            raise ValueError('错误的参数或切片。')
    
    # 定义匹配索引位置行为
    def index(self, value: Union[TMS, str], *args) -> int:
        '''返回符合某个值的第一个索引'''
        if isinstance(value, str):
            first_segment = next((segment for segment in self if segment.type == value), None)
            if first_segment is None:
                raise ValueError(f'消息中不存在类型为 {value} 的消息段。')
            return super().index(first_segment, *args)
        return super().index(value, *args)
    
    # 获取消息中某个类型的所有消息段
    def get(self: TM, type_: str, count: Optional[int]=None) -> TM:
        '''获取消息中某个类型的所有消息段

        参数:
            type_ (str): 消息类型
            count (Optional[int], optional): 要获取的数量

        返回:
            TM: 获取到的消息
        '''
        if count is None:
            return self[type_]
        
        iterator, filtered = (
            segment for segment in self if segment.type == type_
        ), self.__class__()
        for _ in range(count): # 遍历
            segment = next(iterator, None)
            if segment is None:
                break
            filtered.append(segment)
        return filtered
    
    # 计数消息中符合要求的消息段数量
    def count(self, value: Union[TMS, str]) -> int:
        '''计数消息中符合要求的消息段数量

        参数:
            value (Union[TMS, str]): 消息段类型或消息段

        返回:
            int: 计数的数量
        '''
        return len(self[value]) if isinstance(value, str) else super().count(value)
    
    # 添加一个消息段到消息数组末尾
    def append(self: TM, obj: Union[str, TMS]) -> TM:
        '''添加一个消息段到消息数组末尾

        参数:
            obj (Union[str, TMS]): 要添加的消息段

        返回:
            TM: 添加后的消息数组
        '''
        if isinstance(obj, MessageSegment):
            super().append(obj)
        elif isinstance(obj, str):
            self.extend(self._construct(obj))
        else:
            raise ValueError(f'不支持的消息段类型：{type(obj)}')
        return self
    
    # 拼接一个消息数组或多个消息段到消息数组末尾
    def extend(self: TM, obj: Union[TM, Iterable[TMS]]) -> TM:
        '''拼接一个消息数组或多个消息段到消息数组末尾

        参数:
            obj (Union[TM, Iterable[TMS]]): 要添加的消息数组

        返回:
            TM: 添加后的消息段
        '''
        for segment in obj:
            self.append(segment)
        return self
    
    # 定义复制方法
    def copy(self: TM) -> TM:
        '''返回对象的深复制对象'''
        return deepcopy(self)
    
    # 提取消息内纯文本消息
    def extract_plain_text(self) -> str:
        '''提取消息内纯文本消息'''
        return ''.join(str(segment) for segment in self if segment.is_text()).strip()

    # 判断是否为纯字符串
    def is_text(self) -> bool:
        '''判断是否为纯字符串

        返回:
            bool: 是否为纯字符串
        '''
        for seg in self:
            if not seg.is_text():
                return False
        return True
    
    # 日志字符串
    @property
    def log(self) -> str:
        '''日志字符串'''
        return ' '.join(segment.get_log() for segment in self).strip()

# 自动生成文档
__autodoc__ = {
    'MessageSegment.__str__': True,
    'MessageSegment.__add__': True,
    'Message.__getitem__': True,
    'Message._construct': True,
}
