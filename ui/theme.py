"""应用主窗口、弹窗共享的主题和 Qt 调色板。"""

from pathlib import Path
import sys

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QColor, QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication, QDialog, QStyle, QToolTip

from utils.resource_path import get_bundled_resource_path


class ThemedDialog(QDialog):
    """将 Windows 原生标题栏与应用主题同步。"""

    def exec(self) -> int:
        # 显示前先确定位置。winId() 会提前创建原生窗口，窗口有可能先以
        # 默认位置（通常是父窗口/屏幕左上角）出现再被移动；move() 只记录
        # 几何和 WA_Moved 标记，原生窗口会在 exec() 时直接以最终位置创建。
        QToolTip.hideText()
        self.center_over_parent()
        return super().exec()

    def center_over_parent(self) -> None:
        """把对话框放到父窗口中央，并限制在父窗口所在屏幕的可用区域内。"""
        parent = self.parentWidget()
        if parent is None:
            return

        # 让样式表与布局先生效，避免显示时窗口再改变大小导致位置偏移。
        self.ensurePolished()
        if self.layout() is not None:
            self.layout().activate()
        target_size = self.size().expandedTo(
            self.minimumSizeHint().expandedTo(self.minimumSize()))
        if target_size != self.size():
            self.resize(target_size)

        frame = self.frameGeometry()
        offset = frame.topLeft() - self.pos()
        width, height = frame.width(), frame.height()
        if width <= self.width() and height <= self.height():
            # 原生窗口尚未创建时 frameGeometry() 不含标题栏，按样式补偿。
            title_bar = 0
            if QApplication.platformName() == "windows":
                title_bar = self.style().pixelMetric(QStyle.PixelMetric.PM_TitleBarHeight)
            width, height = self.width(), self.height() + title_bar
            offset = QPoint(0, 0)

        window = parent.window()
        parent_frame = window.frameGeometry()
        # 用父窗口中心所在的屏幕，避免 QWidget.screen() 跨屏移动后仍返回旧屏幕。
        screen = QGuiApplication.screenAt(parent_frame.center()) or window.screen()
        available = screen.availableGeometry()
        x = max(available.left(),
                min(parent_frame.center().x() - width // 2, available.right() - width + 1))
        y = max(available.top(),
                min(parent_frame.center().y() - height // 2, available.bottom() - height + 1))
        self.move(x - offset.x(), y - offset.y())

    def showEvent(self, event):
        # QShowEvent 在窗口真正显示前送达；对非 exec() 打开的弹窗也完成定位，
        # 之后 Qt 的 QDialog::showEvent 会因 WA_Moved 而跳过再次居中。
        if not self.testAttribute(Qt.WA_Moved):
            self.center_over_parent()
        super().showEvent(event)

    def event(self, event):
        result = super().event(event)
        if sys.platform == "win32" and event.type() in (QEvent.Show, QEvent.WinIdChange):
            self.update_title_bar()
        return result

    def update_title_bar(self, refresh=False):
        # internalWinId() 只读取现有句柄，在窗口销毁期间不会重新创建它。
        handle = self.internalWinId()
        if not handle or QApplication.platformName() != "windows":
            return
        from ctypes import byref, sizeof, windll
        from ctypes.wintypes import BOOL, DWORD, HWND

        hwnd = HWND(handle)
        try:
            set_attr = windll.dwmapi.DwmSetWindowAttribute
        except (AttributeError, OSError):
            return
        dark = bool(QApplication.instance().property("darkTitleBar"))
        enabled = BOOL(dark)
        if set_attr(hwnd, 20, byref(enabled), sizeof(enabled)) != 0:  # DWMWA_USE_IMMERSIVE_DARK_MODE
            if set_attr(hwnd, 19, byref(enabled), sizeof(enabled)) != 0:  # 较早的 Windows 10
                return
        if sys.getwindowsversion().build >= 22000:
            # Windows 11 支持独立指定标题栏和文字色。浅色时恢复 DWM 默认值。
            for attr, role in ((35, QPalette.Window), (36, QPalette.WindowText)):
                color = QApplication.palette().color(role)
                rgb = color.red() | color.green() << 8 | color.blue() << 16
                value = DWORD(rgb if dark else 0xFFFFFFFF)
                set_attr(hwnd, attr, byref(value), sizeof(value))
        elif refresh and self.isVisible():
            # Windows 10 缓存标题栏，需重绘非客户区的激活状态。保留窗口原有焦点。
            active = self.isActiveWindow()
            wm_ncactivate = 0x0086
            windll.user32.SendMessageW(hwnd, wm_ncactivate, int(not active), 0)
            windll.user32.SendMessageW(hwnd, wm_ncactivate, int(active), 0)


def apply_theme(theme: str) -> None:
    app = QApplication.instance()
    dark = theme == "dark"
    theme_changed = app.property("darkTitleBar") != dark
    app.setProperty("darkTitleBar", dark)
    app.styleHints().setColorScheme(Qt.ColorScheme.Dark if dark else Qt.ColorScheme.Light)

    palette = QPalette()
    role = QPalette.ColorRole
    colors = {
        role.Window: ("#f2f2f2", "#252526"),
        role.Base: ("#ffffff", "#1e1e1e"),
        role.Button: ("#ffffff", "#333337"),
        role.Light: ("#f8f8f8", "#3e3e42"),
        role.Midlight: ("#e6e6e6", "#454549"),
        role.Mid: ("#cccccc", "#515155"),
        role.Dark: ("#c3c3c3", "#626267"),
        role.Shadow: ("#a9a9a9", "#808086"),
        role.WindowText: ("#171717", "#e1e1e3"),
        role.Text: ("#171717", "#e1e1e3"),
        role.ButtonText: ("#171717", "#e1e1e3"),
        role.PlaceholderText: ("#646464", "#a5a5aa"),
        role.Highlight: ("#c9e4fb", "#264f78"),
        role.HighlightedText: ("#101010", "#ffffff"),
        role.Accent: ("#3977b7", "#75baf4"),
        role.Link: ("#2464a4", "#80bfff"),
        role.ToolTipBase: ("#ffffff", "#333337"),
        role.ToolTipText: ("#171717", "#e1e1e3"),
    }
    for color_role, (light_color, dark_color) in colors.items():
        palette.setColor(color_role, QColor(dark_color if dark else light_color))
    disabled_text = QColor("#99999e" if dark else "#757575")
    for color_role in (role.WindowText, role.Text, role.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, color_role, disabled_text)
    app.setPalette(palette)

    style_path = Path(get_bundled_resource_path("styles/style.qss"))
    if style_path.is_file():
        stylesheet = style_path.read_text(encoding="utf-8")
        icon_dir = Path(get_bundled_resource_path("icon")).as_posix()
        app.setStyleSheet(stylesheet.replace("./icon/", f"{icon_dir}/"))

    if sys.platform == "win32":
        for window in app.topLevelWidgets():
            if isinstance(window, ThemedDialog):
                window.update_title_bar(refresh=theme_changed)
