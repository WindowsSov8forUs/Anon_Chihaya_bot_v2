'''Anon Chihaya 框架 Satori 协议适配器
消息类型定义
'''
# -*- coding: utf-8 -*-
# !/usr/bin/python3
from io import BytesIO
from pathlib import Path
from base64 import b64encode
from dataclasses import dataclass
from collections.abc import Iterable
from typing_extensions import override, NotRequired
from typing import TypedDict, Iterable, Optional, Union, overload, Any

from AnonChihayaBot.adapters import Message as BaseMessage
from AnonChihayaBot.adapters import MessageSegment as BaseMessageSegment

from .utils import Element, parse, escape

# 用于 HTML 元素 src 的 data URI 对象
class SrcData(TypedDict):
    '''data URI 对象'''
    data: Union[bytes, BytesIO]
    '''资源数据'''
    mime_type: str
    '''资源 MIME 类型'''

# 消息段类
class MessageSegment(BaseMessageSegment['Message']):
    '''消息段类'''
    # 将消息段转换为 HTML 字符串
    def __str__(self) -> str:
        '''将消息段转换为 HTML 字符串'''
        # 转换消息段中的数据为属性
        def _attr(key: str, value: Any) -> str:
            '''获取 HTML 属性字符串'''
            if value is True:
                return key
            if value is False:
                return f'no-{key}'
            if isinstance(value, (int, float)):
                return f'{key}={value}'
            return f'{key}="{escape(str(value))}"'
        
        attrs = ' '.join(_attr(key, value) for key, value in self.data.items())
        return f'<{self.type} {attrs}/>'
    
    # 获取消息数组类型
    @classmethod
    @override
    def get_message_class(cls) -> type['Message']:
        return Message
    
    # 纯文本
    @staticmethod
    def text(text: str) -> 'Text':
        '''纯文本

        参数:
            text (str): 一段纯文本

        返回:
            Text: 纯文本消息段
        '''
        return Text('text', {'text': text})
    
    # 提及用户 ID
    @staticmethod
    def at(user_id: str, name: Optional[str]=None) -> 'At':
        '''提及用户

        参数:
            user_id (str): 目标用户的 ID
            name (Optional[str], optional): 目标用户的名称

        返回:
            At: 提及用户消息段
        '''
        data: AtData = {'id': user_id}
        if name is not None:
            data['name'] = name
        return At('at', data) # type: ignore
    
    # 提及用户角色
    @staticmethod
    def at_role(role: str, name: Optional[str]=None) -> 'At':
        '''提及用户

        参数:
            role (str): 目标角色
            name (Optional[str], optional): 目标用户的名称

        返回:
            At: 提及用户消息段
        '''
        data: AtData = {'role': role}
        if name is not None:
            data['name'] = name
        return At('at', data)
    
    # 提及用户特殊操作
    @staticmethod
    def at_type(type_: str) -> 'At':
        '''提及用户

        参数:
            type_ (str): 特殊操作，例如 all 表示 @全体成员，here 表示 @在线成员

        返回:
            At: 提及用户消息段
        '''
        return At('at', {'type': type_})
    
    # 提及频道
    @staticmethod
    def sharp(channel_id: str, name: Optional[str]=None) -> 'Sharp':
        '''提及频道

        参数:
            channel_id (str): 目标频道的 ID
            name (Optional[str], optional): 目标频道的名称

        返回:
            Sharp: 提及频道消息段
        '''
        data: SharpData = {'id': channel_id}
        if name is not None:
            data['name'] = name
        return Sharp('sharp', data)
    
    # 链接
    @staticmethod
    def link(href: str) -> 'Link':
        '''链接

        参数:
            href (str): 链接的 URL

        返回:
            Link: 链接消息段
        '''
        return Link('link', {'text': href})
    
    # 图片
    @staticmethod
    @overload
    def image(src: str, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Image':
        '''图片

        参数:
            src (str): 资源的 URL
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Image: 图片消息段
        '''
    
    # 图片
    @staticmethod
    @overload
    def image(src: Path, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Image':
        '''图片

        参数:
            src (Path): 资源的本地路径
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Image: 图片消息段
        '''
    
    # 图片
    @staticmethod
    @overload
    def image(src: SrcData, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Image':
        '''图片

        参数:
            src (SrcData): 资源数据
                `data`: 资源数据，为一个 `bytes` 数据或 `BytesIO` 对象
                `mime_type`: 资源的 MIME 类型，示例：`image/png`
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Image: 图片消息段
        '''
    
    # 图片
    @staticmethod
    def image(
        src: Union[str, Path, SrcData],
        cache: Optional[bool]=None,
        timeout: Optional[str]=None
    ) -> 'Image':
        if isinstance(src, str): # 是图片 URL
            data: ImageData = {'src': src}
        elif isinstance(src, Path): # 是路径
            data: ImageData = {'src': src.as_uri()}
        elif isinstance(src, SrcData): # 是图片资源对象
            if isinstance(src['data'], BytesIO):
                src['data'] = src['data'].getvalue()
            data: ImageData = {
                'src': f'data:{src["mime_type"]};base64,{b64encode(src["data"]).decode()}'
            }
        if cache is not None:
            data['cache'] = cache
        if timeout is not None:
            data['timeout'] = timeout
        return Image('img', data)
    
    # 语音
    @staticmethod
    @overload
    def audio(src: str, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Audio':
        '''语音

        参数:
            src (str): 资源的 URL
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Audio: 语音消息段
        '''
    
    # 语音
    @staticmethod
    @overload
    def audio(src: Path, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Audio':
        '''语音

        参数:
            src (Path): 资源的本地路径
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Audio: 语音消息段
        '''
    
    # 语音
    @staticmethod
    @overload
    def audio(src: SrcData, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Audio':
        '''语音

        参数:
            src (SrcData): 资源数据
                `data`: 资源数据，为一个 `bytes` 数据或 `BytesIO` 对象
                `mime_type`: 资源的 MIME 类型，示例：`image/png`
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Audio: 语音消息段
        '''
    
    # 语音
    @staticmethod
    def audio(
        src: Union[str, Path, SrcData],
        cache: Optional[bool]=None,
        timeout: Optional[str]=None
    ) -> 'Audio':
        if isinstance(src, str): # 是音频 URL
            data: AudioData = {'src': src}
        elif isinstance(src, Path): # 是路径
            data: AudioData = {'src': src.as_uri()}
        elif isinstance(src, SrcData): # 是音频资源对象
            if isinstance(src['data'], BytesIO):
                src['data'] = src['data'].getvalue()
            data: AudioData = {
                'src': f'data:{src["mime_type"]};base64,{b64encode(src["data"]).decode()}'
            }
        if cache is not None:
            data['cache'] = cache
        if timeout is not None:
            data['timeout'] = timeout
        return Audio('audio', data)
    
    # 视频
    @staticmethod
    @overload
    def video(src: str, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Video':
        '''视频

        参数:
            src (str): 资源的 URL
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Video: 视频消息段
        '''
    
    # 视频
    @staticmethod
    @overload
    def video(src: Path, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Video':
        '''视频

        参数:
            src (Path): 资源的本地路径
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Video: 视频消息段
        '''
    
    # 视频
    @staticmethod
    @overload
    def video(src: SrcData, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'Video':
        '''视频

        参数:
            src (SrcData): 资源数据
                `data`: 资源数据，为一个 `bytes` 数据或 `BytesIO` 对象
                `mime_type`: 资源的 MIME 类型，示例：`image/png`
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            Video: 视频消息段
        '''
    
    # 视频
    @staticmethod
    def video(
        src: Union[str, Path, SrcData],
        cache: Optional[bool]=None,
        timeout: Optional[str]=None
    ) -> 'Video':
        if isinstance(src, str): # 是音频 URL
            data: VideoData = {'src': src}
        elif isinstance(src, Path): # 是路径
            data: VideoData = {'src': src.as_uri()}
        elif isinstance(src, SrcData): # 是音频资源对象
            if isinstance(src['data'], BytesIO):
                src['data'] = src['data'].getvalue()
            data: VideoData = {
                'src': f'data:{src["mime_type"]};base64,{b64encode(src["data"]).decode()}'
            }
        if cache is not None:
            data['cache'] = cache
        if timeout is not None:
            data['timeout'] = timeout
        return Video('video', data)
    
    # 文件
    @staticmethod
    @overload
    def file(src: str, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'File':
        '''文件

        参数:
            src (str): 资源的 URL
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            File: 文件消息段
        '''
    
    # 文件
    @staticmethod
    @overload
    def file(src: Path, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'File':
        '''文件

        参数:
            src (Path): 资源的本地路径
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            File: 文件消息段
        '''
    
    # 文件
    @staticmethod
    @overload
    def file(src: SrcData, cache: Optional[bool]=None, timeout: Optional[str]=None) -> 'File':
        '''文件

        参数:
            src (SrcData): 资源数据
                `data`: 资源数据，为一个 `bytes` 数据或 `BytesIO` 对象
                `mime_type`: 资源的 MIME 类型，示例：`image/png`
            cache (Optional[bool], optional): 是否使用已缓存的文件
            timeout (Optional[str], optional): 下载文件的最长时间 (毫秒)

        返回:
            File: 文件消息段
        '''
    
    # 文件
    @staticmethod
    def file(
        src: Union[str, Path, SrcData],
        cache: Optional[bool]=None,
        timeout: Optional[str]=None
    ) -> 'File':
        if isinstance(src, str): # 是音频 URL
            data: FileData = {'src': src}
        elif isinstance(src, Path): # 是路径
            data: FileData = {'src': src.as_uri()}
        elif isinstance(src, SrcData): # 是音频资源对象
            if isinstance(src['data'], BytesIO):
                src['data'] = src['data'].getvalue()
            data: FileData = {
                'src': f'data:{src["mime_type"]};base64,{b64encode(src["data"]).decode()}'
            }
        if cache is not None:
            data['cache'] = cache
        if timeout is not None:
            data['timeout'] = timeout
        return File('file', data)
    
    # 粗体
    @staticmethod
    def bold(text: str) -> 'Bold':
        '''粗体

        参数:
            text (str): 纯文本

        返回:
            Bold: 粗体消息段
        '''
        return Bold('bold', {'text': text})
    
    # 斜体
    @staticmethod
    def italic(text: str) -> 'Italic':
        '''斜体

        参数:
            text (str): 纯文本

        返回:
            Italic: 斜体消息段
        '''
        return Italic('italic', {'text': text})
    
    # 下划线
    @staticmethod
    def underline(text: str) -> 'Underline':
        '''下划线

        参数:
            text (str): 纯文本

        返回:
            Underline: 下划线消息段
        '''
        return Underline('underline', {'text': text})
    
    # 删除线
    @staticmethod
    def strikethrough(text: str) -> 'Strikethrough':
        '''删除线

        参数:
            text (str): 纯文本

        返回:
            Strikethrough: 删除线消息段
        '''
        return Strikethrough('strikethrough', {'text': text})
    
    # 剧透
    @staticmethod
    def spoiler(text: str) -> 'Spoiler':
        '''剧透

        参数:
            text (str): 纯文本

        返回:
            Spoiler: 剧透消息段
        '''
        return Spoiler('spoiler', {'text': text})
    
    # 代码
    @staticmethod
    def code(text: str) -> 'Code':
        '''代码

        参数:
            text (str): 纯文本

        返回:
            Code: 代码消息段
        '''
        return Code('code', {'text': text})
    
    # 上标
    @staticmethod
    def superscript(text: str) -> 'Superscript':
        '''上标

        参数:
            text (str): 纯文本

        返回:
            Superscript: 上标消息段
        '''
        return Superscript('superscript', {'text': text})
    
    # 下标
    @staticmethod
    def subscript(text: str) -> 'Subscript':
        '''下标

        参数:
            text (str): 纯文本

        返回:
            Subscript: 下标消息段
        '''
        return Subscript('subscript', {'text': text})
    
    # 换行
    @staticmethod
    def br() -> 'Br':
        '''换行

        返回:
            Br: 换行消息段
        '''
        return Br('br', {'text': '\n'})
    
    # 段落
    @staticmethod
    def paragraph(text: str) -> 'Paragraph':
        '''段落

        参数:
            text (str): 纯文本

        返回:
            Paragraph: 段落消息段
        '''
        return Paragraph('paragraph', {'text': text})
    
    # 消息
    @staticmethod
    def message(
        id_: Optional[str]=None,
        forward: Optional[bool]=None,
        content: Optional['Message']=None
    ) -> 'RenderMessage':
        '''消息

        参数:
            id_ (Optional[str], optional): 消息的 ID
            forward (Optional[bool], optional): 是否为转发消息
            content (Optional[&#39;Message&#39;], optional): 消息的内容

        返回:
            RenderMessage: 消息消息段
        '''
        data: RenderMessageData = {}
        if id_ is not None:
            data['id'] = id_
        if forward is not None:
            data['forward'] = forward
        if content is not None:
            data['content'] = content
        return RenderMessage('message', data)
    
    # 引用
    @staticmethod
    def quote(
        id_: str,
        forward: Optional[bool]=None,
        content: Optional['Message']=None
    ) -> 'RenderMessage':
        '''引用

        参数:
            id_ (str): 消息的 ID
            forward (Optional[bool], optional): 是否为转发消息
            content (Optional[&#39;Message&#39;], optional): 消息的内容

        返回:
            RenderMessage: 引用消息段
        '''
        data: RenderMessageData = {'id': id_}
        if forward is not None:
            data['forward'] = forward
        if content is not None:
            data['content'] = content
        return RenderMessage('quote', data)
    
    # 作者
    @staticmethod
    def author(
        user_id: str,
        nickname: Optional[str]=None,
        avatar: Optional[str]=None
    ) -> 'Author':
        '''作者

        参数:
            user_id (str): 用户 ID
            nickname (Optional[str], optional): 昵称
            avatar (Optional[str], optional): 头像 URL

        返回:
            Author: 作者消息段
        '''
        data: AuthorData = {'id': user_id}
        if nickname is not None:
            data['nickname'] = nickname
        if avatar is not None:
            data['avatar'] = avatar
        return Author('author', data)
    
    # 返回消息段是否为字符串
    @override
    def is_text(self) -> bool:
        '''消息段是否为字符串'''
        return False
    
    # 日志字符串
    @override
    def get_log(self) -> str:
        if self.is_text():
            return self.data['text']
        return f'[{self.type}]'

# 纯文本数据
class TextData(TypedDict):
    '''纯文本数据'''
    text: str
    '''一段纯文本'''

# 纯文本
@dataclass
class Text(MessageSegment):
    '''纯文本'''
    data: TextData
    '''纯文本数据'''
    # 重写字符串转换方法
    @override
    def __str__(self) -> str:
        '''将消息段转换为 HTML 字符串'''
        return escape(self.data['text'])
    
    # 返回消息段是否为字符串
    @override
    def is_text(self) -> bool:
        '''消息段是否为字符串'''
        return True

# 提及用户数据
class AtData(TypedDict):
    '''提及用户数据'''
    id: NotRequired[str]
    '''目标用户的 ID'''
    name: NotRequired[str]
    '''目标用户的名称'''
    role: NotRequired[str]
    '''目标角色'''
    type: NotRequired[str]
    '''特殊操作，例如 `all` 表示 `@全体成员`，`here` 表示 `@在线成员`'''

# 提及用户
@dataclass
class At(MessageSegment):
    '''提及用户'''
    data: AtData
    '''提及用户数据'''
    # 日志字符串
    @override
    def get_log(self) -> str:
        at_info = (
            self.data['name'] if 'name' in self.data
            else self.data['id'] if 'id' in self.data
            else 'Unknown'
        )
        return f'@{at_info}'

# 提及频道数据
class SharpData(TypedDict):
    '''提及频道数据'''
    id: str
    '''目标频道的 ID'''
    name: NotRequired[str]
    '''目标频道的名称'''

# 提及频道
@dataclass
class Sharp(MessageSegment):
    '''提及频道'''
    data: SharpData
    '''提及频道数据'''

# 链接
@dataclass
class Link(MessageSegment):
    '''链接'''
    data: TextData
    '''链接数据'''
    # 重写字符串转换方法
    @override
    def __str__(self) -> str:
        return f'<a href="{escape(self.data["text"])}"/>'
    
    # 返回消息段是否为字符串
    @override
    def is_text(self) -> bool:
        '''消息段是否为字符串'''
        return True

# 图片数据
class ImageData(TypedDict):
    '''图片数据'''
    src: str
    '''资源的 URL'''
    cache: NotRequired[bool]
    '''是否使用已缓存的文件'''
    timeout: NotRequired[str]
    '''下载文件的最长时间 (毫秒)'''
    width: NotRequired[int]
    '''图片的宽度'''
    height: NotRequired[int]
    '''图片的高度'''

# 图片
@dataclass
class Image(MessageSegment):
    '''图片'''
    data: ImageData
    '''图片数据'''
    # 日志字符串
    @override
    def get_log(self) -> str:
        return '![image]({})'.format(
            f'src={self.data["src"]}' if "src" in self.data else f'url={self.data["url"]}'
        )

# 语音数据
class AudioData(TypedDict):
    '''语音数据'''
    src: str
    '''资源的 URL'''
    cache: NotRequired[bool]
    '''是否使用已缓存的文件'''
    timeout: NotRequired[str]
    '''下载文件的最长时间 (毫秒)'''

# 语音
@dataclass
class Audio(MessageSegment):
    '''语音'''
    data: AudioData
    '''语音数据'''
    # 日志字符串
    @override
    def get_log(self) -> str:
        return '![audio]({})'.format(
            f'src={self.data["src"]}' if "src" in self.data else f'url={self.data["url"]}'
        )

# 视频数据
class VideoData(TypedDict):
    '''视频数据'''
    src: str
    '''资源的 URL'''
    cache: NotRequired[bool]
    '''是否使用已缓存的文件'''
    timeout: NotRequired[str]
    '''下载文件的最长时间 (毫秒)'''

# 视频
@dataclass
class Video(MessageSegment):
    '''视频'''
    data: VideoData
    '''视频数据'''
    # 日志字符串
    @override
    def get_log(self) -> str:
        return '![video]({})'.format(
            f'src={self.data["src"]}' if "src" in self.data else f'url={self.data["url"]}'
        )

# 文件数据
class FileData(TypedDict):
    '''文件数据'''
    src: str
    '''资源的 URL'''
    cache: NotRequired[bool]
    '''是否使用已缓存的文件'''
    timeout: NotRequired[str]
    '''下载文件的最长时间 (毫秒)'''

# 文件
@dataclass
class File(MessageSegment):
    '''文件'''
    data: FileData
    '''文件数据'''
    # 日志字符串
    @override
    def get_log(self) -> str:
        return '![file]({})'.format(
            f'src={self.data["src"]}' if "src" in self.data else f'url={self.data["url"]}'
        )

# 粗体
@dataclass
class Bold(MessageSegment):
    '''粗体'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<b>{escape(self.data["text"])}</b>'

    @override
    def is_text(self) -> bool:
        return True

# 斜体
@dataclass
class Italic(MessageSegment):
    '''斜体'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<i>{escape(self.data["text"])}</i>'

    @override
    def is_text(self) -> bool:
        return True

# 下划线
@dataclass
class Underline(MessageSegment):
    '''下划线'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<u>{escape(self.data["text"])}</u>'

    @override
    def is_text(self) -> bool:
        return True

# 删除线
@dataclass
class Strikethrough(MessageSegment):
    '''删除线'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<s>{escape(self.data["text"])}</s>'

    @override
    def is_text(self) -> bool:
        return True

# 剧透
@dataclass
class Spoiler(MessageSegment):
    '''剧透'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<spl>{escape(self.data["text"])}</spl>'

    @override
    def is_text(self) -> bool:
        return True

# 代码
@dataclass
class Code(MessageSegment):
    '''代码'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<code>{escape(self.data["text"])}</code>'

    @override
    def is_text(self) -> bool:
        return True

# 上标
@dataclass
class Superscript(MessageSegment):
    '''上标'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<sup>{escape(self.data["text"])}</sup>'

    @override
    def is_text(self) -> bool:
        return True

# 下标
@dataclass
class Subscript(MessageSegment):
    '''下标'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<sub>{escape(self.data["text"])}</sub>'

    @override
    def is_text(self) -> bool:
        return True

# 换行
@dataclass
class Br(MessageSegment):
    '''换行'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return "<br/>"

    @override
    def is_text(self) -> bool:
        return True

# 段落
@dataclass
class Paragraph(MessageSegment):
    '''段落'''
    data: TextData
    '''纯文本数据'''
    @override
    def __str__(self):
        return f'<p>{escape(self.data["text"])}</p>'

    @override
    def is_text(self) -> bool:
        return True

# 消息数据
class RenderMessageData(TypedDict):
    '''消息数据'''
    id: NotRequired[str]
    '''消息的 ID'''
    forward: NotRequired[bool]
    '''是否为转发消息'''
    content: NotRequired['Message']
    '''消息的内容'''

# 消息
@dataclass
class RenderMessage(MessageSegment):
    '''消息'''
    data: RenderMessageData
    '''消息数据'''
    # 重写字符串转换方法
    @override
    def __str__(self) -> str:
        '''将消息段转换为 HTML 字符串'''
        attr = []
        if 'id' in self.data:
            attr.append(f'id="{escape(self.data["id"])}"')
        if self.data.get('forward'):
            attr.append('forward')
        if 'content' not in self.data:
            return f'<{self.type} {" ".join(attr)}/>'
        else:
            return '<{} {}>{}</{}>'.format(
                self.type,
                ' '.join(attr),
                self.data['content'],
                self.type
            )
    
    # 日志字符串
    @override
    def get_log(self) -> str:
        attr = []
        if 'id' in self.data:
            attr.append(f'id={escape(self.data["id"])}')
        if self.data.get('forward'):
            attr.append('forward')
        if 'content' not in self.data:
            return f'![{self.type}]({"|".join(attr)})'
        else:
            return f' ![{self.type}]({"|".join(attr)}){self.data["content"].log} '

# 作者数据
class AuthorData(TypedDict):
    '''作者数据'''
    id: str
    '''用户 ID'''
    nickname: NotRequired[str]
    '''昵称'''
    avatar: NotRequired[str]
    '''头像 URL'''

# 作者
@dataclass
class Author(MessageSegment):
    '''作者'''
    data: AuthorData
    '''作者数据'''
    # 日志字符串
    @override
    def get_log(self) -> str:
        attr = []
        if 'nickname' in self.data:
            attr.append(self.data["nickname"])
        attr.append(f'id={self.data["id"]}')
        return f'![author]({"|".join(attr)})'

# 基础元素类型表
ELEMENT_TYPE_MAP = {
    "text": (Text, "text"),
    "at": (At, "at"),
    "sharp": (Sharp, "sharp"),
    "img": (Image, "image"),
    "image": (Image, "image"),
    "audio": (Audio, "audio"),
    "video": (Video, "video"),
    "file": (File, "file"),
    "author": (Author, "author"),
}
'''基础元素类型表'''

# 修饰元素类型表
STYLE_TYPE_MAP = {
    "b": (Bold, "bold"),
    "strong": (Bold, "bold"),
    "i": (Italic, "italic"),
    "em": (Italic, "italic"),
    "u": (Underline, "underline"),
    "ins": (Underline, "underline"),
    "s": (Strikethrough, "strikethrough"),
    "del": (Strikethrough, "strikethrough"),
    "spl": (Spoiler, "spoiler"),
    "code": (Code, "code"),
    "sup": (Superscript, "superscript"),
    "sub": (Subscript, "subscript"),
    "p": (Paragraph, "paragraph"),
}
'''修饰元素类型表'''

# 消息数组类
class Message(BaseMessage[MessageSegment]):
    '''消息数组类'''
    # 获取消息段类型
    @classmethod
    @override
    def get_segment_class(cls) -> type[MessageSegment]:
        return MessageSegment

    # 定义 A + B 行为
    @override
    def __add__(self, other: Union[str, MessageSegment, Iterable[MessageSegment]]) -> 'Message':
        return super().__add__(MessageSegment.text(other) if isinstance(other, str) else other)
    
    # 定义 B + A 行为
    @override
    def __radd__(self, other: Union[str, MessageSegment, Iterable[MessageSegment]]) -> 'Message':
        return super().__radd__(MessageSegment.text(other) if isinstance(other, str) else other)
    
    # 构造消息数组
    @staticmethod
    @override
    def _construct(message: str) -> Iterable[MessageSegment]:
        yield from Message.from_satori_element(parse(message))
    
    # 处理从 Satori 协议获取的 HTML 元素为消息对象
    @classmethod
    def from_satori_element(cls, elements: list[Element]) -> 'Message':
        '''处理从 Satori 协议获取的 HTML 元素'''
        message = Message()
        # 遍历元素列表
        for element in elements:
            if element.type in ELEMENT_TYPE_MAP: # 如果在基础元素类型表中
                seg_cls, seg_type = ELEMENT_TYPE_MAP[element.type]
                message.append(seg_cls(seg_type, element.attrs.copy()))
            elif element.type in ['a', 'link']: # 如果是链接
                message.append(Link('link', {'text': element.attrs['href']}))
            elif element.type in STYLE_TYPE_MAP: # 如果在修饰元素类型表中
                seg_cls, seg_type = STYLE_TYPE_MAP[element.type]
                message.append(seg_cls(seg_type, {'text': element.children[0].attrs['text']}))
            elif element.type in ['br', 'newline']: # 如果是换行
                message.append(Br('br', {'text': '\n'}))
            elif element.type in ['message', 'quote']: # 如果是消息或引用
                data = element.attrs.copy()
                if element.children: # 如果有子消息
                    data['content'] = Message.from_satori_element(element.children)
                message.append(RenderMessage(element.type, data)) # type: ignore
            else: # 其他元素直接作为纯文本处理
                message.append(Text('text', {'text': str(element)}))
        return message
