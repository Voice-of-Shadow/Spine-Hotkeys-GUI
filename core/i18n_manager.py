# -*- coding: utf-8 -*-
"""
国际化管理器模块
负责界面语言切换和文本渲染
"""

import json
import os
import sys
from typing import Dict, Optional, Tuple

from utils.resource_path import get_bundled_resource_path


class I18nManager:
    """国际化管理器"""
    
    def __init__(self, language_dir: str):
        """
        初始化国际化管理器
        
        Args:
            language_dir: 语言包目录路径
        """
        self.language_dir = language_dir
        self.current_language = ""
        self.interface_texts: Dict[str, str] = {}
        self.keydoc_texts: Dict[str, str] = {}

    def _read_texts(self, filename: str) -> Optional[Dict[str, str]]:
        directories = [self.language_dir]
        if getattr(sys, 'frozen', False):
            # 外部自定义翻译优先；升级后新加的键由内置语言包提供。
            directories.insert(0, get_bundled_resource_path("language"))

        texts = None
        for directory in directories:
            path = os.path.join(directory, filename)
            if os.path.isfile(path):
                with open(path, encoding="utf-8") as file:
                    entries = json.load(file)
                if texts is None:
                    texts = {}
                texts.update(entries)
        return texts
    
    def load_language(self, language_code: str) -> bool:
        """
        加载指定语言包
        
        Args:
            language_code: 语言代码（如 zh_CN）
            
        Returns:
            加载是否成功
        """
        try:
            interface_file = f"Interface.{language_code}.json"
            interface = self._read_texts(interface_file)
            if interface is None:
                print(f"界面语言包不存在: {interface_file}")
                return False

            self.keydoc_texts = self._read_texts(f"KeyDoc.{language_code}.json") or {}
            self.interface_texts = interface
            self.current_language = language_code
            return True
        except Exception as e:
            print(f"加载语言包失败: {e}")
            return False
    
    def get_text(self, key: str, default: Optional[str] = None) -> str:
        """
        获取界面文本
        
        Args:
            key: 文本键名
            default: 默认值（如果未指定则返回 key）
            
        Returns:
            对应的文本内容
        """
        if default is None:
            default = key
        return self.interface_texts.get(key, default)
    
    def get_keydoc(self, command_id: str) -> Tuple[str, str]:
        """
        获取命令的翻译和备注
        
        Args:
            command_id: 命令 ID
            
        Returns:
            (命令翻译, 备注信息)
        """
        
        name = self.keydoc_texts.get(command_id, command_id)
        
        note_key = f"{command_id}.note"
        note = self.keydoc_texts.get(note_key, "")
        
        return name, note
    
    def get_command_name(self, command_id: str) -> str:
        """
        获取命令名称翻译
        
        Args:
            command_id: 命令 ID
            
        Returns:
            翻译后的命令名称
        """
        return self.keydoc_texts.get(command_id, command_id)
    
    def get_command_note(self, command_id: str) -> str:
        """
        获取命令备注信息
        
        Args:
            command_id: 命令 ID
            
        Returns:
            备注信息
        """
        note_key = f"{command_id}.note"
        return self.keydoc_texts.get(note_key, "")
    
    def get_category_name(self, category_id: str) -> str:
        """
        获取类别翻译
        
        Args:
            category_id: 类别 ID
            
        Returns:
            翻译后的类别名称
        """
        return self.keydoc_texts.get(category_id, category_id)
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language
