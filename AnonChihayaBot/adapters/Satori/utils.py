'''Anon Chihaya 框架 Satori 协议适配器
杂项定义
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
import re
from pydantic import Field, BaseModel
from typing import Optional, Union, Any

# 对字符串进行转义
def escape(string: str) -> str:
    '''对字符串进行转义

    参数:
        string (str): 需要转义的字符串

    返回:
        str: 转义后的字符串
    '''
    return (
        string.replace('&', '&amp;')
        .replace('"', '&quot;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )

# 对字符串进行去转义
def unescape(string: str) -> str:
    '''对字符串进行转义

    参数:
        string (str): 需要去转义的字符串

    返回:
        str: 去转义后的字符串
    '''
    return (
        string.replace('&quot;', '"')
        .replace('&amp;', '&')
        .replace('&lt;', '<')
        .replace('&gt;', '>')
    )

# 消息元素类
class Element(BaseModel):
    '''消息元素类'''
    type: str
    '''元素类型'''
    attrs: dict[str, Any]=Field(default_factory=dict)
    '''元素属性'''
    children: list['Element']=Field(default_factory=list)
    '''子元素'''
    source: Optional[str]=None
    '''元素原始字符串'''
    # 重写 __str__() 方法
    def __str__(self) -> str:
        '''将元素转换为字符串'''
        if self.source is not None: # 如果有原始字符串
            return self.source
        if self.type == 'text': # 如果是文本类型
            return escape(self.attrs['text'])
        # 若不符合则生成一个 HTML 标签字符串
        def _attr(key: str, value: Any) -> str:
            '''获取元素属性的字符串表示'''
            # 如果是 bool 值
            if value is True:
                return key
            if value is False:
                return f'no-{key}'
            return f'{key}="{escape(str(value))}"'
        
        attrs = ' '.join(_attr(key, value) for key, value in self.attrs.items())
        if not self.children: # 如果没有子元素
            return f'<{self.type} {attrs}/>'
        # 有子元素
        childrens = ''.join(str(children) for children in self.children)
        return f'<{self.type} {attrs}>{childrens}</{self.type}>'

# 消息标签类
class Token(BaseModel):
    '''消息标签类'''
    type: str
    '''标签类型'''
    close: str
    '''是否关闭'''
    empty: str
    '''是否为空'''
    attrs: dict[str, Any]
    '''标签属性'''
    source: str
    '''原始字符串'''

# 字符串解析函数
def parse(src: str) -> list[Element]:
    '''将字符串解析为元素列表

    参数:
        src (str): 原始字符串

    返回:
        list[Element]: 解析出的元素列表
    '''
    # HTML 标签正则匹配
    tag_pat = re.compile(r'<!--[\s\S]*?-->|<(/?)([^!\s>/]*)([^>]*?)\s*(/?)>')
    # HTML 属性正则匹配
    attr_pat = re.compile(r'([^\s=]+)(?:=\"([^\"]*)\"|=\'([^\']*)\')?', re.S)
    # 解析对象存储列表
    tokens: list[Union[Token, Element]] = []
    
    # 将字符串中部分转换为文本 Element 对象
    def parse_n_push(source: str) -> None:
        '''转换源字符串不含 `HTML` 标签部分

        参数:
            source (str): 要转换的字符串
        '''
        text = unescape(source)
        if text: # 如果不为空
            tokens.append(Element(type='text', attrs={'text': text}))
    
    # 匹配 HTML 标签并循环处理
    while tag_map := tag_pat.search(src):
        parse_n_push(src[:tag_map.start()]) # 处理第一个匹配之前部分
        src = src[tag_map.end():] # 截取匹配结果后的部分为源字符串
        # 如果是注释则跳过
        if tag_map.group(0).startswith('<!--'):
            continue
        # 根据匹配结果创建 Token 对象
        close, tag, attr_str, empty = tag_map.groups()
        token = Token(
            type=tag or 'template',
            close=close,
            empty=empty,
            attrs={},
            source=tag_map.group(0)
        )
        # 匹配 HTML 属性并循环处理
        while attr_map := attr_pat.search(attr_str):
            # 获取有效属性值
            key, value1, value2 = attr_map.groups()
            value = value1 or value2
            if value: # 若值存在
                token.attrs[key] = unescape(value)
            elif key.startswith('no-'): # 若为表 False 属性
                token.attrs[key] = False
            else: # 表 True 属性
                token.attrs[key] = True
            attr_str = attr_str[attr_map.end():] # 截取匹配结果后的部分为源字符串
        tokens.append(token)
    
    parse_n_push(src) # 处理剩余源字符串
    
    # 定义存储正在处理的 Element 对象的列表，并以一个 "template" 类型 Element 对象作为根元素
    stack = [Element(type='template')]
    
    # 回滚 stack 列表元素方法
    def rollback(count: int) -> None:
        '''回滚 stack 列表元素并作为文本添加到上一层元素的子元素中

        参数:
            count (int): 需要回滚的元素数
        '''
        while count:
            child = stack.pop(0)
            source = stack[0].children.pop(-1)
            stack[0].children.append(Element(type='text', attrs={'text': source}))
            stack[0].children.extend(child.children)
            count -= 1
    
    # 循环处理 tokens 列表中对象
    for token in tokens:
        if isinstance(token, Element): # 如果是 Element 对象
            stack[0].children.append(token) # 作为第一个元素的子元素添加
        elif token.close: # 如果是关闭标签
            index = 0
            # 查找与之对应的开放标签并记录索引
            while index < len(stack) and stack[index].type != token.type:
                index += 1
            if index == len(stack): # 如果没有找到
                stack[0].children.append(
                    Element(type='text', attrs={'text': token.source})
                )
            else: # 回滚处理
                rollback(index)
                element = stack.pop(0) # 弹出第一个元素并赋值
                element.source = None
        else: # 是 Token 且不是关闭标签
            # 创建一个 Element 对象并添加为 stack 第一元素的子元素
            element = Element(type=token.type, attrs=token.attrs)
            stack[0].children.append(element)
            if not token.empty: # 如果不是空标签
                # 赋值，并将 element 设为第一元素
                element.source = token.source
                stack.insert(0, element)
    
    rollback(len(stack) - 1) # 回滚 stack 中除最后一个元素歪的所有元素
    # 将根元素的子元素作为解析结果返回
    return stack[0].children
