'''Anon Chihaya 框架适配器
杂项定义，包含了自建日志对象 `Logging` 以及 `json` 操作对象 `MyJson` 等方法
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
import os
import json
import inspect
import threading
import traceback
from time import sleep
from datetime import datetime, timedelta
from typing import Callable, Optional, Literal, TypeVar, Union, overload, Any

from .bot import Bot as BaseBot
from .event import Event as BaseEvent

# 获取 log 目录所在父目录
LOG_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# 创建类型变量
Bot = TypeVar('Bot', bound=BaseBot)
Event = TypeVar('Event', bound=BaseEvent)

# 插件功能函数类型
FunctionLike = Callable[[Bot, Event], None]
# 插件装饰器函数类型
Decorater = Callable[[FunctionLike], FunctionLike]
# 定时任务函数类型
ScheduledFunction = Callable[[Bot], None]
# 定时器装饰器函数类型
Scheduler = Callable[[ScheduledFunction], ScheduledFunction]

# 插件功能列表
function_list: list['Function'] = []
# 定时任务列表
schedule_list: list['Schedule'] = []

# json 文件读写类
class MyJson:
    '''json 文件读写类'''
    locks: dict[str, threading.Lock] = {}
    '''文件锁字典'''
    
    # json 文件读取为字典
    @classmethod
    def read_to_dict(cls, file_name: str) -> dict[str, Any]:
        '''读取 `.json` 文件为字典

        参数:
            file_name (str): 要读取的文件路径

        返回:
            dict[str, Any]: 文件内容
        '''
        # 判断文件是否已有线程锁对象，如果没有则创建一个
        if not file_name in list(cls.locks.keys()):
            cls.locks[file_name] = threading.Lock()
            
        # 获取对应的线程锁对象
        lock = cls.locks[file_name]
        # 尝试获取线程锁
        lock.acquire()
        
        # 检测文件是否存在
        if not os.path.exists(file_name):
            data = {}
            with open(file_name, 'w+', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return data
        
        # 尝试进行文件操作
        try:
            with open(file_name, 'r+', encoding='utf-8') as file:
                data = json.load(file)
        except Exception as exception:
            raise exception
        else:
            return data
        finally:
            # 释放线程锁
            lock.release()
            
    # json 文件读取为列表
    @classmethod
    def read_to_list(cls, file_name: str) -> list[Any]:
        '''读取 `.json` 文件为列表

        参数:
            file_name (str): 要读取的文件路径

        返回:
            list[Any]: 文件内容
        '''
        # 判断文件是否已有线程锁对象，如果没有则创建一个
        if not file_name in list(cls.locks.keys()):
            cls.locks[file_name] = threading.Lock()
            
        # 获取对应的线程锁对象
        lock = cls.locks[file_name]
        # 尝试获取线程锁
        lock.acquire()
        
        # 检测文件是否存在
        if not os.path.exists(file_name):
            data = []
            with open(file_name, 'w+', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return data
        
        # 尝试进行文件操作
        try:
            with open(file_name, 'r+', encoding='utf-8') as file:
                data = json.load(file)
        except Exception as exception:
            raise exception
        else:
            return data
        finally:
            # 释放线程锁
            lock.release()
            
    # json 文件写入
    @classmethod
    def write(cls, file_name: str, data: Union[dict[str, Any], list[Any]]) -> None:
        '''写入 `.json` 文件

        参数:
            file_name (str): 要写入的文件路径
            data (Union[dict[str, Any], list[Any]]): 要写入的内容
        '''
        # 判断文件是否已有线程锁对象，如果没有则创建一个
        if not file_name in list(cls.locks.keys()):
            cls.locks[file_name] = threading.Lock()
            
        # 获取对应的线程锁对象
        lock = cls.locks[file_name]
        # 尝试获取线程锁
        lock.acquire()
        
        # 尝试进行文件操作
        try:
            with open(file_name, 'w+', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as exception:
            raise exception
        else:
            return
        finally:
            # 释放线程锁
            lock.release()

# 日志记录类
class Logging:
    '''日志记录类'''
    lock = threading.Lock() # 创建线程锁对象
    
    # 输出日志记录方法
    @classmethod
    def info(cls, info: str) -> None:
        '''输出日志记录方法

        参数:
            info (str): 记录的日志内容
        '''
        # 获取当前日期
        now = datetime.now()
        date_now = now.strftime('%Y-%m-%d')
        # 获取引用模块名称
        module = inspect.getmodule(inspect.stack()[1][0])
        if not module is None:
            name = '.'.join(module.__name__.split('.')[-2:])
        else:
            name = ''
        
        # 拼接完整日志内容
        log_message = '[{time}] INFO in {name}: {info}\n'.format(
            time = now.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
            name = name,
            info = info
        )
        
        # 获取线程锁
        cls.lock.acquire()
        # 检测日志路径是否存在
        if not os.path.exists(LOG_DIR + '/log'):
            os.mkdir(LOG_DIR + '/log')
        # 创建并写入日志文件
        with open(LOG_DIR + f'/log/{date_now}.log', 'a+', encoding='utf-8') as log_file:
            log_file.write(log_message)
        # 释放线程锁
        cls.lock.release()
    
    # 警告日志记录方法
    @classmethod
    def warning(cls, info: str) -> None:
        '''警告日志记录方法

        参数:
            info (str): 记录的日志内容
        '''
        # 获取当前日期
        now = datetime.now()
        date_now = now.strftime('%Y-%m-%d')
        # 获取引用模块名称
        module = inspect.getmodule(inspect.stack()[1][0])
        if not module is None:
            name = '.'.join(module.__name__.split('.')[-2:])
        else:
            name = ''
        
        # 拼接完整日志内容
        log_message = '[{time}] WARNING in {name}: {info}\n'.format(
            time = now.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
            name = name,
            info = info
        )
        
        # 获取线程锁
        cls.lock.acquire()
        # 检测日志路径是否存在
        if not os.path.exists(LOG_DIR + '/log'):
            os.mkdir(LOG_DIR + '/log')
        # 创建并写入日志文件
        with open(LOG_DIR + f'/log/{date_now}.log', 'a+', encoding='utf-8') as log_file:
            log_file.write(log_message)
        # 释放线程锁
        cls.lock.release()
    
    # 错误信息日志记录方法
    @classmethod
    def error(cls, exception: Exception) -> None:
        '''错误信息日志记录方法

        参数:
            exception (Exception): 记录的错误信息
        '''
        # 获取当前日期
        now = datetime.now()
        date_now = now.strftime('%Y-%m-%d')
        # 获取引用模块名称
        module = inspect.getmodule(inspect.stack()[1][0])
        if not module is None:
            name = '.'.join(module.__name__.split('.')[-2:])
        else:
            name = ''
            
        # 获取错误追踪信息
        error = '\n' + ''.join(traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__
            ))
        # 拼接完整日志内容
        log_message = '[{time}] ERROR in {name}: {error}\n'.format(
            time = now.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
            name = name,
            error = error
            )
        
        # 获取线程锁
        cls.lock.acquire()
        # 检测日志路径是否存在
        if not os.path.exists(LOG_DIR + '/log'):
            os.mkdir(LOG_DIR + '/log')
        # 创建并写入日志文件
        with open(LOG_DIR + f'/log/{date_now}.log', 'a+', encoding='utf-8') as log_file:
            log_file.write(log_message)
        # 释放线程锁
        cls.lock.release()

# 功能信息类
class Function():
    '''功能信息类'''
    # 初始化
    def __init__(
        self,
        inner_name: str,
        name: str,
        desc: str,
        help_doc: str,
        function: FunctionLike
    ) -> None:
        '''功能信息类

        参数:
            inner_name (str): 函数名
            name (str): 功能名
            desc (str): 功能简介
            function (Function): 功能函数
        '''
        self.inner_name: str = inner_name
        '''函数名'''
        self.name: str = name
        '''功能名'''
        self.desc: str = desc
        '''功能简介'''
        self.help_doc: str = help_doc
        '''功能帮助'''
        self.function: FunctionLike = function
        '''功能函数'''

# 定时任务类
class Schedule():
    '''定时任务类'''
    # 初始化
    def __init__(self, name: str, function: ScheduledFunction, kill_container: list[bool]) -> None:
        '''定时任务类

        参数:
            name (str): 任务名称
            function (ScheduledFunction): 任务函数
        '''
        self.name: str = name
        '''任务名称'''
        self.job: ScheduledFunction = function
        '''任务函数'''
        self.killed: list[bool] = kill_container
        '''任务是否被终止'''
    
    # 终止任务
    def kill(self) -> None:
        '''终止任务'''
        self.killed[0] = True

# 插件功能注册装饰器
def plugin_register(
    *,
    name: Optional[str]=None,
    desc: Optional[str]=None,
    command: str='',
    to_me: bool=False,
) -> Decorater:
    '''插件功能注册装饰器

    参数:
        name (Optional[str], optional): 功能名。
            若置空则以 `插件名.函数名` 代替。默认为空。
        desc (Optional[str], optional): 功能简介。
            当功能所在插件收到 /help 请求时，该字符串将会作为功能描述输出。默认为空。
        command (str, optional): 指令过滤，指定该函数只会传入以该字符串开头的消息。
            置空则不进行过滤。默认为空。
        to_me (bool, optional): 指定该功能是否只会在机器人被提及时启用。
            置空则不进行过滤。默认为空。

    返回:
        Decorater: 一个装饰器函数。
    '''
    # 定义内部装饰器函数，接收并处理函数对象
    def inner_decorator(function: FunctionLike) -> FunctionLike:
        '''内部装饰器函数，接收并处理函数对象'''
        plugin_name = function.__module__.split('.')
        try:
            plugin_name = plugin_name[plugin_name.index('plugin') + 1:][0]
        except ValueError:
            plugin_name = plugin_name[-1]
        function_name = (
            f'{plugin_name}.{function.__name__}' if plugin_name != '__main__'
            else function.__name__
        )
        # 检测函数是否已被装饰过
        if function_name in [func.inner_name for func in function_list]:
            return function
        outer_name = name if name is not None else function.__name__
        help_doc = (
            function.__doc__ if function.__doc__ is not None
            else f'[{outer_name}]'
        )
        # 定义内部函数，用于代替被装饰的函数被引用
        def inner_function(bot: Bot, event: Event) -> None:
            '''定义内部函数，用于代替被装饰的函数被引用'''
            # 尝试获取事件消息以判断是否为消息事件
            try:
                message = event.get_message()
            except NotImplementedError: # 表明现在不是消息事件
                if not to_me and command == '': # 没有过滤指定
                    try:
                        function(bot, event)
                    except Exception as exception:
                        Logging.error(exception)
                        print(f'[{function_name}] 运行出错: {type(exception).__name__}: {exception}')
                    return None
                else:
                    return None
            # 判断事件消息内容
            if message[0].is_text() and message[0].data['text'].startswith('/help '): # 如果是帮助
                if (
                    message[0].data['text'][6:] == outer_name
                    or message[0].data['text'][6:] == function.__name__
                ): # 如果是当前功能名
                    help_reply = f'[{outer_name}]\n{help_doc}'
                    try:
                        bot.send(event, help_reply)
                    except Exception as exception:
                        Logging.error(exception)
                        print(f'发送帮助消息时出错: {type(exception).__name__}: {exception}')
                return None
            if to_me: # 如果要求提及机器人
                if event.is_tome(): # 如果提及机器人
                    try:
                        function(bot, event)
                    except Exception as exception:
                        Logging.error(exception)
                        print(f'[{function_name}] 运行出错: {type(exception).__name__}: {exception}')
                return None
            if command != '': # 如果有指令过滤
                if message[0].is_text() and message[0].data['text'].startswith(command):
                    message[0].data['text'] = message[0].data['text'][len(command):].strip()
                    try:
                        function(bot, event)
                    except Exception as exception:
                        Logging.error(exception)
                        print(f'[{function_name}] 运行出错: {type(exception).__name__}: {exception}')
                return None
            try:
                function(bot, event)
            except Exception as exception:
                Logging.error(exception)
                print(f'[{function_name}] 运行出错: {type(exception).__name__}: {exception}')
            return None
        # 将被装饰的函数名和函数对象添加到列表中
        function_list.append(
            Function(
                function_name,
                outer_name,
                desc if desc is not None else outer_name,
                help_doc,
                inner_function
            )
        )
        return inner_function
    return inner_decorator

# 时间间隔定时任务注册装饰器
@overload
def schedule_register(
    trigger: Literal['interval'],
    *,
    id: Optional[str]=None,
    max_instance: Optional[int]=None,
    **kwargs: int) -> Scheduler:
    '''定时任务注册装饰器

    参数:
        trigger (Literal[&#39;interval&#39;]): 时间间隔定时任务
        id (Optional[str], optional): 定时任务名称，默认为函数名
        max_instance (Optional[int], optional):最大同时执行上限，默认不设限
        kwargs: 设定时间间隔，值为一个整数，表示每过多少秒 / 分钟 / 小时执行一次
            second (int): 时间间隔秒数
            minute (int): 时间间隔分钟数
            hour (int): 时间间隔小时数
    '''
    ...

# 定时策略定时任务注册装饰器
@overload
def schedule_register(
    trigger: Literal['cron'],
    *,
    id: Optional[str]=None,
    max_instance: Optional[int]=None,
    **kwargs: str
) -> Scheduler:
    '''定时任务注册装饰器

    参数:
        trigger (Literal[&#39;interval&#39;]): 定时策略定时任务
        id (Optional[str], optional): 定时任务名称，默认为函数名
        max_instance (Optional[int], optional):最大同时执行上限，默认不设限
        kwargs: 设定定时策略，值为一串由 `,` 分隔开的数字，表示每分钟某秒 / 每小时某分钟 / 每天某小时执行一次
            second (str): 时间间隔秒数
            minute (str): 时间间隔分钟数
            hour (str): 时间间隔小时数
    '''
    ...

# 定时任务注册装饰器
def schedule_register(
    trigger: Literal['interval', 'cron'],
    *,
    id: Optional[str]=None,
    max_instance: Optional[int]=None,
    **kwargs: Union[str, int]
) -> Scheduler:
    # 定义内部装饰器函数，接收并处理函数对象
    def inner_decorator(function: ScheduledFunction) -> ScheduledFunction:
        '''内部装饰器函数，接收并处理函数对象'''
        # 执行任务子函数
        def _execute_job(bot: Bot) -> None:
            '''执行任务子函数'''
            try:
                function(bot)
            except Exception as exception:
                Logging.error(exception)
                print(f'[{function.__name__}] 运行出错: {type(exception).__name__}: {exception}')
            return
        
        # 线程建立子函数
        def run_job(bot: Bot) -> None:
            '''线程建立子函数'''
            thread = threading.Thread(target=_execute_job, args=(bot,), daemon=True)
            threads.append(thread)
            thread.start()
            thread.join()
            threads.remove(thread)
            return
        
        # 定义一个线程列表，用于控制线程数量
        threads: list[threading.Thread] = []
        # 定义函数终止标识容器
        kill_container: list[bool] = [False]
        # 获取定时设置
        second = kwargs.get('second', None)
        minute = kwargs.get('minute', None)
        hour = kwargs.get('hour', None)
        # 判断定时策略
        if trigger == 'interval': # 如果是时间间隔
            if isinstance(second, int):
                interval = second
            elif isinstance(minute, int):
                interval = minute * 60
            elif isinstance(hour, int):
                interval = hour * 3600
            else:
                raise ValueError('时间间隔定义错误。')
            # 定义内部函数，用于代替被装饰的函数被引用
            def interval_function(bot: Bot) -> None:
                '''定义内部函数，用于代替被装饰的函数被引用'''
                now = datetime.now()
                while True: # 循环运行子函数任务
                    while (datetime.now() - now).seconds < interval:
                        sleep(0.1)
                        if kill_container[0] == True:
                            return
                        continue
                    now = datetime.now()
                    if max_instance is not None:
                        if len(threads) >= max_instance:
                            print(
                                '任务 {} 的任务实例数达到最大值，将在 {} 再次尝试执行。'.format(
                                    id,
                                    (now + timedelta(seconds=interval)).strftime(
                                        '%Y-%m-%d %H:%M:%S'
                                    )
                                )
                            )
                            continue
                    threading.Thread(target=run_job, args=(bot,), daemon=True).start()
            schedule_list.append(
                Schedule(
                    id if id is not None else function.__name__,
                    interval_function,
                    kill_container
                )
            )
            return interval_function
        elif trigger == 'cron': # 如果是定时策略
            if isinstance(second, str):
                seconds = [
                    int(i.strip()) for i in second.split(',')
                    if i.strip() != '' and int(i.strip()) in range(0, 60)
                ]
                crons = {
                    'type': 'second',
                    'cron': [(second, False) for second in seconds]
                }
            elif isinstance(minute, str):
                minutes = [
                    int(i.strip()) for i in minute.split(',')
                    if i.strip() != '' and int(i.strip()) in range(0, 60)
                ]
                crons = {
                    'type': 'minute',
                    'cron': [(minute, False) for minute in minutes]
                }
            elif isinstance(hour, str):
                hours = [
                    int(i.strip()) for i in hour.split(',')
                    if i.strip() != '' and int(i.strip()) in range(0, 24)
                ]
                crons = {
                    'type': 'hour',
                    'cron': [(hour, False) for hour in hours]
                }
            else:
                raise ValueError('定时策略定义错误。')
            # 定义内部函数，用于代替被装饰的函数被引用
            def cron_function(bot: Bot) -> None:
                '''定义内部函数，用于代替被装饰的函数被引用'''
                while True: # 循环运行子函数任务
                    if kill_container[0] == True:
                        return
                    now = datetime.now()
                    if crons['type'] == 'second': nowstime = now.second
                    elif crons['type'] == 'minute': nowstime = now.minute
                    elif crons['type'] == 'hour': nowstime = now.hour
                    else: raise ValueError('定时策略定义错误。')
                    for index, cron in enumerate(crons['cron']):
                        if cron[0] == nowstime:
                            if not cron[1]:
                                for _cron in crons['cron']:
                                    _cron[1] = False
                                if max_instance is not None:
                                    if len(threads) >= max_instance:
                                        if index < len(crons['cron']) - 1:
                                            nexttime = crons['cron'][index + 1][0]
                                        else:
                                            nexttime = crons['cron'][0][0]
                                            if crons['type'] in ['second', 'minute']:
                                                nexttime += 60
                                            else:
                                                nexttime += 24
                                        if crons['type'] == 'second':
                                            next = now + timedelta(seconds=(nexttime - nowstime))
                                        elif crons['type'] == 'minute':
                                            next = now + timedelta(minutes=(nexttime - nowstime))
                                        elif crons['type'] == 'hour':
                                            next = now + timedelta(hours=(nexttime - nowstime))
                                        else:
                                            continue
                                        print(
                                            '任务 {} 的任务实例数达到最大值，将在 {} 再次尝试执行。'.format(
                                                id,
                                                next.strftime('%Y-%m-%d %H:%M:%S')
                                            )
                                        )
                                        continue
                                crons['cron'][index][1] = True 
                                threading.Thread(target=run_job, args=(bot,), daemon=True).start()
                    sleep(0.1)
            schedule_list.append(
                Schedule(
                    id if id is not None else function.__name__,
                    cron_function,
                    kill_container
                )
            )
            return cron_function
    return inner_decorator

# 运行定时任务
def _schedule_run(bot: Bot) -> None:
    '''运行定时任务'''
    for schedule in schedule_list:
        threading.Thread(target=schedule.job, args=(bot,), daemon=True).start()
    return

# 截止定时任务
def _schedule_kill() -> None:
    '''截止定时任务'''
    for schedule in schedule_list:
        schedule.kill()
    schedule_list.clear()
    return
