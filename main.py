# -*- coding: utf-8 -*-
"""
Spine 热键设置 GUI 程序入口
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui import HotkeyDialog
from core.controller import Controller


def main():
    """程序主入口"""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Spine Hotkey GUI")
    
    dialog = HotkeyDialog()
    controller = Controller(dialog)
    controller.initialize()
    dialog.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
