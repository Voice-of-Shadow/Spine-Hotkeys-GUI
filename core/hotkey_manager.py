# -*- coding: utf-8 -*-
"""
快捷键数据管理器模块
负责快捷键 JSON 数据的 CRUD 操作
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple


class HotkeyManager:
    """快捷键数据管理器"""
    
    def __init__(self):
        """初始化快捷键管理器"""
        self.data: List[Dict[str, Any]] = []
        self.json_path: str = ""
        self._modified: bool = False
    
    def load_from_json(self, json_path: str) -> bool:
        """
        从 JSON 文件加载数据
        
        Args:
            json_path: JSON 文件路径
            
        Returns:
            加载是否成功
        """
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                self.json_path = json_path
                self._modified = False
                return True
            return False
        except Exception as e:
            print(f"加载快捷键数据失败: {e}")
            return False
    
    def save_to_json(self, json_path: Optional[str] = None) -> bool:
        """
        保存数据到 JSON 文件
        
        Args:
            json_path: JSON 文件路径（默认使用加载时的路径）
            
        Returns:
            保存是否成功
        """
        try:
            path = json_path or self.json_path
            if not path:
                return False
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            self._modified = False
            return True
        except Exception as e:
            print(f"保存快捷键数据失败: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """
        获取所有类别 ID 列表
        
        Returns:
            类别 ID 列表
        """
        return [cat.get("categoryId", "") for cat in self.data]
    
    def get_items_by_category(self, category_id: str) -> List[Dict[str, Any]]:
        """
        根据类别 ID 获取快捷键项列表
        
        Args:
            category_id: 类别 ID
            
        Returns:
            快捷键项列表
        """
        for category in self.data:
            if category.get("categoryId") == category_id:
                return category.get("items", [])
        return []
    
    def get_item(self, category_id: str, command_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定的快捷键项
        
        Args:
            category_id: 类别 ID
            command_id: 命令 ID
            
        Returns:
            快捷键项，未找到返回 None
        """
        items = self.get_items_by_category(category_id)
        for item in items:
            if item.get("commandId") == command_id:
                return item
        return None
    
    def add_shortcut(self, category_id: str, command_id: str, shortcut: str) -> bool:
        """
        为命令添加快捷键
        
        Args:
            category_id: 类别 ID
            command_id: 命令 ID
            shortcut: 快捷键字符串
            
        Returns:
            添加是否成功
        """
        item = self.get_item(category_id, command_id)
        if item is not None:
            if shortcut not in item.get("shortcuts", []):
                item.setdefault("shortcuts", []).append(shortcut)
                self._modified = True
                return True
        return False
    
    def remove_shortcut(self, category_id: str, command_id: str, shortcut: str) -> bool:
        """
        删除命令的快捷键
        
        Args:
            category_id: 类别 ID
            command_id: 命令 ID
            shortcut: 快捷键字符串
            
        Returns:
            删除是否成功
        """
        item = self.get_item(category_id, command_id)
        if item is not None and shortcut in item.get("shortcuts", []):
            item["shortcuts"].remove(shortcut)
            self._modified = True
            return True
        return False
    
    def update_shortcut(self, category_id: str, command_id: str,
                        old_shortcut: str, new_shortcut: str) -> bool:
        """
        修改命令的快捷键
        
        Args:
            category_id: 类别 ID
            command_id: 命令 ID
            old_shortcut: 原快捷键
            new_shortcut: 新快捷键
            
        Returns:
            修改是否成功
        """
        item = self.get_item(category_id, command_id)
        if item is not None:
            shortcuts = item.get("shortcuts", [])
            if old_shortcut in shortcuts:
                index = shortcuts.index(old_shortcut)
                shortcuts[index] = new_shortcut
                self._modified = True
                return True
            elif old_shortcut == "" and new_shortcut:
                shortcuts.append(new_shortcut)
                self._modified = True
                return True
        return False
    
    def set_shortcut_at_index(self, category_id: str, command_id: str,
                               index: int, shortcut: str) -> bool:
        """
        设置指定索引位置的快捷键
        
        Args:
            category_id: 类别 ID
            command_id: 命令 ID
            index: 快捷键索引
            shortcut: 新快捷键
            
        Returns:
            设置是否成功
        """
        item = self.get_item(category_id, command_id)
        if item is not None:
            shortcuts = item.get("shortcuts", [])
            if 0 <= index < len(shortcuts):
                shortcuts[index] = shortcut
                self._modified = True
                return True
        return False
    
    def add_empty_shortcut(self, category_id: str, command_id: str) -> int:
        """
        为命令添加一个空快捷键位置
        
        Args:
            category_id: 类别 ID
            command_id: 命令 ID
            
        Returns:
            新增位置的索引，失败返回 -1
        """
        item = self.get_item(category_id, command_id)
        if item is not None:
            shortcuts = item.setdefault("shortcuts", [])
            shortcuts.append("")
            self._modified = True
            return len(shortcuts) - 1
        return -1
    
    def remove_shortcut_at_index(self, category_id: str, command_id: str, index: int) -> bool:
        """
        删除指定索引位置的快捷键
        
        Args:
            category_id: 类别 ID
            command_id: 命令 ID
            index: 快捷键索引
            
        Returns:
            删除是否成功
        """
        item = self.get_item(category_id, command_id)
        if item is not None:
            shortcuts = item.get("shortcuts", [])
            if 0 <= index < len(shortcuts):
                shortcuts.pop(index)
                self._modified = True
                return True
        return False
    
    def get_all_shortcuts(self) -> List[Tuple[str, str, str, int]]:
        """
        获取所有快捷键的扁平列表
        
        Returns:
            [(category_id, command_id, shortcut, index), ...]
        """
        result = []
        for category in self.data:
            category_id = category.get("categoryId", "")
            for item in category.get("items", []):
                command_id = item.get("commandId", "")
                for idx, shortcut in enumerate(item.get("shortcuts", [])):
                    if shortcut:
                        result.append((category_id, command_id, shortcut, idx))
        return result
    
    def find_commands_by_shortcut(self, shortcut: str) -> List[Tuple[str, str, int]]:
        """
        查找使用某快捷键的所有命令
        
        Args:
            shortcut: 快捷键字符串
            
        Returns:
            [(category_id, command_id, index), ...]
        """
        result = []
        if not shortcut:
            return result
        
        for category in self.data:
            category_id = category.get("categoryId", "")
            for item in category.get("items", []):
                command_id = item.get("commandId", "")
                shortcuts = item.get("shortcuts", [])
                for idx, s in enumerate(shortcuts):
                    if s == shortcut:
                        result.append((category_id, command_id, idx))
        return result
    
    def is_modified(self) -> bool:
        """判断数据是否被修改"""
        return self._modified
    
    def set_modified(self, modified: bool = True) -> None:
        """设置修改标志"""
        self._modified = modified
    
    def get_json_path(self) -> str:
        """获取当前加载的 JSON 文件路径"""
        return self.json_path
