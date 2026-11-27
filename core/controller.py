# -*- coding: utf-8 -*-
"""
主控制器模块
协调所有模块，连接 UI 和业务逻辑
"""

import os
import re
import subprocess
import sys
from typing import Dict, Optional

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QFileDialog

from .config_manager import ConfigManager
from .i18n_manager import I18nManager
from .hotkey_manager import HotkeyManager, ShortcutRow
from .conflict_detector import ConflictDetector
from .keyboard_handler import KeyboardHandler
from utils.file_converter import FileConverter
from utils.resource_path import get_external_resource_path
from ui.theme import apply_theme


class Controller:
    """主控制器"""
    
    def __init__(self, dialog):
        """
        初始化控制器
        
        Args:
            dialog: HotkeyDialog 实例
        """
        self.dialog = dialog
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.config_manager = ConfigManager(
            get_external_resource_path("config.json")
        )
        self.i18n_manager = I18nManager(
            get_external_resource_path("language")
        )
        self.hotkey_manager = HotkeyManager()
        self.conflict_detector = ConflictDetector(self.hotkey_manager)
        self.keyboard_handler = KeyboardHandler('normal')

        self.is_linked = False
        self.is_quote_mode_active = False
        self.current_mode = 'normal'
        
        self.row_data_map: Dict[int, ShortcutRow] = {}

        self.current_category = ""
        self._exact_search = False

        self._connect_signals()
    
    def _connect_signals(self):
        """连接 UI 信号到处理方法"""
        self.dialog.btn_link.clicked.connect(self.on_link_clicked)
        self.dialog.btn_open_folder.clicked.connect(self.on_open_folder)
        self.dialog.btn_edit_hotkey.clicked.connect(self.on_edit_hotkey)
        self.dialog.btn_add_hotkey.clicked.connect(self.on_add_hotkey)
        self.dialog.btn_delete_hotkey.clicked.connect(self.on_delete_hotkey)
        self.dialog.btn_undo_hotkey.clicked.connect(self.on_undo_hotkey)
        self.dialog.search_edit.textChanged.connect(self.on_search_changed)
        self.dialog.btn_capture_search.clicked.connect(self.on_capture_search)
        self.dialog.btn_quote_mode.clicked.connect(self.on_quote_mode_toggled)
        self.dialog.btn_help.clicked.connect(lambda: self.on_info_button('help'))
        self.dialog.btn_hotkey_doc.clicked.connect(lambda: self.on_info_button('hotkey_doc'))
        self.dialog.btn_key_mapping.clicked.connect(lambda: self.on_info_button('key_mapping'))
        self.dialog.btn_about.clicked.connect(lambda: self.on_info_button('about'))

        from PySide6.QtWidgets import QDialogButtonBox
        self.dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.on_save)
        self.dialog.button_box.button(QDialogButtonBox.StandardButton.Save).clicked.connect(self.on_save_only)
        self.dialog.button_box.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.on_cancel)
        
        self.dialog.combo_category.currentIndexChanged.connect(self.on_category_changed)
        self.dialog.combo_language.currentIndexChanged.connect(self.on_language_changed)
        self.dialog.btn_theme.clicked.connect(self.on_theme_toggled)
        self.dialog.hotkey_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.dialog.hotkey_edit_clicked.connect(self.on_hotkey_edit_clicked)
    
    def initialize(self):
        """执行启动初始化流程"""
        apply_theme(self.config_manager.get_theme())
        language = self.config_manager.get_primary_language()
        self.i18n_manager.load_language(language)
        
        self.update_ui_texts()
        self._populate_language_combo()
        self._update_button_states()
        self._update_window_title()
        
        link_path = self.config_manager.get_link_path()
        if link_path and os.path.exists(link_path):
            self._do_import(link_path)
        
        if not self.config_manager.get_initialized():
            self.on_info_button('about')
            self.config_manager.set_initialized(True)
        
        self.config_manager.update_system_status()
    
    def update_ui_texts(self):
        """更新所有界面文本"""
        self.dialog.group_hotkey_list.setTitle(
            self.i18n_manager.get_text("groupHotkeyList", "快捷键列表")
        )
        self.dialog.label_category.setText(
            self.i18n_manager.get_text("labelCategory", "类别：")
        )
        search_hint = self.i18n_manager.get_text("searchHotkeys", "在所有类别中搜索名称或快捷键")
        self.dialog.search_edit.setPlaceholderText(
            self.i18n_manager.get_text("searchPlaceholder", "搜索名称或快捷键")
        )
        self.dialog.search_edit.setAccessibleName(search_hint)
        self.dialog.search_edit.setToolTip(f"{search_hint} ({self.dialog.find_shortcut.key().toString()})")
        capture_label = self.i18n_manager.get_text("captureSearch", "按键搜索")
        self.dialog.btn_capture_search.setAccessibleName(capture_label)
        self.dialog.btn_capture_search.setToolTip(
            f"{capture_label} ({self.dialog.CAPTURE_SEARCH_KEY.toString()})"
        )
        self.dialog.combo_category.setPlaceholderText(
            self.i18n_manager.get_text("allCategories", "所有类别")
        )
        self.dialog.btn_undo_hotkey.setText(self.i18n_manager.get_text("btnUndoHotkey", "撤回上一步"))
        self.dialog.btn_undo_hotkey.setToolTip(self.dialog.undo_shortcut.key().toString())
        self.dialog.label_language.setText(
            self.i18n_manager.get_text("labelLanguage", "语言：")
        )
        self._update_theme_button()
        self.dialog.label_status.setText(
            self.i18n_manager.get_text("statusLabel", "  请选择想设置快捷方式的操作")
        )
        
        self.dialog.btn_edit_hotkey.setText(
            self.i18n_manager.get_text("btnEditHotkey", "修改快捷键")
        )
        self.dialog.btn_add_hotkey.setText(
            self.i18n_manager.get_text("btnAddHotkey", "添加快捷键")
        )
        self.dialog.btn_delete_hotkey.setText(
            self.i18n_manager.get_text("btnDeleteHotkey", "删除快捷键")
        )
        self.dialog.btn_quote_mode.setText(
            self.i18n_manager.get_text("btnQuoteMode", "单引号模式")
        )
        
        if self.is_linked:
            self.dialog.btn_link.setText(
                self.i18n_manager.get_text("btnLink_relink", "重链接")
            )
        else:
            self.dialog.btn_link.setText(
                self.i18n_manager.get_text("btnLink_link", "链接")
            )
        
        self.dialog.btn_open_folder.setText(
            self.i18n_manager.get_text("btnOpenFolder", "打开文件夹")
        )
        self.dialog.btn_help.setText(
            self.i18n_manager.get_text("btnHelp", "使用说明")
        )
        self.dialog.btn_hotkey_doc.setText(
            self.i18n_manager.get_text("btnHotkeyDoc", "快捷键说明")
        )
        self.dialog.btn_key_mapping.setText(
            self.i18n_manager.get_text("btnKeyMapping", "快捷键字符对应")
        )
        self.dialog.btn_about.setText(
            self.i18n_manager.get_text("btnAbout", "程序信息")
        )
        
        from PySide6.QtWidgets import QDialogButtonBox
        self.dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).setText(
            self.i18n_manager.get_text("btn_ok", "确认")
        )
        self.dialog.button_box.button(QDialogButtonBox.StandardButton.Save).setText(
            self.i18n_manager.get_text("btn_save", "保存")
        )
        self.dialog.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(
            self.i18n_manager.get_text("btn_cancel", "取消")
        )
    
    def _update_theme_button(self):
        if self.config_manager.get_theme() == "dark":
            text = self.i18n_manager.get_text("btnUseLightTheme", "切换为浅色主题")
        else:
            text = self.i18n_manager.get_text("btnUseDarkTheme", "切换为深色主题")
        self.dialog.btn_theme.setText(text)

    def on_theme_toggled(self):
        theme = "light" if self.config_manager.get_theme() == "dark" else "dark"
        self.config_manager.set_theme(theme)
        apply_theme(theme)
        self._update_theme_button()

    def _populate_language_combo(self):
        """填充语言下拉列表"""
        self.dialog.combo_language.blockSignals(True)
        self.dialog.combo_language.clear()
        
        available = self.config_manager.get_available_languages()
        current = self.config_manager.get_primary_language()
        current_index = 0
        
        for i, lang_code in enumerate(available):
            display_name = self.config_manager.get_language_display_name(lang_code)
            self.dialog.combo_language.addItem(display_name, lang_code)
            if lang_code == current:
                current_index = i
        
        self.dialog.combo_language.setCurrentIndex(current_index)
        self.dialog.combo_language.blockSignals(False)
    
    def _update_window_title(self):
        """更新窗口标题"""
        base_title = self.i18n_manager.get_text("windowTitle", "Spine快捷键编辑工具")
        version = self.config_manager.get_version()
        
        if self.is_linked:
            status = self.i18n_manager.get_text("status_linked", "[已链接]")
        else:
            status = self.i18n_manager.get_text("status_unlinked", "[未链接]")
        
        self.dialog.setWindowTitle(f"{base_title} {version} {status}")
    
    def _update_button_states(self):
        """更新按钮启用/禁用状态"""
        self.dialog.btn_open_folder.setEnabled(self.is_linked)
        self.dialog.combo_category.setEnabled(self.is_linked)
        self.dialog.search_edit.setEnabled(self.is_linked)
        self.dialog.find_shortcut.setEnabled(self.is_linked)
        self.dialog.set_capture_search_enabled(self.is_linked)
        self.dialog.btn_undo_hotkey.setEnabled(self.hotkey_manager.can_undo())
        self.dialog.undo_shortcut.setEnabled(self.hotkey_manager.can_undo())
        
        selected_row = self.dialog.get_selected_row()
        has_selection = selected_row >= 0 and self.is_linked
        
        has_hotkey = False
        can_delete = False
        can_add = False
        
        if has_selection and selected_row in self.row_data_map:
            cat_id, cmd_id, idx = self.row_data_map[selected_row]
            item = self.hotkey_manager.get_item(cat_id, cmd_id)
            if item:
                shortcuts = item.get("shortcuts", [])
                total_rows = len(shortcuts)
                
                if idx < total_rows:
                    has_hotkey = bool(shortcuts[idx])
                
                has_empty_row = any(not s for s in shortcuts)
                
                if has_hotkey:
                    can_delete = True
                elif not has_hotkey and total_rows > 1:
                    can_delete = True
                
                if has_hotkey and not has_empty_row:
                    can_add = True
        
        self.dialog.btn_edit_hotkey.setEnabled(has_selection)
        self.dialog.btn_add_hotkey.setEnabled(has_selection and can_add)
        self.dialog.btn_delete_hotkey.setEnabled(has_selection and can_delete)
    
    def _update_status_label(self):
        """更新底部状态栏"""
        selected_row = self.dialog.get_selected_row()
        
        if selected_row < 0 or selected_row not in self.row_data_map:
            if self.dialog.search_edit.text().strip() and not self.row_data_map:
                self.dialog.set_status_text(self.i18n_manager.get_text("noSearchResults", "没有匹配的名称或快捷键"))
                return
            self.dialog.set_status_text(
                self.i18n_manager.get_text("statusLabel", "请选择想设置快捷方式的操作")
            )
            return
        
        cat_id, cmd_id, idx = self.row_data_map[selected_row]
        cmd_name = self.i18n_manager.get_command_name(cmd_id)
        note = self.i18n_manager.get_command_note(cmd_id)
        
        item = self.hotkey_manager.get_item(cat_id, cmd_id)
        conflict_text = ""
        if item:
            shortcuts = item.get("shortcuts", [])
            if idx < len(shortcuts) and shortcuts[idx]:
                shortcut = shortcuts[idx]
                conflicts = self.conflict_detector.get_conflicting_commands(
                    shortcut, cat_id, cmd_id
                )
                if conflicts:
                    conflict_names = [
                        self.i18n_manager.get_command_name(c[1])
                        for c in conflicts
                    ]
                    conflict_label = self.i18n_manager.get_text("statusConflict", "存在冲突：")
                    conflict_text = f"\t\t{conflict_label}{'、'.join(conflict_names)}"
        
        line1 = f"「{cmd_name}」{conflict_text}"
        line2 = note if note else ""
        
        if line2:
            status_text = f"{line1}\n  {line2}"
        else:
            status_text = line1
        
        self.dialog.set_status_text(status_text)
    
    def on_link_clicked(self):
        """处理链接按钮点击"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.dialog,
            self.i18n_manager.get_text("dialogTitle_link", "链接"),
            "",
            "Text Files (*.txt)"
        )
        
        if file_path:
            self._do_import(file_path)
    
    def _do_import(self, file_path: str):
        """执行导入流程"""
        from ui.dialogs import AlertDialog
        
        valid, error = FileConverter.validate_hotkey_file(file_path)
        if not valid:
            AlertDialog.show_alert(
                self.dialog,
                self.i18n_manager.get_text("dialogTitle_link", "链接"),
                self.i18n_manager.get_text("dialogContent_selectFile", "请链接正确的快捷键文件"),
                self.i18n_manager.get_text("btn_ok", "确认")
            )
            return
        
        try:
            from utils.resource_path import get_external_resource_path
            processing_dir = get_external_resource_path("processing")
            json_path = FileConverter.import_and_process(file_path, processing_dir)
            
            if not self.hotkey_manager.load_from_json(json_path):
                raise OSError(json_path)
            self.config_manager.set_link_path(file_path)
            self.is_linked = True
            self.current_category = ""
            self._set_search_text("")
            
            self.dialog.btn_link.setText(
                self.i18n_manager.get_text("btnLink_relink", "重链接")
            )
            self._update_window_title()
            self._populate_category_combo()
            self._render_hotkey_list()
        
        except Exception as e:
            AlertDialog.show_alert(
                self.dialog,
                self.i18n_manager.get_text("dialogTitle_formatError", "格式化错误"),
                str(e),
                self.i18n_manager.get_text("btn_ok", "确认")
            )
    
    def _populate_category_combo(self):
        """填充类别下拉列表"""
        combo = self.dialog.combo_category
        categories = self.hotkey_manager.get_categories()
        with QSignalBlocker(combo):
            combo.clear()
            for category in categories:
                combo.addItem(self.i18n_manager.get_category_name(category), category)
        if self.current_category not in categories:
            self.current_category = categories[0] if categories else ""
        self._sync_category_selection()
    
    def _sync_category_selection(self):
        combo = self.dialog.combo_category
        with QSignalBlocker(combo):
            index = combo.findData(self.current_category)
            combo.setCurrentIndex(-1 if self.dialog.search_edit.text().strip() else index)

    def on_search_changed(self):
        self._exact_search = False
        self._sync_category_selection()
        self._render_hotkey_list()

    def _set_search_text(self, text: str, *, exact: bool = False):
        with QSignalBlocker(self.dialog.search_edit):
            self.dialog.search_edit.setText(text)
        self._exact_search = exact

    def on_capture_search(self):
        from ui.dialogs import KeyInputDialog

        if not self.is_linked:
            return
        title = self.i18n_manager.get_text("captureSearch", "按键搜索")
        shortcut = KeyInputDialog.capture(
            self.dialog,
            mode=self.current_mode,
            mode_text=f"{title} · {self._input_mode_name()}",
            prompt_text=self.i18n_manager.get_text("pressSearchShortcut", "请按下要查找的快捷键"),
            cancel_text=self.i18n_manager.get_text("btn_cancel", "取消"),
            search_only=True,
        )
        if shortcut:
            self._set_search_text(shortcut, exact=True)
            self._sync_category_selection()
            self._render_hotkey_list()

    def _input_mode_name(self):
        if self.is_quote_mode_active:
            return self.i18n_manager.get_text("dialogTitle_characterMode", "单引号模式")
        return self.i18n_manager.get_text("dialogTitle_normalMode", "一般模式")

    def _visible_commands(self, category, query, key_query):
        name_query = query.casefold()
        match_literal_case = "'" in query
        for item in self.hotkey_manager.get_items_by_category(category):
            command = item["commandId"]
            name = self.i18n_manager.get_command_name(command)
            bindings = list(enumerate(item["shortcuts"]))
            name_matches = name_query in name.casefold() or name_query in command.casefold()
            if query and (self._exact_search or not name_matches):
                normalized = ((i, self._search_key(key, match_literal_case)) for i, key in bindings)
                if self._exact_search:
                    matches = {i for i, key in normalized if key == key_query}
                else:
                    matches = {i for i, key in normalized if key_query in key}
                if not matches:
                    continue
                # 保留匹配命令下新添加的空位，方便直接在搜索结果里录入。
                bindings = [(i, key) for i, key in bindings if i in matches or not key]
            yield command, name, bindings

    @staticmethod
    def _search_key(text: str, match_literal_case: bool) -> str:
        # Spine 的单引号字符区分大小写；引号内的空格和加号也可能是按键本身。
        keys, quote, literal = text.partition("'")
        keys = re.sub(r"\s*\+\s*", "+", keys.casefold())
        return keys + quote + (literal if match_literal_case else literal.casefold())

    def _render_hotkey_list(self, selection: Optional[ShortcutRow] = None):
        """按当前类别或全局搜索结果显示，编辑后的选中项通过命令和绑定索引定位。"""
        table = self.dialog.hotkey_table
        scroll = table.verticalScrollBar()
        position = scroll.value() if selection else 0
        query = self.dialog.search_edit.text().strip()
        key_query = self._search_key(query, "'" in query)
        categories = self.hotkey_manager.get_categories() if query else [self.current_category]
        self.conflict_detector.invalidate_cache()
        conflicts = self.conflict_detector.get_shortcuts_with_conflicts()
        selected_row = -1

        with QSignalBlocker(table):
            self.dialog.clear_hotkey_list()
            self.row_data_map.clear()
            for category in categories:
                commands = self._visible_commands(category, query, key_query)
                for group_index, (command, name, bindings) in enumerate(commands):
                    if group_index == 0 and query:
                        self.dialog.add_category_heading(self.i18n_manager.get_category_name(category))
                    elif group_index > 0:
                        self.dialog.add_separator_row()
                    for visible_index, (index, key) in enumerate(bindings):
                        row = table.rowCount()
                        self.dialog.add_hotkey_row(name if visible_index == 0 else "", key, key in conflicts)
                        self.row_data_map[row] = (category, command, index)
                        if self.row_data_map[row] == selection:
                            selected_row = row

        scroll.setValue(position)
        if selected_row >= 0:
            table.selectRow(selected_row)
        self.on_selection_changed()
    
    def on_category_changed(self, index: int):
        """处理类别切换"""
        if index >= 0:
            self.current_category = self.dialog.combo_category.itemData(index)
            self._set_search_text("")
            self._render_hotkey_list()
    
    def on_selection_changed(self):
        """处理表格选择变化"""
        self._update_button_states()
        self._update_status_label()
    
    def on_hotkey_edit_clicked(self, row: int):
        """处理快捷键输入框点击"""
        if not self.is_linked or row not in self.row_data_map:
            return
        self.on_edit_hotkey()
    
    def on_quote_mode_toggled(self):
        """处理单引号模式切换"""
        self.is_quote_mode_active = not self.is_quote_mode_active
        self.current_mode = 'character' if self.is_quote_mode_active else 'normal'
        self.keyboard_handler.set_mode(self.current_mode)
        self.dialog.set_button_active(self.dialog.btn_quote_mode, self.is_quote_mode_active)
    
    def on_edit_hotkey(self):
        """处理修改快捷键"""
        from ui.dialogs import KeyInputDialog, AlertDialog, ConfirmDialog
        
        selected_row = self.dialog.get_selected_row()
        if selected_row < 0 or selected_row not in self.row_data_map:
            return
        
        cat_id, cmd_id, idx = self.row_data_map[selected_row]
        item = self.hotkey_manager.get_item(cat_id, cmd_id)
        if not item:
            return
        
        shortcuts = item.get("shortcuts", [])
        old_hotkey = shortcuts[idx] if idx < len(shortcuts) else ""

        new_hotkey = KeyInputDialog.capture(
            self.dialog,
            mode=self.current_mode,
            current_hotkey=old_hotkey,
            mode_text=self._input_mode_name(),
            prompt_text=self.i18n_manager.get_text("dialogContent_pressKey", "请从键盘按下要设置的快捷键"),
            delete_text=self.i18n_manager.get_text("btnDeleteHotkey", "删除快捷键"),
            cancel_text=self.i18n_manager.get_text("btn_cancel", "取消")
        )
        
        if new_hotkey is None:
            return
        
        if new_hotkey == "":
            self._do_delete_hotkey(cat_id, cmd_id, idx)
            return
        
        existing_shortcuts = [s for i, s in enumerate(shortcuts) if s and i != idx]
        if new_hotkey in existing_shortcuts:
            AlertDialog.show_alert(
                self.dialog,
                self.i18n_manager.get_text("dialogTitle_warning", "提示"),
                self.i18n_manager.get_text("dialogContent_duplicateHotkey", "此快捷键已录入"),
                self.i18n_manager.get_text("btn_ok", "确认")
            )
            return
        
        conflicts = self.conflict_detector.get_conflicting_commands(new_hotkey, cat_id, cmd_id)
        to_clear = []
        if conflicts:
            result = ConfirmDialog.ask(
                self.dialog,
                self.i18n_manager.get_text("dialogTitle_confirm", "确认操作"),
                self.i18n_manager.get_text("dialogContent_conflict", "与已设置的快捷键存在冲突。\n是否删除已有的设置？"),
                self.i18n_manager.get_text("btn_yes", "是"),
                self.i18n_manager.get_text("btn_no", "否"),
                self.i18n_manager.get_text("btn_cancel", "取消")
            )
            
            if result == ConfirmDialog.CANCEL:
                return
            if result == ConfirmDialog.YES:
                to_clear = conflicts

        target = (cat_id, cmd_id, idx)
        with self.hotkey_manager.edit(target, to_clear):
            for conflict in to_clear:
                bindings = self.hotkey_manager.get_item(*conflict)["shortcuts"]
                if len(bindings) == 1:
                    self.hotkey_manager.set_shortcut_at_index(*conflict, 0, "")
                else:
                    self.hotkey_manager.remove_shortcut(*conflict, new_hotkey)
            self.hotkey_manager.set_shortcut_at_index(cat_id, cmd_id, idx, new_hotkey)
        self._render_hotkey_list(target)
    
    def on_add_hotkey(self):
        """处理添加快捷键"""
        selected_row = self.dialog.get_selected_row()
        if selected_row < 0 or selected_row not in self.row_data_map:
            return
        
        target = self.row_data_map[selected_row]
        cat_id, cmd_id, _ = target
        with self.hotkey_manager.edit(target):
            new_idx = self.hotkey_manager.add_empty_shortcut(cat_id, cmd_id)
        if new_idx >= 0:
            self._render_hotkey_list((cat_id, cmd_id, new_idx))
    
    def on_delete_hotkey(self):
        """处理删除快捷键"""
        selected_row = self.dialog.get_selected_row()
        if selected_row < 0 or selected_row not in self.row_data_map:
            return
        
        cat_id, cmd_id, idx = self.row_data_map[selected_row]
        self._do_delete_hotkey(cat_id, cmd_id, idx)
    
    def _do_delete_hotkey(self, cat_id: str, cmd_id: str, idx: int):
        """执行删除快捷键"""
        item = self.hotkey_manager.get_item(cat_id, cmd_id)
        if not item:
            return
        
        shortcuts = item.get("shortcuts", [])
        if idx >= len(shortcuts):
            return
        
        with self.hotkey_manager.edit((cat_id, cmd_id, idx)):
            if len(shortcuts) == 1:
                self.hotkey_manager.set_shortcut_at_index(cat_id, cmd_id, 0, "")
            else:
                self.hotkey_manager.remove_shortcut_at_index(cat_id, cmd_id, idx)
        self._render_hotkey_list((cat_id, cmd_id, max(0, idx - 1)))

    def on_undo_hotkey(self):
        target = self.hotkey_manager.undo()
        if target is None:
            return
        if not self.dialog.search_edit.text().strip():
            self.current_category = target[0]
            self._sync_category_selection()
        self._render_hotkey_list(target)
    
    def on_open_folder(self):
        """打开链接文件所在文件夹"""
        link_path = self.config_manager.get_link_path()
        if link_path and os.path.exists(link_path):
            folder = os.path.dirname(link_path)
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.run(['open', folder])
            else:
                subprocess.run(['xdg-open', folder])
    
    def on_language_changed(self, index: int):
        """处理语言切换"""
        if index >= 0:
            lang_code = self.dialog.combo_language.itemData(index)
            if lang_code and lang_code != self.i18n_manager.get_current_language():
                selection = self.row_data_map.get(self.dialog.get_selected_row())
                self.i18n_manager.load_language(lang_code)
                self.config_manager.set_primary_language(lang_code)
                self.update_ui_texts()
                self._update_window_title()
                self._populate_category_combo()
                
                if self.is_linked:
                    self._render_hotkey_list(selection)
    
    def on_info_button(self, info_type: str):
        """处理信息按钮点击"""
        from ui.dialogs import InfoDialog
        
        title = ""
        content = ""
        is_about = False
        
        if info_type == 'help':
            title = self.i18n_manager.get_text("dialogTitle_userGuide", "使用说明")
            content = self.i18n_manager.get_text("userGuide", "")
        elif info_type == 'hotkey_doc':
            title = self.i18n_manager.get_text("dialogTitle_shortcutsGuide", "快捷键说明")
            content = self.i18n_manager.get_text("shortcutsGuide", "")
        elif info_type == 'key_mapping':
            title = self.i18n_manager.get_text("dialogTitle_keyMapping", "关键字字符对应")
            content = self.i18n_manager.get_text("keyMapping", "")
        elif info_type == 'about':
            title = self.i18n_manager.get_text("dialogTitle_about", "程序信息")
            content = self._build_about_content()
            is_about = True
        
        InfoDialog(
            self.dialog,
            title,
            content,
            self.i18n_manager.get_text("btn_ok", "确认"),
            use_markdown=False,
            is_about=is_about
        ).exec()
    
    def _build_about_content(self) -> str:
        """构建程序信息内容"""
        designer_label = self.i18n_manager.get_text("about_designer", "设计")
        version_label = self.i18n_manager.get_text("about_version", "版本")
        build_label = self.i18n_manager.get_text("about_buildDate", "构建")
        compatible_label = self.i18n_manager.get_text("about_compatible", "适配")
        
        designer = "Voice of Shadow"
        version = self.config_manager.get_version()
        build_date = self.config_manager.get_build_date()
        compatible = self.config_manager.get_compatible_version()
        
        content = f"""- {designer_label}：\t{designer}
- {version_label}：\t{version}
- {build_label}：\t{build_date}
- {compatible_label}：\t{compatible}"""
        
        return content
    
    def on_save(self):
        """处理保存操作"""
        if self._confirm_save():
            self.dialog.accept()
    
    def on_save_only(self):
        """处理仅保存操作，不退出程序"""
        self._confirm_save()

    def _confirm_save(self) -> bool:
        """取消或写入失败时保持窗口打开。仅在快捷键文件写入成功后更新保存点。"""
        from ui.dialogs import ConfirmDialog, AlertDialog

        if not self.is_linked or not self.hotkey_manager.is_modified():
            return True

        result = ConfirmDialog.ask(
            self.dialog,
            self.i18n_manager.get_text("dialogTitle_confirmSave", "确认保存"),
            self.i18n_manager.get_text("dialogContent_saveChanges", "是否保存对快捷键的修改？"),
            self.i18n_manager.get_text("btn_yes", "是"),
            self.i18n_manager.get_text("btn_no", "否"),
            self.i18n_manager.get_text("btn_cancel", "取消")
        )

        if result != ConfirmDialog.YES:
            return result == ConfirmDialog.NO

        try:
            json_path = self.hotkey_manager.get_json_path()
            if not self.hotkey_manager.save_to_json(mark_saved=False):
                raise OSError(json_path)
            FileConverter.json_to_txt(json_path, self.config_manager.get_link_path())
            self.hotkey_manager.set_modified(False)
            return True
        except Exception as e:
            AlertDialog.show_alert(
                self.dialog,
                self.i18n_manager.get_text("dialogTitle_formatError", "错误"),
                str(e),
                self.i18n_manager.get_text("btn_ok", "确认")
            )
            return False
    
    def on_cancel(self):
        """处理取消操作"""
        self.dialog.reject()
