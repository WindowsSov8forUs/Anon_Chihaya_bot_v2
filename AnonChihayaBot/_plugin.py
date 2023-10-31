'''Anon Chihaya 框架
插件管理功能
'''
import os
import sys
import importlib
from types import ModuleType

from AnonChihayaBot.adapters import logger
from AnonChihayaBot.adapters.utils import Function, function_list

# 插件包所在文件夹路径
PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/plugin'
# 添加插件所在目录
sys.path.append(PLUGIN_DIR)
# 插件列表
global plugins
plugins: list['Plugin'] = []
# 判断是否正在更新插件
global in_reloading
in_reloading: bool = False

# 插件对象
class Plugin():
    '''AnonChihayaBot 插件对象

    参数:
        name (str): 插件名称
        module (ModuleType): 插件包对象
    '''
    # 初始化
    def __init__(self, name: str, doc: str, package_name: str, module: ModuleType) -> None:
        '''AnonChihayaBot 插件对象

        参数:
            name (str): 插件名称
            package_name (str): 插件包名称
            module (ModuleType): 插件包对象
        '''
        self.name: str = name
        '''插件名称'''
        self.doc: str = doc
        '''插件说明'''
        self.package_name: str = package_name
        '''插件包名称'''
        self.module: ModuleType = module
        '''插件对象'''
        self.functions: list[Function] = []
        '''插件功能对象列表'''

# 插件热重载，限制插件位于 './plugin' 文件夹内
def _plugin_reload() -> None:
    '''插件热重载'''
    # 使用栈来迭代地重加载所有子模块和子包
    def _reload_recursive_in_iter(plugin: ModuleType) -> None:
        '''使用栈来迭代地重加载所有子模块和子包'''
        pre_stack = [plugin] # 模块预存放栈
        stack: list[ModuleType] = [] # 模块存放栈
        while pre_stack: # 迭代存放
            module = pre_stack.pop() # 取出栈中第一个模块
            stack.append(module)
            for attribute_name in dir(module): # 遍历查找模块内对象
                attribute = getattr(module, attribute_name) # 获取对象
                if isinstance(attribute, ModuleType): # 如果对象为模块
                    fn_child = getattr(attribute, '__file__', None) # 获取对象路径
                    if isinstance(fn_child, str): # 如果存在路径
                        if os.path.normcase(fn_child).startswith(os.path.normcase(PLUGIN_DIR)):
                            # 如果是插件包所在路径
                            if fn_child.endswith('utils.py'): # 优先加载 utils.py
                                importlib.reload(attribute)
                            else:
                                pre_stack.append(attribute) # 放入栈中
        
        while stack: # 遍历重加载
            module = stack.pop(-1)
            importlib.reload(module)
    
    global plugins
    global in_reloading
    
    in_reloading = True
    plugins.clear() # 重置插件列表
    
    # 导入 plugin 包
    if not os.path.exists(PLUGIN_DIR):
        os.makedirs(PLUGIN_DIR, exist_ok=True)
    for plugin_name in os.listdir(PLUGIN_DIR):
        # 过滤不合法名称
        if not plugin_name.startswith('plugin_'):
            continue
        if plugin_name.endswith('.py'): # 去除 .py 后缀
            plugin_name = plugin_name[:-3]
        try:
            plugin = importlib.import_module(f'{plugin_name}')
            _reload_recursive_in_iter(plugin)
        except Exception as exception:
            info = f'导入插件 [{plugin_name}] 时出错: {type(exception).__name__}: {exception}'
            print(info)
            logger.error(exception)
            continue
        
        # 尝试获取插件注释文档字符串
        doc = plugin.__doc__ if plugin.__doc__ is not None else f'{plugin_name}'
        if len(docs := doc.split('\n')) > 1:
            doc = '\n'.join(docs[1:])
        plg = Plugin(docs[0], doc, plugin_name, plugin)
        plg.functions = function_list.copy()
        function_list.clear()
        plugins.append(plg)
        print(f'插件 [{plugin_name}] 加载完成。')
    in_reloading = False
    return

# 判断是否正在重载插件
def _in_reloading() -> bool:
    '''判断是否正在重载插件'''
    return in_reloading

# 查找插件
def find_plugin(name: str) -> Plugin:
    '''查找插件

    参数:
        name (str): 要查找的插件名

    返回:
        Plugin: 找到的插件
    '''
    for plugin in plugins:
        if plugin.name.lower() == name.lower():
            return plugin
        else:
            if plugin.package_name.lower() == name.lower():
                return plugin
    raise ValueError(f'未找到插件 [{name}]')

# 查找功能
def find_function(name: str) -> Function:
    '''查找功能

    参数:
        name (str): 要查找的功能名

    返回:
        Function: 找到的插件对象
    '''
    for plugin in plugins:
        for function in plugin.functions:
            if (
                function.name.lower() == name.lower()
                or function.inner_name.split('.')[-1].lower() == name.lower()
            ):
                return function
    raise ValueError(f'未找到功能 [{name}]')
