# -*- coding: utf-8 -*-
"""
国际化管理器模块
负责界面语言切换和文本渲染
"""

import json
import os
from typing import Any, Dict, Optional, Tuple


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
    
    def load_language(self, language_code: str) -> bool:
        """
        加载指定语言包
        
        Args:
            language_code: 语言代码（如 zh_CN）
            
        Returns:
            加载是否成功
        """
        try:
            interface_path = os.path.join(
                self.language_dir, f"Interface.{language_code}.json"
            )
            if os.path.exists(interface_path):
                with open(interface_path, 'r', encoding='utf-8') as f:
                    self.interface_texts = json.load(f)
            else:
                print(f"界面语言包不存在: {interface_path}")
                return False
            
            keydoc_path = os.path.join(
                self.language_dir, f"KeyDoc.{language_code}.json"
            )
            if os.path.exists(keydoc_path):
                with open(keydoc_path, 'r', encoding='utf-8') as f:
                    self.keydoc_texts = json.load(f)
            else:
                print(f"快捷键文档语言包不存在: {keydoc_path}")
                self.keydoc_texts = {}
            
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
