# -*- coding: utf-8 -*-
"""
自定义对话框模块
包含信息提示窗、操作确认窗、录入提示窗、单按钮提示窗
"""

import os
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextBrowser, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.keyboard_handler import KeyboardHandler


def _load_global_stylesheet() -> str:
    """加载全局样式表"""
    from utils.resource_path import get_bundled_resource_path
    
    style_path = get_bundled_resource_path("styles/style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            stylesheet = f.read()
        
        icon_dir = get_bundled_resource_path("icon")
        icon_dir = icon_dir.replace(os.sep, '/')
        stylesheet = stylesheet.replace('./icon/', f'{icon_dir}/')
        
        return stylesheet
    return ""


def _get_icon_path() -> str:
    """获取图标路径"""
    from utils.resource_path import get_bundled_resource_path
    return get_bundled_resource_path("icon/icon.png")


class InfoDialog(QDialog):
    """
    信息提示窗 (A)
    用于信息展示（使用说明、快捷键说明、关键字对应、程序信息）
    """
    
    def __init__(self, parent: Optional[QWidget], title: str, content: str,
                 button_text: str = "确认", use_markdown: bool = False,
                 is_about: bool = False):
        """
        初始化信息提示窗
        
        Args:
            parent: 父窗口
            title: 对话框标题
            content: 内容文本
            button_text: 按钮文本
            use_markdown: 是否使用 Markdown 渲染（默认关闭）
            is_about: 是否为程序信息对话框
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        if is_about:
            self.setFixedSize(320, 220)
        else:
            self.setMinimumSize(400, 250)
        
        icon_path = _get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        if is_about:
            self.content_browser = QTextBrowser()
            self.content_browser.setObjectName("aboutContent")
            self.content_browser.setOpenExternalLinks(True)
            self.content_browser.setReadOnly(True)
            self.content_browser.setStyleSheet("background-color: transparent; border: none;")
            self.content_browser.setMarkdown(content)
            layout.addWidget(self.content_browser, 4)
        else:
            self.content_browser = QTextBrowser()
            self.content_browser.setOpenExternalLinks(True)
            self.content_browser.setReadOnly(True)
            
            if use_markdown:
                self.content_browser.setMarkdown(content)
            else:
                self.content_browser.setPlainText(content)
            
            layout.addWidget(self.content_browser, 4)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_ok = QPushButton(button_text)
        self.btn_ok.setObjectName("btnOk")
        self.btn_ok.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_ok)
        button_layout.addStretch()
        layout.addLayout(button_layout, 1)
        
        self.setStyleSheet(_load_global_stylesheet())


class AlertDialog(QDialog):
    """
    单按钮提示窗
    用于 warning、link、formatError 类型的提示
    与 ConfirmDialog 样式一致，但只有一个确认按钮
    """
    
    def __init__(self, parent: Optional[QWidget], title: str, content: str,
                 button_text: str = "确认"):
        """
        初始化单按钮提示窗
        
        Args:
            parent: 父窗口
            title: 对话框标题
            content: 内容文本
            button_text: 按钮文本
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(350, 150)
        self.setModal(True)
        
        icon_path = _get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.label_content = QLabel(content)
        self.label_content.setWordWrap(True)
        self.label_content.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_content, 4)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_confirm = QPushButton(button_text)
        self.btn_confirm.setObjectName("btnConfirm")
        self.btn_confirm.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_confirm)
        button_layout.addStretch()
        layout.addLayout(button_layout, 1)
        
        self.setStyleSheet(_load_global_stylesheet())
    
    @staticmethod
    def show_alert(parent: Optional[QWidget], title: str, content: str,
                   button_text: str = "确认") -> None:
        """
        静态方法：显示单按钮提示对话框
        """
        dialog = AlertDialog(parent, title, content, button_text)
        dialog.exec()


class ConfirmDialog(QDialog):
    """
    操作确认窗 (B)
    用于重要操作确认，提供是/否/取消三个选项
    """
    
    YES = 1
    NO = 0
    CANCEL = -1
    
    def __init__(self, parent: Optional[QWidget], title: str, content: str,
                 yes_text: str = "是", no_text: str = "否", cancel_text: str = "取消"):
        """
        初始化操作确认窗
        
        Args:
            parent: 父窗口
            title: 对话框标题
            content: 内容文本
            yes_text: "是"按钮文本
            no_text: "否"按钮文本
            cancel_text: "取消"按钮文本
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(350, 150)
        self.setModal(True)
        
        self._result = self.CANCEL
        
        icon_path = _get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.label_content = QLabel(content)
        self.label_content.setWordWrap(True)
        self.label_content.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_content, 4)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_yes = QPushButton(yes_text)
        self.btn_yes.setObjectName("btnYes")
        self.btn_yes.setStyleSheet("""
            QPushButton#btnYes {
                background-color: #1070e0;
                color: white;
                border: 1px solid #0d5dbf;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
                min-height: 28px;
            }
            QPushButton#btnYes:hover {
                background-color: #0d5dbf;
            }
            QPushButton#btnYes:pressed {
                background-color: #0a4a9e;
            }
        """)
        self.btn_yes.clicked.connect(self._on_yes)
        button_layout.addWidget(self.btn_yes)
        
        self.btn_no = QPushButton(no_text)
        self.btn_no.setObjectName("btnNo")
        self.btn_no.clicked.connect(self._on_no)
        button_layout.addWidget(self.btn_no)
        
        self.btn_cancel = QPushButton(cancel_text)
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.btn_cancel)
        
        button_layout.addStretch()
        layout.addLayout(button_layout, 1)
        
        self.setStyleSheet(_load_global_stylesheet())
    
    def _on_yes(self):
        """处理"是"按钮点击"""
        self._result = self.YES
        self.accept()
    
    def _on_no(self):
        """处理"否"按钮点击"""
        self._result = self.NO
        self.reject()
    
    def _on_cancel(self):
        """处理"取消"按钮点击"""
        self._result = self.CANCEL
        self.reject()
    
    def get_result(self) -> int:
        """获取用户选择结果"""
        return self._result
    
    @staticmethod
    def ask(parent: Optional[QWidget], title: str, content: str,
            yes_text: str = "是", no_text: str = "否",
            cancel_text: str = "取消") -> int:
        """
        静态方法：显示确认对话框并返回结果
        
        Returns:
            ConfirmDialog.YES, ConfirmDialog.NO, 或 ConfirmDialog.CANCEL
        """
        dialog = ConfirmDialog(parent, title, content, yes_text, no_text, cancel_text)
        dialog.exec()
        return dialog.get_result()


class KeyInputDialog(QDialog):
    """
    录入提示窗 (C)
    用于快捷键录入，监听键盘输入
    """
    
    hotkey_captured = Signal(str)
    
    def __init__(self, parent: Optional[QWidget], mode: str = 'normal',
                 current_hotkey: str = "", mode_text: str = "一般模式",
                 prompt_text: str = "请从键盘按下要设置的快捷键",
                 delete_text: str = "删除快捷键", cancel_text: str = "取消"):
        """
        初始化录入提示窗
        
        Args:
            parent: 父窗口
            mode: 处理模式 ('normal' 或 'character')
            current_hotkey: 当前快捷键（用于判断是否启用删除按钮）
            mode_text: 模式显示文本
            prompt_text: 提示文本
            delete_text: 删除按钮文本
            cancel_text: 取消按钮文本
        """
        super().__init__(parent)
        
        self.mode = mode
        self.current_hotkey = current_hotkey
        self._captured_hotkey: Optional[str] = None
        self._deleted = False
        self.keyboard_handler = KeyboardHandler(mode)
        
        self.setWindowTitle(mode_text)
        self.setFixedSize(400, 160)
        self.setModal(True)
        
        icon_path = _get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.label_prompt = QLabel(prompt_text)
        self.label_prompt.setObjectName("promptLabel")
        self.label_prompt.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_prompt, 4)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_delete = QPushButton(delete_text)
        self.btn_delete.setObjectName("btnCancel")
        self.btn_delete.setEnabled(bool(current_hotkey))
        self.btn_delete.clicked.connect(self._on_delete)
        button_layout.addWidget(self.btn_delete)
        
        self.btn_cancel = QPushButton(cancel_text)
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        button_layout.addStretch()
        layout.addLayout(button_layout, 1)
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(_load_global_stylesheet())
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """处理键盘按下事件"""
        if event.key() == Qt.Key_Escape:
            self.reject()
            return
        
        shortcut = self.keyboard_handler.process_key_event(event)
        
        if shortcut:
            self._captured_hotkey = shortcut
            self.accept()
    
    def _on_delete(self):
        """处理删除按钮点击"""
        self._deleted = True
        self._captured_hotkey = ""
        self.accept()
    
    def get_hotkey(self) -> Optional[str]:
        """
        获取录入的快捷键
        
        Returns:
            快捷键字符串，删除返回空字符串，取消返回 None
        """
        return self._captured_hotkey
    
    def is_deleted(self) -> bool:
        """是否选择了删除"""
        return self._deleted
    
    @staticmethod
    def capture(parent: Optional[QWidget], mode: str = 'normal',
                current_hotkey: str = "", mode_text: str = "一般模式",
                prompt_text: str = "请从键盘按下要设置的快捷键",
                delete_text: str = "删除快捷键",
                cancel_text: str = "取消") -> Optional[str]:
        """
        静态方法：显示录入对话框并返回结果
        
        Returns:
            录入的快捷键，删除返回空字符串，取消返回 None
        """
        dialog = KeyInputDialog(
            parent, mode, current_hotkey, mode_text,
            prompt_text, delete_text, cancel_text
        )
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            return dialog.get_hotkey()
        return None
