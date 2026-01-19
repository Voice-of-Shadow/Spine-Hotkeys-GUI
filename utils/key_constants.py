# -*- coding: utf-8 -*-
"""
键盘常量定义模块
定义快捷键处理所需的各种常量和映射表
"""

KEY_NAMES = [
    # 字母 A-Z
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    # 主键盘数字及符号
    "NUM_0", "NUM_1", "NUM_2", "NUM_3", "NUM_4", "NUM_5", "NUM_6",
    "NUM_7", "NUM_8", "NUM_9",
    # 小键盘
    "NUMPAD_0", "NUMPAD_1", "NUMPAD_2", "NUMPAD_3", "NUMPAD_4", "NUMPAD_5", "NUMPAD_6",
    "NUMPAD_7", "NUMPAD_8", "NUMPAD_9", "NUMPAD_DIVIDE", "NUMPAD_DOT",
    "NUMPAD_ENTER", "NUMPAD_EQUALS", "NUMPAD_MINUS", "NUMPAD_MULTIPLY",
    "NUMPAD_PLUS", "NUMPAD_LEFT_PAREN", "NUMPAD_RIGHT_PAREN",
    # 其他功能键与符号键
    "APOSTROPHE", "AT", "BACKSLASH", "BACKSPACE", "COLON", "COMMA", "DELETE",
    "END", "ENTER", "EQUALS", "ESCAPE", "GRAVE", "HOME", "INSERT",
    "LEFT_BRACKET", "MINUS", "NUM_LOCK", "PAGE_UP", "PAGE_DOWN",
    "PERIOD", "PLUS", "POUND", "PRINT_SCREEN", "RIGHT_BRACKET",
    "SCROLL_LOCK", "SEMICOLON", "SLASH", "SPACE", "STAR", "TAB",
    # 方向键
    "DOWN", "LEFT", "RIGHT", "UP",
    # 功能键 F1-F24
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24"
]

KEY_TO_CHAR = {
    'GRAVE': '`',
    'AT': '@',
    'POUND': '#',
    'MINUS': '-',
    'PLUS': '+',
    'EQUALS': '=',
    'LEFT_BRACKET': '[',
    'RIGHT_BRACKET': ']',
    'BACKSLASH': '\\',
    'SEMICOLON': ';',
    'APOSTROPHE': "'",
    'COLON': ':',
    'COMMA': ',',
    'PERIOD': '.',
    'SLASH': '/',
    'SPACE': ' ',
    'STAR': '*',
    'NUM_0': '0',
    'NUM_1': '1',
    'NUM_2': '2',
    'NUM_3': '3',
    'NUM_4': '4',
    'NUM_5': '5',
    'NUM_6': '6',
    'NUM_7': '7',
    'NUM_8': '8',
    'NUM_9': '9'
}

CHAR_TO_KEY = {
    '0': 'NUM_0',
    '1': 'NUM_1',
    '2': 'NUM_2',
    '3': 'NUM_3',
    '4': 'NUM_4',
    '5': 'NUM_5',
    '6': 'NUM_6',
    '7': 'NUM_7',
    '8': 'NUM_8',
    '9': 'NUM_9'
}

NUMPAD_KEYS = {
    "NUMPAD_0", "NUMPAD_1", "NUMPAD_2", "NUMPAD_3", "NUMPAD_4",
    "NUMPAD_5", "NUMPAD_6", "NUMPAD_7", "NUMPAD_8", "NUMPAD_9",
    "NUMPAD_DIVIDE", "NUMPAD_DOT", "NUMPAD_ENTER", "NUMPAD_EQUALS",
    "NUMPAD_MINUS", "NUMPAD_MULTIPLY", "NUMPAD_PLUS",
    "NUMPAD_LEFT_PAREN", "NUMPAD_RIGHT_PAREN"
}

SHIFT_CHAR_MAP = {
    'GRAVE': '~',
    'NUM_1': '!',
    'NUM_2': '@',
    'NUM_3': '#',
    'NUM_4': '$',
    'NUM_5': '%',
    'NUM_6': '^',
    'NUM_7': '&',
    'NUM_8': '*',
    'NUM_9': '(',
    'NUM_0': ')',
    'MINUS': '_',
    'EQUALS': '+',
    'LEFT_BRACKET': '{',
    'RIGHT_BRACKET': '}',
    'BACKSLASH': '|',
    'SEMICOLON': ':',
    'APOSTROPHE': '"',
    'COMMA': '<',
    'PERIOD': '>',
    'SLASH': '?'
}

VALID_MODIFIERS = {'ctrl', 'alt', 'shift'}

MODIFIER_ORDER = ['ctrl', 'shift', 'alt']

from PySide6.QtCore import Qt

QT_KEY_TO_NAME = {
    # 字母
    Qt.Key_A: 'A', Qt.Key_B: 'B', Qt.Key_C: 'C', Qt.Key_D: 'D',
    Qt.Key_E: 'E', Qt.Key_F: 'F', Qt.Key_G: 'G', Qt.Key_H: 'H',
    Qt.Key_I: 'I', Qt.Key_J: 'J', Qt.Key_K: 'K', Qt.Key_L: 'L',
    Qt.Key_M: 'M', Qt.Key_N: 'N', Qt.Key_O: 'O', Qt.Key_P: 'P',
    Qt.Key_Q: 'Q', Qt.Key_R: 'R', Qt.Key_S: 'S', Qt.Key_T: 'T',
    Qt.Key_U: 'U', Qt.Key_V: 'V', Qt.Key_W: 'W', Qt.Key_X: 'X',
    Qt.Key_Y: 'Y', Qt.Key_Z: 'Z',
    # 主键盘数字
    Qt.Key_0: 'NUM_0', Qt.Key_1: 'NUM_1', Qt.Key_2: 'NUM_2',
    Qt.Key_3: 'NUM_3', Qt.Key_4: 'NUM_4', Qt.Key_5: 'NUM_5',
    Qt.Key_6: 'NUM_6', Qt.Key_7: 'NUM_7', Qt.Key_8: 'NUM_8',
    Qt.Key_9: 'NUM_9',
    # 功能键
    Qt.Key_F1: 'F1', Qt.Key_F2: 'F2', Qt.Key_F3: 'F3', Qt.Key_F4: 'F4',
    Qt.Key_F5: 'F5', Qt.Key_F6: 'F6', Qt.Key_F7: 'F7', Qt.Key_F8: 'F8',
    Qt.Key_F9: 'F9', Qt.Key_F10: 'F10', Qt.Key_F11: 'F11', Qt.Key_F12: 'F12',
    Qt.Key_F13: 'F13', Qt.Key_F14: 'F14', Qt.Key_F15: 'F15', Qt.Key_F16: 'F16',
    Qt.Key_F17: 'F17', Qt.Key_F18: 'F18', Qt.Key_F19: 'F19', Qt.Key_F20: 'F20',
    Qt.Key_F21: 'F21', Qt.Key_F22: 'F22', Qt.Key_F23: 'F23', Qt.Key_F24: 'F24',
    # 方向键
    Qt.Key_Up: 'UP', Qt.Key_Down: 'DOWN', Qt.Key_Left: 'LEFT', Qt.Key_Right: 'RIGHT',
    # 其他功能键
    Qt.Key_Escape: 'ESCAPE', Qt.Key_Tab: 'TAB', Qt.Key_Backspace: 'BACKSPACE',
    Qt.Key_Return: 'ENTER', Qt.Key_Enter: 'NUMPAD_ENTER',
    Qt.Key_Insert: 'INSERT', Qt.Key_Delete: 'DELETE',
    Qt.Key_Home: 'HOME', Qt.Key_End: 'END',
    Qt.Key_PageUp: 'PAGE_UP', Qt.Key_PageDown: 'PAGE_DOWN',
    Qt.Key_Space: 'SPACE', Qt.Key_Print: 'PRINT_SCREEN',
    Qt.Key_ScrollLock: 'SCROLL_LOCK', Qt.Key_NumLock: 'NUM_LOCK',
    # 符号键
    Qt.Key_QuoteLeft: 'GRAVE', Qt.Key_Minus: 'MINUS', Qt.Key_Equal: 'EQUALS',
    Qt.Key_BracketLeft: 'LEFT_BRACKET', Qt.Key_BracketRight: 'RIGHT_BRACKET',
    Qt.Key_Backslash: 'BACKSLASH', Qt.Key_Semicolon: 'SEMICOLON',
    Qt.Key_Apostrophe: 'APOSTROPHE', Qt.Key_Comma: 'COMMA',
    Qt.Key_Period: 'PERIOD', Qt.Key_Slash: 'SLASH',
    Qt.Key_Plus: 'PLUS', Qt.Key_Asterisk: 'STAR',
    Qt.Key_At: 'AT', Qt.Key_NumberSign: 'POUND', Qt.Key_Colon: 'COLON',
}

QT_NUMPAD_KEYS = {
    Qt.Key_0: 'NUMPAD_0', Qt.Key_1: 'NUMPAD_1', Qt.Key_2: 'NUMPAD_2',
    Qt.Key_3: 'NUMPAD_3', Qt.Key_4: 'NUMPAD_4', Qt.Key_5: 'NUMPAD_5',
    Qt.Key_6: 'NUMPAD_6', Qt.Key_7: 'NUMPAD_7', Qt.Key_8: 'NUMPAD_8',
    Qt.Key_9: 'NUMPAD_9',
}


def is_numpad_key(key_name: str) -> bool:
    """判断是否为小键盘按键"""
    return key_name in NUMPAD_KEYS


def get_key_name_from_qt(qt_key: int, is_keypad: bool = False) -> str:
    """从 Qt 键码获取键名"""
    if is_keypad and qt_key in QT_NUMPAD_KEYS:
        return QT_NUMPAD_KEYS[qt_key]
    return QT_KEY_TO_NAME.get(qt_key, '')


def get_char_from_key(key_name: str, shift_pressed: bool = False) -> str:
    """根据物理键和 Shift 状态获取字符"""
    if shift_pressed and key_name in SHIFT_CHAR_MAP:
        return SHIFT_CHAR_MAP[key_name]
    return KEY_TO_CHAR.get(key_name, '')
