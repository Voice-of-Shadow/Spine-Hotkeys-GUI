# -*- coding: utf-8 -*-
"""
冲突检测器模块
负责检测全局快捷键冲突
"""

from typing import Dict, List, Optional, Set, Tuple

from .hotkey_manager import HotkeyManager


class ConflictDetector:
    """冲突检测器"""
    
    def __init__(self, hotkey_manager: HotkeyManager):
        """
        初始化冲突检测器
        
        Args:
            hotkey_manager: 快捷键管理器实例
        """
        self.hotkey_manager = hotkey_manager
        self._conflict_cache: Dict[str, List[Tuple[str, str]]] = {}
        self._cache_valid = False
    
    def invalidate_cache(self) -> None:
        """使缓存失效"""
        self._cache_valid = False
        self._conflict_cache.clear()
    
    def detect_all_conflicts(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        全局冲突检测
        
        Returns:
            冲突字典 {shortcut: [(category_id, command_id), ...]}
            仅包含有多个命令使用的快捷键
        """
        shortcut_map: Dict[str, List[Tuple[str, str]]] = {}
        
        all_shortcuts = self.hotkey_manager.get_all_shortcuts()
        for category_id, command_id, shortcut, _ in all_shortcuts:
            if shortcut:
                if shortcut not in shortcut_map:
                    shortcut_map[shortcut] = []
                shortcut_map[shortcut].append((category_id, command_id))
        
        conflicts = {
            shortcut: commands
            for shortcut, commands in shortcut_map.items()
            if len(commands) > 1
        }
        
        self._conflict_cache = conflicts
        self._cache_valid = True
        
        return conflicts
    
    def check_conflict(self, shortcut: str,
                       exclude_category: Optional[str] = None,
                       exclude_command: Optional[str] = None) -> bool:
        """
        检测某个快捷键是否与其他命令冲突
        
        Args:
            shortcut: 要检测的快捷键
            exclude_category: 排除的类别 ID
            exclude_command: 排除的命令 ID
            
        Returns:
            是否存在冲突
        """
        if not shortcut:
            return False
        
        commands = self.hotkey_manager.find_commands_by_shortcut(shortcut)
        
        if exclude_category and exclude_command:
            commands = [
                (cat, cmd, idx)
                for cat, cmd, idx in commands
                if not (cat == exclude_category and cmd == exclude_command)
            ]
        
        return len(commands) > 0
    
    def get_conflicting_commands(self, shortcut: str,
                                  exclude_category: Optional[str] = None,
                                  exclude_command: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        获取与某快捷键冲突的命令列表
        
        Args:
            shortcut: 快捷键
            exclude_category: 排除的类别 ID
            exclude_command: 排除的命令 ID
            
        Returns:
            [(category_id, command_id), ...]
        """
        if not shortcut:
            return []
        
        commands = self.hotkey_manager.find_commands_by_shortcut(shortcut)
        
        result_set: Set[Tuple[str, str]] = set()
        for cat, cmd, _ in commands:
            if exclude_category and exclude_command:
                if cat == exclude_category and cmd == exclude_command:
                    continue
            result_set.add((cat, cmd))
        
        return list(result_set)
    
    def get_shortcuts_with_conflicts(self) -> Set[str]:
        """
        获取所有存在冲突的快捷键集合
        
        Returns:
            冲突快捷键集合
        """
        if not self._cache_valid:
            self.detect_all_conflicts()
        return set(self._conflict_cache.keys())
    
    def is_shortcut_conflicting(self, shortcut: str) -> bool:
        """
        检查快捷键是否在冲突列表中
        
        Args:
            shortcut: 快捷键
            
        Returns:
            是否冲突
        """
        if not self._cache_valid:
            self.detect_all_conflicts()
        return shortcut in self._conflict_cache
