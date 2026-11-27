# -*- coding: utf-8 -*-
"""
Spine 热键设置 GUI 程序入口
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, QEvent, Qt
from PySide6.QtGui import QIcon
from ui import HotkeyDialog
from core.controller import Controller
from utils.resource_path import get_bundled_resource_path


def main():
    """程序主入口"""
    if sys.platform == "win32":
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("VoiceOfShadow.SpineHotkeysEditor")

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Spine Hotkey GUI")
    app.setWindowIcon(QIcon(get_bundled_resource_path("icon/icon (00000).ico")))
    
    dialog = HotkeyDialog()
    controller = Controller(dialog)
    controller.initialize()
    dialog.show()
    
    exit_code = app.exec()
    # 让 Qt 在 Python 回调和绘制委托仍然有效时销毁窗口及其子控件。
    dialog.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.shutdown()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
