# -*- coding: utf-8 -*-
"""
热键设置对话框界面模块
仅包含界面布局和样式，不包含业务逻辑
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QWidget, QTableWidget,
    QPushButton, QLineEdit, QDialogButtonBox,
    QSizePolicy, QFrame, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QIcon, QPixmap
from utils.resource_path import get_bundled_resource_path


class HotkeyDialog(QDialog):
    """热键设置主对话框"""
    
    hotkey_edit_clicked = Signal(int)
    
    RIGHT_PANEL_WIDTH = 140
    LEFT_BUTTON_PANEL_WIDTH = 140
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._load_stylesheet()
    
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
        
        icon_path = get_bundled_resource_path("icon/icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def _create_widgets(self):
        """创建所有控件"""
        self.label_category = QLabel("类别：")
        self.label_category.setObjectName("labelCategory")
        
        self.combo_category = QComboBox()
        self.combo_category.setObjectName("comboCategory")
        self.combo_category.addItem("菜单")
        self.combo_category.setMinimumWidth(100)
        
        self.hotkey_table = QTableWidget()
        self.hotkey_table.setObjectName("hotkeyTable")
        self._setup_hotkey_table()
        
        self._selected_row = -1
        self.hotkey_rows = {}
        self._separator_rows = set()
        self.warning_icon_path = get_bundled_resource_path("icon/warning.png")
        
        self.btn_edit_hotkey = QPushButton("修改快捷键")
        self.btn_edit_hotkey.setObjectName("btnEditHotkey")
        
        self.btn_add_hotkey = QPushButton("添加快捷键")
        self.btn_add_hotkey.setObjectName("btnAddHotkey")
        
        self.btn_delete_hotkey = QPushButton("删除快捷键")
        self.btn_delete_hotkey.setObjectName("btnDeleteHotkey")
        
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
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("确认")
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setText("保存")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
    
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
    
    def add_hotkey_row(self, name: str, hotkey: str = "", show_warning: bool = False):
        """添加一行快捷键"""
        row = self.hotkey_table.rowCount()
        self.hotkey_table.insertRow(row)
        
        name_label = QLabel(name)
        name_label.setMinimumWidth(200)
        name_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        name_label.setContentsMargins(10, 0, 4, 0)
        name_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hotkey_table.setCellWidget(row, 0, name_label)
        
        warning_container = QWidget()
        warning_container.setAttribute(Qt.WA_TransparentForMouseEvents)
        warning_layout = QHBoxLayout(warning_container)
        warning_layout.setContentsMargins(0, 0, 0, 0)
        warning_layout.setSpacing(0)
        warning_layout.setAlignment(Qt.AlignCenter)
        
        warning_label = QLabel()
        warning_label.setFixedSize(24, 24)
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        if show_warning and os.path.exists(self.warning_icon_path):
            pixmap = QPixmap(self.warning_icon_path).scaled(
                24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            warning_label.setPixmap(pixmap)
        warning_layout.addWidget(warning_label)
        self.hotkey_table.setCellWidget(row, 1, warning_container)
        
        hotkey_edit = QLineEdit(hotkey)
        hotkey_edit.setReadOnly(True)
        hotkey_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hotkey_edit.setFixedWidth(280)
        hotkey_edit.setContentsMargins(0, 0, 0, 0)
        hotkey_edit.installEventFilter(self)
        hotkey_edit.setProperty("row", row)
        self.hotkey_table.setCellWidget(row, 2, hotkey_edit)
        
        self.hotkey_rows[row] = (name_label, warning_label, hotkey_edit)
    
    def _setup_layout(self):
        """设置布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        upper_layout = QHBoxLayout()
        upper_layout.setSpacing(10)
        
        self.group_hotkey_list = QGroupBox("快捷键列表")
        self.group_hotkey_list.setObjectName("groupHotkeyList")
        group_layout = QVBoxLayout(self.group_hotkey_list)
        group_layout.setContentsMargins(10, 15, 10, 10)
        group_layout.setSpacing(8)
        
        category_layout = QHBoxLayout()
        category_layout.addWidget(self.label_category)
        category_layout.addWidget(self.combo_category)
        category_layout.addStretch()
        group_layout.addLayout(category_layout)
        
        body_layout = QHBoxLayout()
        body_layout.setSpacing(10)
        body_layout.addWidget(self.hotkey_table, 4)
        
        left_btn_layout = QVBoxLayout()
        left_btn_layout.setSpacing(8)
        left_btn_layout.addWidget(self.btn_edit_hotkey)
        left_btn_layout.addWidget(self.btn_add_hotkey)
        left_btn_layout.addWidget(self.btn_delete_hotkey)
        left_btn_layout.addWidget(self.btn_quote_mode)
        left_btn_layout.addStretch()
        
        left_btn_widget = QWidget()
        left_btn_widget.setLayout(left_btn_layout)
        left_btn_widget.setFixedWidth(self.LEFT_BUTTON_PANEL_WIDTH)
        body_layout.addWidget(left_btn_widget)
        
        group_layout.addLayout(body_layout, 1)
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
        right_widget.setFixedWidth(self.RIGHT_PANEL_WIDTH)
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
    
    def _load_stylesheet(self):
        """加载样式表"""
        from utils.resource_path import get_bundled_resource_path
        
        style_path = get_bundled_resource_path("styles/style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
            
            icon_dir = get_bundled_resource_path("icon")
            icon_dir = icon_dir.replace(os.sep, '/')
            stylesheet = stylesheet.replace('./icon/', f'{icon_dir}/')
            
            self.setStyleSheet(stylesheet)
    
    def set_status_text(self, text: str):
        """设置状态栏文本"""
        self.label_status.setText(text)
    
    def clear_hotkey_list(self):
        """清空快捷键列表"""
        self.hotkey_table.setRowCount(0)
        self.hotkey_rows.clear()
        self._separator_rows.clear()
    
    def set_row_warning(self, row: int, show_warning: bool):
        """设置指定行的警告图标"""
        if row in self.hotkey_rows:
            warning_label = self.hotkey_rows[row][1]
            if show_warning and os.path.exists(self.warning_icon_path):
                pixmap = QPixmap(self.warning_icon_path).scaled(
                    20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                warning_label.setPixmap(pixmap)
            else:
                warning_label.clear()
    
    def eventFilter(self, obj, event):
        """事件过滤器：处理QLineEdit的点击事件"""
        if event.type() == QEvent.MouseButtonPress:
            if isinstance(obj, QLineEdit) and obj.property("row") is not None:
                row = obj.property("row")
                self.hotkey_table.selectRow(row)
                self._selected_row = row
                self.hotkey_edit_clicked.emit(row)
                return True
        return super().eventFilter(obj, event)
    
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
        from PySide6.QtWidgets import QTableWidgetItem
        
        row = self.hotkey_table.rowCount()
        self.hotkey_table.insertRow(row)
        
        for col in range(3):
            item = QTableWidgetItem()
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)
            self.hotkey_table.setItem(row, col, item)
        
        self.hotkey_table.setRowHeight(row, 1)
        self._separator_rows.add(row)
    
    def get_row_hotkey(self, row: int) -> str:
        """获取指定行的快捷键"""
        if row in self.hotkey_rows:
            hotkey_edit = self.hotkey_rows[row][2]
            return hotkey_edit.text()
        return ""
    
    def set_row_hotkey(self, row: int, hotkey: str):
        """设置指定行的快捷键"""
        if row in self.hotkey_rows:
            hotkey_edit = self.hotkey_rows[row][2]
            hotkey_edit.setText(hotkey)

