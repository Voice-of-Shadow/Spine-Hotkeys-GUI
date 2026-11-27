# -*- coding: utf-8 -*-
"""
热键设置对话框界面模块
仅包含界面布局和样式，不包含业务逻辑
"""

import sys

from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QComboBox, QWidget, QTableWidget,
    QPushButton, QLineEdit, QDialogButtonBox,
    QSizePolicy, QFrame, QHeaderView, QAbstractItemView, QTableWidgetItem,
    QStyledItemDelegate, QStyle
)
from PySide6.QtCore import QEvent, Qt, QSize, QLineF, QRectF, QTimer, Signal
from PySide6.QtGui import QIcon, QKeySequence, QPainter, QPalette, QPen, QPixmap, QShortcut
from utils.resource_path import get_bundled_resource_path
from .theme import ThemedDialog

if sys.platform == "win32":
    from ctypes import windll
    from ctypes.wintypes import HWND, MSG


class ShortcutDelegate(QStyledItemDelegate):
    """在可见的快捷键单元格内绘制输入框。"""

    def __init__(self, table):
        super().__init__(table)
        self._field = QLineEdit()
        self._field.setReadOnly(True)

    def paint(self, painter, option, index):
        if not index.flags() & Qt.ItemFlag.ItemIsEnabled:
            super().paint(painter, option, index)
            return

        palette = option.palette
        selected = option.state & QStyle.StateFlag.State_Selected
        painter.fillRect(option.rect, palette.highlight() if selected else palette.base())
        rect = option.rect.adjusted(1, 4, -9, -4)
        # 在独立画布上绘制 Qt 输入框，避免滚动时 QWidget.render 改动表格 painter 的偏移。
        scale = painter.device().devicePixelRatioF()
        pixels = QPixmap(rect.size() * scale)
        pixels.setDevicePixelRatio(scale)
        pixels.fill(Qt.transparent)
        self._field.resize(rect.size())
        self._field.setFont(option.font)
        self._field.setText(index.data() or "")
        self._field.setCursorPosition(0)
        self._field.render(pixels)
        painter.drawPixmap(rect, pixels)


class HotkeyDialog(ThemedDialog):
    """热键设置主对话框"""
    
    hotkey_edit_clicked = Signal(int)
    CAPTURE_SEARCH_KEY = QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_F)
    _CAPTURE_SEARCH_HOTKEY_ID = 0x4653
    
    RIGHT_PANEL_WIDTH = 140
    LEFT_BUTTON_PANEL_WIDTH = 140
    
    def __init__(self, parent=None):
        self._capture_hotkey_window = None
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        self._setup_window()
        self._create_widgets()
        self._setup_layout()
    
    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("快捷键设置")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        
    def _create_widgets(self):
        """创建所有控件"""
        self.label_category = QLabel("类别：")
        self.label_category.setObjectName("labelCategory")
        
        self.combo_category = QComboBox()
        self.combo_category.setObjectName("comboCategory")
        self.combo_category.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.combo_category.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.combo_category.setMinimumWidth(100)

        self.btn_capture_search = QPushButton()
        self.btn_capture_search.setObjectName("btnCaptureSearch")
        self.btn_capture_search.setAutoDefault(False)
        self.btn_capture_search.setFixedWidth(32)
        self.btn_capture_search.setIconSize(QSize(18, 18))
        self._update_capture_icon(QApplication.palette())
        QApplication.instance().paletteChanged.connect(self._update_capture_icon)

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("searchHotkeys")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setMinimumWidth(140)
        self.search_edit.setMaximumWidth(216)
        self.find_shortcut = QShortcut(QKeySequence.StandardKey.Find, self)
        self.find_shortcut.activated.connect(self._focus_search)
        
        self.hotkey_table = QTableWidget()
        self.hotkey_table.setObjectName("hotkeyTable")
        self._setup_hotkey_table()
        
        self._selected_row = -1
        self.hotkey_rows = {}
        self._separator_rows = set()
        self.warning_icon = QIcon(get_bundled_resource_path("icon/warning.png"))
        
        self.btn_edit_hotkey = QPushButton("修改快捷键")
        self.btn_edit_hotkey.setObjectName("btnEditHotkey")
        
        self.btn_add_hotkey = QPushButton("添加快捷键")
        self.btn_add_hotkey.setObjectName("btnAddHotkey")
        
        self.btn_delete_hotkey = QPushButton("删除快捷键")
        self.btn_delete_hotkey.setObjectName("btnDeleteHotkey")

        self.btn_undo_hotkey = QPushButton("撤回上一步")
        self.btn_undo_hotkey.setObjectName("btnUndoHotkey")
        self.undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        self.undo_shortcut.setAutoRepeat(False)
        self.undo_shortcut.activated.connect(self.btn_undo_hotkey.click)
        
        self.btn_quote_mode = QPushButton("单引号模式")
        self.btn_quote_mode.setObjectName("btnQuoteMode")
        
        self.btn_link = QPushButton("链接")
        self.btn_link.setObjectName("btnLink")
        
        self.btn_open_folder = QPushButton("打开文件夹")
        self.btn_open_folder.setObjectName("btnOpenFolder")
        
        self.label_language = QLabel("语言：")
        self.label_language.setObjectName("labelLanguage")
        
        self.combo_language = QComboBox()
        self.combo_language.setObjectName("comboLanguage")
        self.combo_language.addItems(["中文", "English"])

        self.btn_theme = QPushButton()
        self.btn_theme.setObjectName("btnTheme")
        
        self.btn_help = QPushButton("使用说明")
        self.btn_help.setObjectName("btnHelp")
        
        self.btn_hotkey_doc = QPushButton("快捷键说明")
        self.btn_hotkey_doc.setObjectName("btnHotkeyDoc")
        
        self.btn_key_mapping = QPushButton("关键字字符对应")
        self.btn_key_mapping.setObjectName("btnKeyMapping")
        
        self.btn_about = QPushButton("程序信息")
        self.btn_about.setObjectName("btnAbout")
        
        self.label_status = QLabel("  请选择想设置快捷方式的操作")
        self.label_status.setObjectName("statusLabel")
        
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.setObjectName("dialogButtonBox")
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setObjectName("btnOk")
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setObjectName("btnSave")
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("确认")
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setText("保存")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
    
    def _update_capture_icon(self, palette):
        icon = QIcon()
        size = self.btn_capture_search.iconSize().width()
        for mode, group in ((QIcon.Normal, QPalette.Active), (QIcon.Disabled, QPalette.Disabled)):
            ink = palette.color(group, QPalette.ButtonText)
            for scale in (1, 2):
                pixmap = QPixmap(size * scale, size * scale)
                pixmap.fill(Qt.transparent)
                pixmap.setDevicePixelRatio(scale)
                with QPainter(pixmap) as painter:
                    painter.scale(size / 20, size / 20)
                    painter.setRenderHint(QPainter.Antialiasing)
                    painter.setPen(QPen(ink, 1.8, Qt.SolidLine, Qt.RoundCap))
                    painter.drawEllipse(QRectF(2.5, 2.5, 11, 11))
                    painter.drawLine(QLineF(12, 12, 17.5, 17.5))
                icon.addPixmap(pixmap, mode)
        self.btn_capture_search.setIcon(icon)

    def _setup_hotkey_table(self):
        """配置快捷键表格"""
        table = self.hotkey_table
        table.setColumnCount(3)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.ClickFocus)
        table.setIconSize(QSize(24, 24))
        table.setItemDelegateForColumn(2, ShortcutDelegate(table))
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        
        table.setColumnWidth(1, 36)
        table.setColumnWidth(2, 290)
        table.setColumnWidth(0, 200)
        table.verticalHeader().setDefaultSectionSize(36)
        table.verticalHeader().setMinimumSectionSize(0)
        table.itemSelectionChanged.connect(self._on_selection_changed)
        table.cellClicked.connect(self._on_cell_clicked)
    
    def _add_sample_hotkeys(self):
        """添加示例快捷键数据（用于布局展示）"""
        sample_data = [
            ("复原", "Ctrl+Z", False),
            ("重做", "Ctrl+Y", False),
            ("", "Ctrl + Shift + alt + NUMPAD_RIGHT_PAREN", True),
            ("剪切", "Ctrl+X", False),
            ("复制", "Ctrl+C", False),
            ("粘贴", "Ctrl+V", False),
            ("删除", "Delete", False),
            ("复制参数值", "", False),
            ("粘贴参数值", "", True),
            ("解除选择", "Escape", False),
            ("取消选择被隐藏和被锁定的对象", "", False),
            ("Tree Filter - Text Search Filters", "", False),
        ]
        
        for name, hotkey, has_warning in sample_data:
            self.add_hotkey_row(name, hotkey, has_warning)
    
    def _needs_tooltip(self, text: str, column: int) -> bool:
        """只在文字被单元格截断时才显示 tooltip，避免普通悬浮也弹出小窗。"""
        if not text:
            return False
        available = max(0, self.hotkey_table.columnWidth(column) - 24)
        return self.fontMetrics().horizontalAdvance(text) > available

    def add_hotkey_row(self, name: str, hotkey: str = "", show_warning: bool = False):
        """添加一行快捷键"""
        row = self.hotkey_table.rowCount()
        self.hotkey_table.insertRow(row)
        
        name_item = QTableWidgetItem(name)
        if self._needs_tooltip(name, 0):
            name_item.setToolTip(name)
        warning_item = QTableWidgetItem()
        if show_warning:
            warning_item.setIcon(self.warning_icon)
        shortcut_item = QTableWidgetItem(hotkey)
        if self._needs_tooltip(hotkey, 2):
            shortcut_item.setToolTip(hotkey)
        self.hotkey_rows[row] = (name_item, warning_item, shortcut_item)
        for column, item in enumerate(self.hotkey_rows[row]):
            self.hotkey_table.setItem(row, column, item)
    
    def _setup_layout(self):
        """设置布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        upper_layout = QHBoxLayout()
        upper_layout.setSpacing(10)
        
        self.group_hotkey_list = QGroupBox("快捷键列表")
        self.group_hotkey_list.setObjectName("groupHotkeyList")
        group_layout = QGridLayout(self.group_hotkey_list)
        group_layout.setContentsMargins(10, 15, 10, 10)
        group_layout.setHorizontalSpacing(10)
        group_layout.setVerticalSpacing(8)
        group_layout.setColumnStretch(0, 1)
        group_layout.setRowStretch(1, 1)
        
        category_layout = QHBoxLayout()
        category_layout.setSpacing(4)
        category_layout.addWidget(self.label_category)
        category_layout.addWidget(self.combo_category)
        category_layout.addStretch(1)
        category_layout.addWidget(self.btn_capture_search)
        category_layout.addWidget(self.search_edit, 8)
        group_layout.addLayout(category_layout, 0, 0)
        group_layout.addWidget(self.hotkey_table, 1, 0)
        
        left_btn_layout = QVBoxLayout()
        left_btn_layout.setSpacing(8)
        left_btn_layout.addWidget(self.btn_edit_hotkey)
        left_btn_layout.addWidget(self.btn_add_hotkey)
        left_btn_layout.addWidget(self.btn_delete_hotkey)
        left_btn_layout.addWidget(self.btn_undo_hotkey)
        left_btn_layout.addWidget(self.btn_quote_mode)
        left_btn_layout.addStretch()
        
        left_btn_widget = QWidget()
        left_btn_widget.setLayout(left_btn_layout)
        left_btn_widget.setFixedWidth(self.LEFT_BUTTON_PANEL_WIDTH)
        group_layout.addWidget(left_btn_widget, 1, 1)
        upper_layout.addWidget(self.group_hotkey_list, 5)
        
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)
        
        top_buttons_layout = QVBoxLayout()
        top_buttons_layout.setSpacing(8)
        top_buttons_layout.addWidget(self.btn_link)
        top_buttons_layout.addWidget(self.btn_open_folder)
        right_panel.addLayout(top_buttons_layout)
        right_panel.addStretch(1)
        
        center_layout = QVBoxLayout()
        center_layout.setSpacing(8)
        center_layout.addWidget(self.label_language)
        center_layout.addWidget(self.combo_language)
        center_layout.addWidget(self.btn_theme)
        right_panel.addLayout(center_layout)
        right_panel.addStretch(1)
        
        bottom_buttons_layout = QVBoxLayout()
        bottom_buttons_layout.setSpacing(8)
        bottom_buttons_layout.addWidget(self.btn_help)
        bottom_buttons_layout.addWidget(self.btn_hotkey_doc)
        bottom_buttons_layout.addWidget(self.btn_key_mapping)
        bottom_buttons_layout.addWidget(self.btn_about)
        right_panel.addLayout(bottom_buttons_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setMinimumWidth(self.RIGHT_PANEL_WIDTH)
        upper_layout.addWidget(right_widget)
        main_layout.addLayout(upper_layout, 4)
        
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(0, 5, 0, 5)
        status_layout.addWidget(self.label_status)
        status_layout.addStretch()
        main_layout.addWidget(status_frame, 1)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.button_box, 0, Qt.AlignCenter)
        button_layout.addStretch(1)
        button_layout.setContentsMargins(0, 5, 0, 5)
        main_layout.addLayout(button_layout)
    
    def set_status_text(self, text: str):
        """设置状态栏文本"""
        self.label_status.setText(text)
    
    def clear_hotkey_list(self):
        """清空快捷键列表"""
        self.hotkey_table.clearSpans()
        self.hotkey_table.setRowCount(0)
        self._selected_row = -1
        self.hotkey_rows.clear()
        self._separator_rows.clear()
    
    def set_row_warning(self, row: int, show_warning: bool):
        """设置指定行的警告图标"""
        if row in self.hotkey_rows:
            warning_item = self.hotkey_rows[row][1]
            warning_item.setIcon(self.warning_icon if show_warning else QIcon())

    def _on_cell_clicked(self, row: int, column: int):
        if column == 2 and row in self.hotkey_rows:
            if self.get_selected_row() != row:
                self.hotkey_table.selectRow(row)
            self.hotkey_edit_clicked.emit(row)
    
    def _on_selection_changed(self):
        """处理选择变化事件"""
        selected_rows = self.hotkey_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row in self._separator_rows:
                self.hotkey_table.clearSelection()
                self._selected_row = -1
            else:
                self._selected_row = row
        else:
            self._selected_row = -1
    
    def get_selected_row(self) -> int:
        """获取当前选中的行索引，未选中返回-1"""
        return self._selected_row
    
    def clear_selection(self):
        """清除选中状态"""
        self.hotkey_table.clearSelection()
        self._selected_row = -1
    
    def set_button_active(self, button: QPushButton, active: bool):
        """设置按钮激活状态"""
        button.setProperty("active", active)
        button.style().unpolish(button)
        button.style().polish(button)
    
    def add_separator_row(self):
        """添加分割线行"""
        row = self.hotkey_table.rowCount()
        self.hotkey_table.insertRow(row)
        
        for col in range(3):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.hotkey_table.setItem(row, col, item)
        
        self.hotkey_table.setRowHeight(row, 1)
        self._separator_rows.add(row)

    def add_category_heading(self, name: str):
        """为跨类别的搜索结果添加不可选的分组标题。"""
        table = self.hotkey_table
        row = table.rowCount()
        table.insertRow(row)
        heading = QTableWidgetItem(name)
        heading.setFlags(Qt.ItemFlag.ItemIsEnabled)
        font = heading.font()
        font.setBold(True)
        heading.setFont(font)
        table.setItem(row, 0, heading)
        table.setSpan(row, 0, 1, table.columnCount())
        self._separator_rows.add(row)

    def _focus_search(self):
        self.search_edit.setFocus()
        self.search_edit.selectAll()

    def eventFilter(self, watched, event):
        event_type = event.type()
        if (
            event_type in (QEvent.Type.ShortcutOverride, QEvent.Type.KeyPress)
            and self.btn_capture_search.isEnabled()
            and isinstance(watched, QWidget)
            and watched.window() is self
            and QApplication.activeModalWidget() is None
            and event.keyCombination() == self.CAPTURE_SEARCH_KEY[0]
        ):
            # 在焦点控件处理按键前拦截，避免其抢先接受组合键。
            event.accept()
            if event_type == QEvent.Type.KeyPress and not event.isAutoRepeat():
                self.btn_capture_search.click()
            return True
        return super().eventFilter(watched, event)

    def set_capture_search_enabled(self, enabled):
        self.btn_capture_search.setEnabled(enabled)
        self._set_windows_capture_hotkey(enabled and self.isActiveWindow())

    def _set_windows_capture_hotkey(self, active):
        if sys.platform != "win32" or QApplication.platformName() != "windows":
            return
        # 仅在主窗口前台时注册，优先于微软拼音的简繁切换；离开编辑器后归还组合键。
        handle = self.internalWinId() if active else None
        registered = self._capture_hotkey_window
        if registered == handle:
            return
        if registered:
            windll.user32.UnregisterHotKey(HWND(registered), self._CAPTURE_SEARCH_HOTKEY_ID)
            self._capture_hotkey_window = None
        if handle:
            modifiers = 0x0002 | 0x0004 | 0x4000  # MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT
            if windll.user32.RegisterHotKey(HWND(handle), self._CAPTURE_SEARCH_HOTKEY_ID, modifiers, 0x46):
                self._capture_hotkey_window = handle

    def nativeEvent(self, event_type, message):
        if sys.platform == "win32" and event_type == b"windows_generic_MSG":
            msg = MSG.from_address(int(message))
            if msg.message == 0x0312 and msg.wParam == self._CAPTURE_SEARCH_HOTKEY_ID:  # WM_HOTKEY
                QTimer.singleShot(0, self, self._activate_capture_search)
                return True, 0
        return super().nativeEvent(event_type, message)

    def _activate_capture_search(self):
        if self.isActiveWindow() and QApplication.activeModalWidget() is None:
            self.btn_capture_search.click()

    def event(self, event):
        result = super().event(event)
        if event.type() == QEvent.Type.WindowDeactivate:
            self._set_windows_capture_hotkey(False)
        elif event.type() == QEvent.Type.WindowActivate:
            self._set_windows_capture_hotkey(self.btn_capture_search.isEnabled())
        return result

    def showEvent(self, event):
        QApplication.instance().installEventFilter(self)
        super().showEvent(event)

    def hideEvent(self, event):
        self._set_windows_capture_hotkey(False)
        QApplication.instance().removeEventFilter(self)
        super().hideEvent(event)

    def keyPressEvent(self, event):
        if self.search_edit.hasFocus():
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                event.accept()
                return
            if event.key() == Qt.Key_Escape and self.search_edit.text():
                self.search_edit.clear()
                event.accept()
                return
        super().keyPressEvent(event)
    
    def get_row_hotkey(self, row: int) -> str:
        """获取指定行的快捷键"""
        if row in self.hotkey_rows:
            return self.hotkey_rows[row][2].text()
        return ""
    
    def set_row_hotkey(self, row: int, hotkey: str):
        """设置指定行的快捷键"""
        if row in self.hotkey_rows:
            shortcut_item = self.hotkey_rows[row][2]
            shortcut_item.setText(hotkey)
            shortcut_item.setToolTip(hotkey if self._needs_tooltip(hotkey, 2) else "")

