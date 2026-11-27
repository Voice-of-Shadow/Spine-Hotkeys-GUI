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
from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QKeyEvent

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.keyboard_handler import KeyboardHandler
from .theme import ThemedDialog


class InfoDialog(ThemedDialog):
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
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        if is_about:
            self.content_browser = QTextBrowser()
            self.content_browser.setObjectName("aboutContent")
            self.content_browser.setOpenExternalLinks(True)
            self.content_browser.setReadOnly(True)
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


class AlertDialog(ThemedDialog):
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
        
    @staticmethod
    def show_alert(parent: Optional[QWidget], title: str, content: str,
                   button_text: str = "确认") -> None:
        """
        静态方法：显示单按钮提示对话框
        """
        dialog = AlertDialog(parent, title, content, button_text)
        dialog.exec()


class ConfirmDialog(ThemedDialog):
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


class KeyInputDialog(ThemedDialog):
    """
    录入提示窗 (C)
    用于快捷键录入，监听键盘输入
    """
    
    hotkey_captured = Signal(str)
    
    def __init__(self, parent: Optional[QWidget], mode: str = 'normal',
                 current_hotkey: str = "", mode_text: str = "一般模式",
                 prompt_text: str = "请从键盘按下要设置的快捷键",
                 delete_text: str = "删除快捷键", cancel_text: str = "取消",
                 *, search_only: bool = False):
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
        self._search_only = search_only
        self.current_hotkey = current_hotkey
        self._captured_hotkey: Optional[str] = None
        self._deleted = False
        self.keyboard_handler = KeyboardHandler(mode)
        
        self.setWindowTitle(mode_text)
        self.setFixedSize(400, 160)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.label_prompt = QLabel(prompt_text)
        self.label_prompt.setObjectName("promptLabel")
        self.label_prompt.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_prompt, 4)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 设置可见性前先指定父窗口，避免按钮被显示成独立窗口。
        self.btn_delete = QPushButton(delete_text, self)
        self.btn_delete.setObjectName("btnCancel")
        self.btn_delete.setEnabled(bool(current_hotkey))
        self.btn_delete.setHidden(search_only)
        self.btn_delete.clicked.connect(self._on_delete)
        button_layout.addWidget(self.btn_delete)
        
        self.btn_cancel = QPushButton(cancel_text)
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        button_layout.addStretch()
        layout.addLayout(button_layout, 1)
        
        self.setFocusPolicy(Qt.StrongFocus)
        if search_only:
            self.btn_cancel.setAutoDefault(False)
            self.btn_cancel.setFocusPolicy(Qt.NoFocus)
            self.setFocus()

    def event(self, event):
        # 录入搜索时也要捕获 Tab、回车和空格，它们通常会被 Qt 用于导航或激活按钮。
        if event.type() == QEvent.Type.KeyPress and self._search_only:
            if not event.isAutoRepeat():
                self.keyPressEvent(event)
            event.accept()
            return True
        return super().event(event)
    
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
                cancel_text: str = "取消", *, search_only: bool = False) -> Optional[str]:
        """
        静态方法：显示录入对话框并返回结果
        
        Returns:
            录入的快捷键，删除返回空字符串，取消返回 None
        """
        dialog = KeyInputDialog(
            parent, mode, current_hotkey, mode_text,
            prompt_text, delete_text, cancel_text, search_only=search_only
        )
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            return dialog.get_hotkey()
        return None
