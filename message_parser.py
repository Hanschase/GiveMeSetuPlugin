"""
消息解析模块
用于解析用户输入的命令并提取参数
"""

import re
from typing import Dict, List, Any
from .config import Config


class MessageParser:
    def __init__(self):
        self.config = Config()
        # 支持的关键词
        self.keywords = ['色图', '涩图', 'setu']
        # R18关键词
        self.r18_keywords = ['r18', 'R18']
    
    def parse_command(self, message: str) -> Dict[str, Any]:
        """
        解析消息命令
        返回: {
            'is_valid': bool,
            'source': 'lolicon'|'cloud'|'auto',
            'tags': list,
            'r18': bool
        }
        """
        message = message.strip()
        
        # 检查是否以支持的关键词开头
        if not self._is_valid_keyword(message):
            return {
                'is_valid': False,
                'source': self.config.DEFAULT_SOURCE,
                'tags': [],
                'r18': False
            }
        
        # 分割消息
        parts = message.split()
        
        # 找到匹配的关键词和提取真正的关键词部分
        keyword = ""
        keyword_end_index = 0
        
        for kw in self.keywords:
            if message.lower().startswith(kw.lower()):
                keyword = kw
                keyword_end_index = len(kw)
                break
            elif message.lower().startswith('r18' + kw.lower()):
                keyword = 'r18' + kw
                keyword_end_index = len('r18' + kw)
                break
            elif message.lower().startswith('r' + kw.lower()):
                keyword = 'r' + kw  
                keyword_end_index = len('r' + kw)
                break
        
        # 提取关键词后的剩余部分作为参数
        remaining_message = message[keyword_end_index:].strip()
        args = remaining_message.split() if remaining_message else []
        
        # 检测R18
        r18_flag = self._detect_r18(keyword)
        if not r18_flag:
            r18_flag = self.config.DEFAULT_R18_FLAG
        
        # 解析源和标签
        source, tags = self._parse_source_and_tags(args)
        
        return {
            'is_valid': True,
            'source': source,
            'tags': tags,
            'r18': r18_flag
        }
    
    def _is_valid_keyword(self, message: str) -> bool:
        """检查消息是否以有效关键词开头"""
        message_lower = message.lower()
        for keyword in self.keywords:
            # 检查是否以关键词开头（可能包含r18前缀）
            patterns = [
                keyword.lower(),
                'r18' + keyword.lower(),
                'r' + keyword.lower()
            ]
            
            for pattern in patterns:
                if message_lower.startswith(pattern):
                    # 确保关键词后面是空格或字符串结束，避免"setu图"这种情况
                    if len(message) == len(pattern) or message[len(pattern)].isspace():
                        return True
        return False
    
    def _detect_r18(self, keyword: str) -> bool:
        """检测R18标志"""
        keyword_lower = keyword.lower()
        return any(r18_kw in keyword_lower for r18_kw in self.r18_keywords)
    
    def _parse_source_and_tags(self, args: List[str]) -> tuple:
        """
        解析源和标签
        返回: (source, tags)
        """
        source = self.config.DEFAULT_SOURCE
        tags = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # 检查是否是源参数
            if arg == '-s' and i + 1 < len(args):
                next_arg = args[i + 1].lower()
                if next_arg in ['lolicon', 'cloud']:
                    source = next_arg
                    i += 2  # 跳过 -s 和源名称
                    continue
                else:
                    # -s 后面跟的不是有效源，当作标签处理
                    tags.append(arg)
                    i += 1
            else:
                # 普通标签
                tags.append(arg)
                i += 1
        
        return source, tags
    
    def get_help_text(self) -> str:
        """获取帮助文本"""
        return """
命令格式：色图|涩图 [-s [lolicon|cloud]] [tag,...]

参数说明：
- -s lolicon：从Lolicon API获取图片（默认）
- -s cloud：从NextCloud随机获取图片
- tag：图片标签（仅对lolicon有效）

示例：
- 涩图：随机获取图片
- 涩图 莉音：获取标签为"莉音"的图片
- 涩图 -s cloud：从NextCloud获取图片
- r18涩图：获取R18图片（需要权限）
        """.strip()
