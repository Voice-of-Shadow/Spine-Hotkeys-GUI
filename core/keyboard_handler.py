# -*- coding: utf-8 -*-
"""
键盘处理器模块
实现核心处理规则，处理键盘事件并生成快捷键字符串
"""

from typing import Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent

from utils.key_constants import (
    KEY_NAMES,
    KEY_TO_CHAR,
    NUMPAD_KEYS,
    SHIFT_CHAR_MAP,
    MODIFIER_ORDER,
    QT_KEY_TO_NAME,
    get_key_name_from_qt,
    is_numpad_key
)


class KeyboardHandler:
    """键盘处理器"""

    MODIFIER_KEYS = {
        Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta,
        Qt.Key_AltGr, Qt.Key_CapsLock, Qt.Key_NumLock, Qt.Key_ScrollLock
    }
    
    def __init__(self, mode: str = 'normal'):
        """
        初始化键盘处理器
        
        Args:
            mode: 处理模式 ('normal' 或 'character')
        """
        self.mode = mode
    
    def set_mode(self, mode: str) -> None:
        """
        设置处理模式
        
        Args:
            mode: 'normal' 或 'character'
        """
        self.mode = mode
    
    def is_modifier_only(self, event: QKeyEvent) -> bool:
        """
        判断是否只按下了修饰键
        
        Args:
            event: 键盘事件
            
        Returns:
            是否只是修饰键
        """
        return event.key() in self.MODIFIER_KEYS
    
    def process_key_event(self, event: QKeyEvent) -> Optional[str]:
        """
        处理键盘事件，生成快捷键字符串
        
        Args:
            event: 键盘事件
            
        Returns:
            快捷键字符串，无效返回 None
        """
        if self.is_modifier_only(event):
            return None
        
        if self.mode == 'character':
            return self._process_character_mode(event)
        else:
            return self._process_normal_mode(event)
    
    def _get_modifiers(self, event: QKeyEvent) -> Tuple[bool, bool, bool]:
        """
        获取修饰键状态
        
        Returns:
            (ctrl_pressed, shift_pressed, alt_pressed)
        """
        modifiers = event.modifiers()
        ctrl = bool(modifiers & Qt.ControlModifier)
        shift = bool(modifiers & Qt.ShiftModifier)
        alt = bool(modifiers & Qt.AltModifier)
        return ctrl, shift, alt
    
    def _process_normal_mode(self, event: QKeyEvent) -> Optional[str]:
        """
        一般模式处理
        
        Args:
            event: 键盘事件
            
        Returns:
            快捷键字符串
        """
        ctrl, shift, alt = self._get_modifiers(event)
        
        qt_key = event.key()
        
        is_keypad = bool(event.modifiers() & Qt.KeypadModifier)
        key_name = get_key_name_from_qt(qt_key, is_keypad)
        
        if not key_name:
            text = event.text().upper()
            if len(text) == 1 and text.isalpha():
                key_name = text
        
        if not key_name or key_name not in KEY_NAMES:
            return None
        
        return self._build_shortcut_string(ctrl, shift, alt, key_name)
    
    def _process_character_mode(self, event: QKeyEvent) -> Optional[str]:
        """
        字符模式处理
        
        Args:
            event: 键盘事件
            
        Returns:
            快捷键字符串
        """
        ctrl, shift, alt = self._get_modifiers(event)
        
        is_keypad = bool(event.modifiers() & Qt.KeypadModifier)
        if is_keypad:
            return None
        
        qt_key = event.key()
        key_name = get_key_name_from_qt(qt_key, False)
        
        if key_name and is_numpad_key(key_name):
            return None
        
        char = None
        
        text = event.text()
        if text and len(text) == 1 and text.isprintable():
            char = text
        else:
            if key_name:
                if shift and key_name in SHIFT_CHAR_MAP:
                    char = SHIFT_CHAR_MAP[key_name]
                elif key_name in KEY_TO_CHAR:
                    char = KEY_TO_CHAR[key_name]
                elif len(key_name) == 1:
                    char = key_name.lower() if not shift else key_name.upper()
        
        if not char:
            return None
        
        if alt:
            return f"alt + '{char}'"
        else:
            return f"'{char}'"
    
    def _build_shortcut_string(self, ctrl: bool, shift: bool, alt: bool,
                                key_name: str) -> str:
        """
        构建快捷键字符串
        
        Args:
            ctrl: Ctrl 是否按下
            shift: Shift 是否按下
            alt: Alt 是否按下
            key_name: 键名
            
        Returns:
            格式化的快捷键字符串
        """
        modifiers = []
        if ctrl:
            modifiers.append('ctrl')
        if shift:
            modifiers.append('shift')
        if alt:
            modifiers.append('alt')
        
        if modifiers:
            return f"{' + '.join(modifiers)} + {key_name}"
        else:
            return key_name
    
    def is_valid_key(self, key_name: str) -> bool:
        """
        验证键名是否有效
        
        Args:
            key_name: 键名
            
        Returns:
            是否有效
        """
        if self.mode == 'character':
            return not is_numpad_key(key_name)
        else:
            return key_name in KEY_NAMES
