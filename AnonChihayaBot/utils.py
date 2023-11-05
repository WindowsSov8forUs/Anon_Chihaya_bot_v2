'''Anon Chihaya 框架
杂项内容
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from PIL import ImageFont

# 以指定字符串为始终点切割字符串
def str_cut_out(
    str: str,
    str_begin: str='',
    str_end: str='',
    type_: bool=True
) -> str:
    '''以指定字符串为始终点切割字符串

    参数:
        str (str): 要切割的字符串
        str_begin (str, optional): 起始标志字符串。若留空则表示从字符串的开头开始切割
        str_end (str, optional): 终止标志字符串。若留空则表示从字符串的结尾开始切割
        type_ (bool, optional): 切割方式标识。True 表示保留标志字符串，False 表示不保留标志字符串，默认为 True

    返回:
        str: 得到的字符串，若没有要提取的字符串则返回一个空字符串
    '''
    # 检测起始点
    if str_begin != '':
        begin_index = str.find(str_begin)
        if begin_index == -1: # 如果没找到则视为未指定
            str_begin = ''
            begin_index = 0
    else:
        begin_index = 0
    # 检测终点
    if str_end != '':
        end_index = str.find(str_end,begin_index + len(str_begin))
        if end_index == -1: # 如果没找到则视为未指定
            str_end = ''
            end_index = len(str)
    else:
        end_index = len(str)
    # 切割
    if type_:
        str_print = str[begin_index:end_index + len(str_end)]
    else:
        str_print = str[begin_index + len(str_begin):end_index]

    # 返回切割结果
    return str_print

# 以指定字符串为始终点从字符串中切除
def str_remove(
    str: str,
    str_begin: str='',
    str_end: str='',
    type_: bool=True
) -> str:
    '''以指定字符串为始终点切除字符串

    参数:
        str (str): 要切除的字符串
        str_begin (str, optional): 起始标志字符串。若留空则表示从字符串的开头开始切除
        str_end (str, optional): 终止标志字符串。若留空则表示切除到字符串的结尾
        type_ (bool, optional): 切割方式标识。True 表示保留标志字符串，False 表示不保留标志字符串，默认为 True

    Raises:
        ValueError: 要切除的字符串不存在

    返回:
        str: 得到的字符串
    '''
    # 检测起始点
    if str_begin != '':
        begin_index = str.find(str_begin)
    else:
        begin_index = 0
    # 检测终点
    if str_end != '':
        end_index = str.find(str_end,begin_index + len(str_begin))
    else:
        end_index = len(str)
    # 检测是否存在
    if begin_index == -1 or end_index == -1:
        # 要切除的字符串不存在
        raise ValueError('要切除的字符串不存在。')
    # 切除
    if type_:
        str_print = str[:begin_index + len(str_begin)] + str[end_index:]
    else:
        str_print = str[:begin_index] + str[end_index + len(str_end):]

    # 返回切割结果
    return str_print

# 换行切割字符串
def break_line(line_get: str, width_limit: int, font: ImageFont.FreeTypeFont) -> str:
    '''换行切割字符串，输入需要切割的字符串及每行限制长度，返回切割后的字符串

    参数:
        line_get (str): 需要切割的字符串
        width_limit (int): 每行限制像素长度
        font (ImageFont.FreeTypeFont): 使用的字体 `PIL.ImageFont.FreeTypeFont`

    返回:
        str: 切割后的字符串
    '''
    TABLE_WIDTH = 4
    result = ''
    width = 0
    for chr in line_get:
        if chr == '️': # 不可见字符
            chr = ''
        elif chr == '⃣': # 占位字符
            chr = ''
        elif chr == '\n': # 换行字符
            width = 0
            result += ' ' + chr
        elif chr == '\t': # 制表符字符
            width += TABLE_WIDTH * font.getlength(' ')
            result += chr
        else: # 其他字符
            font_width = font.getlength(chr)
            if (width + font_width) > width_limit: # 剩余宽度不够
                width = font_width
                result += '\n' + chr
            else:
                width += font_width
                result += chr
        if width >= width_limit:
            result += '\n'
            width = 0
            
    if result.endswith('\n'):
        return result
    return result + '\n'

from .adapters import Json as Json
from .adapters import Logging as Logging

logger = Logging()
