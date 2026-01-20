# -*- coding: utf-8 -*-
"""
主控制器模块
协调所有模块，连接 UI 和业务逻辑
"""

import os
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import QFileDialog, QApplication

from .config_manager import ConfigManager
from .i18n_manager import I18nManager
from .hotkey_manager import HotkeyManager
from .conflict_detector import ConflictDetector
from .keyboard_handler import KeyboardHandler
from utils.file_converter import FileConverter
from utils.resource_path import get_external_resource_path


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
        
        self.row_data_map: Dict[int, Tuple[str, str, int]] = {}

        self.current_category = ""

        self._connect_signals()
    
    def _connect_signals(self):
        """连接 UI 信号到处理方法"""
        self.dialog.btn_link.clicked.connect(self.on_link_clicked)
        self.dialog.btn_open_folder.clicked.connect(self.on_open_folder)
        self.dialog.btn_edit_hotkey.clicked.connect(self.on_edit_hotkey)
        self.dialog.btn_add_hotkey.clicked.connect(self.on_add_hotkey)
        self.dialog.btn_delete_hotkey.clicked.connect(self.on_delete_hotkey)
        self.dialog.btn_quote_mode.clicked.connect(self.on_quote_mode_toggled)
        self.dialog.btn_help.clicked.connect(lambda: self.on_info_button('help'))
        self.dialog.btn_hotkey_doc.clicked.connect(lambda: self.on_info_button('hotkey_doc'))
        self.dialog.btn_key_mapping.clicked.connect(lambda: self.on_info_button('key_mapping'))
        self.dialog.btn_about.clicked.connect(lambda: self.on_info_button('about'))
        self.dialog.button_box.accepted.connect(self.on_save)
        self.dialog.button_box.rejected.connect(self.on_cancel)
        self.dialog.combo_category.currentIndexChanged.connect(self.on_category_changed)
        self.dialog.combo_language.currentIndexChanged.connect(self.on_language_changed)
        self.dialog.hotkey_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.dialog.hotkey_edit_clicked.connect(self.on_hotkey_edit_clicked)
    
    def initialize(self):
        """执行启动初始化流程"""
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
        self.dialog.label_language.setText(
            self.i18n_manager.get_text("labelLanguage", "语言：")
        )
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
        self.dialog.button_box.button(QDialogButtonBox.Ok).setText(
            self.i18n_manager.get_text("btn_ok", "确认")
        )
        self.dialog.button_box.button(QDialogButtonBox.Cancel).setText(
            self.i18n_manager.get_text("btn_cancel", "取消")
        )
    
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
            
            self.hotkey_manager.load_from_json(json_path)
            self._normalize_empty_shortcuts()
            self.config_manager.set_link_path(file_path)
            self.is_linked = True
            
            self.dialog.btn_link.setText(
                self.i18n_manager.get_text("btnLink_relink", "重链接")
            )
            self._update_window_title()
            self._update_button_states()
            self._populate_category_combo()
            
            if self.current_category:
                self._render_hotkey_list()
        
        except Exception as e:
            AlertDialog.show_alert(
                self.dialog,
                self.i18n_manager.get_text("dialogTitle_formatError", "格式化错误"),
                str(e),
                self.i18n_manager.get_text("btn_ok", "确认")
            )
    
    def _normalize_empty_shortcuts(self):
        """将空快捷键列表转换为包含单个空字符串的列表"""
        for category in self.hotkey_manager.data:
            for item in category.get("items", []):
                shortcuts = item.get("shortcuts", [])
                if not shortcuts:
                    item["shortcuts"] = [""]
    
    def _populate_category_combo(self):
        """填充类别下拉列表"""
        self.dialog.combo_category.blockSignals(True)
        self.dialog.combo_category.clear()
        
        categories = self.hotkey_manager.get_categories()
        for cat_id in categories:
            display_name = self.i18n_manager.get_category_name(cat_id)
            self.dialog.combo_category.addItem(display_name, cat_id)
        
        if categories:
            self.current_category = categories[0]
            self.dialog.combo_category.setCurrentIndex(0)
        
        self.dialog.combo_category.blockSignals(False)
    
    def _render_hotkey_list(self, preserve_selection: bool = False, target_row: int = -1):
        """
        渲染快捷键列表
        
        Args:
            preserve_selection: 是否保持之前的选中状态
            target_row: 指定要选中的行索引（-1表示使用当前选中行）
        """
        current_row = self.dialog.get_selected_row()
        scroll_bar = self.dialog.hotkey_table.verticalScrollBar()
        scroll_position = scroll_bar.value()
        
        self.dialog.clear_hotkey_list()
        self.row_data_map.clear()
        
        if not self.current_category:
            return
        
        self.conflict_detector.invalidate_cache()
        conflicting_shortcuts = self.conflict_detector.get_shortcuts_with_conflicts()
        items = self.hotkey_manager.get_items_by_category(self.current_category)
        
        row_index = 0
        for i, item in enumerate(items):
            cmd_id = item.get("commandId", "")
            shortcuts = item.get("shortcuts", [])
            
            if i > 0:
                self.dialog.add_separator_row()
                row_index += 1
            
            cmd_name = self.i18n_manager.get_command_name(cmd_id)
            
            if not shortcuts:
                show_warning = False
                self.dialog.add_hotkey_row(cmd_name, "", show_warning)
                self.row_data_map[row_index] = (self.current_category, cmd_id, 0)
                row_index += 1
            else:
                for idx, shortcut in enumerate(shortcuts):
                    name_display = cmd_name if idx == 0 else ""
                    show_warning = shortcut in conflicting_shortcuts
                    
                    self.dialog.add_hotkey_row(name_display, shortcut, show_warning)
                    self.row_data_map[row_index] = (self.current_category, cmd_id, idx)
                    row_index += 1

        scroll_bar.setValue(scroll_position)

        if preserve_selection or target_row >= 0:
            row_to_select = target_row if target_row >= 0 else current_row
            if row_to_select >= 0 and row_to_select < self.dialog.hotkey_table.rowCount():
                if row_to_select not in self.dialog._separator_rows:
                    self.dialog.hotkey_table.selectRow(row_to_select)
                    self.dialog._selected_row = row_to_select
    
    def on_category_changed(self, index: int):
        """处理类别切换"""
        if index >= 0:
            self.current_category = self.dialog.combo_category.itemData(index)
            self._render_hotkey_list()
            self.dialog.clear_selection()
            self._update_button_states()
            self._update_status_label()
    
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

        if self.is_quote_mode_active:
            mode_text = self.i18n_manager.get_text("dialogTitle_characterMode", "单引号模式")
        else:
            mode_text = self.i18n_manager.get_text("dialogTitle_normalMode", "一般模式")
        
        new_hotkey = KeyInputDialog.capture(
            self.dialog,
            mode=self.current_mode,
            current_hotkey=old_hotkey,
            mode_text=mode_text,
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
            elif result == ConfirmDialog.YES:
                for conflict_cat, conflict_cmd in conflicts:
                    self.hotkey_manager.remove_shortcut(conflict_cat, conflict_cmd, new_hotkey)
        
        if old_hotkey:
            self.hotkey_manager.update_shortcut(cat_id, cmd_id, old_hotkey, new_hotkey)
        else:
            self.hotkey_manager.set_shortcut_at_index(cat_id, cmd_id, idx, new_hotkey)
        
        self._render_hotkey_list(preserve_selection=True)
        self._update_button_states()
    
    def on_add_hotkey(self):
        """处理添加快捷键"""
        selected_row = self.dialog.get_selected_row()
        if selected_row < 0 or selected_row not in self.row_data_map:
            return
        
        cat_id, cmd_id, _ = self.row_data_map[selected_row]
        new_idx = self.hotkey_manager.add_empty_shortcut(cat_id, cmd_id)
        if new_idx >= 0:
            self._render_hotkey_list()
            
            target_row = -1
            for row, (r_cat, r_cmd, r_idx) in self.row_data_map.items():
                if r_cat == cat_id and r_cmd == cmd_id and r_idx == new_idx:
                    target_row = row
                    break

            if target_row >= 0 and target_row < self.dialog.hotkey_table.rowCount():
                if target_row not in self.dialog._separator_rows:
                    self.dialog.hotkey_table.selectRow(target_row)
                    self.dialog._selected_row = target_row
            
            self._update_button_states()
    
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
        
        selected_row = self.dialog.get_selected_row()
        target_row = selected_row
        
        is_first_shortcut = (idx == 0)
        
        if len(shortcuts) == 1:
            self.hotkey_manager.set_shortcut_at_index(cat_id, cmd_id, 0, "")
        else:
            self.hotkey_manager.remove_shortcut_at_index(cat_id, cmd_id, idx)
            
            if not is_first_shortcut and selected_row > 0:
                target_row = selected_row - 1
        
        self._render_hotkey_list(target_row=target_row)
        self._update_button_states()
    
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
                self.i18n_manager.load_language(lang_code)
                self.config_manager.set_primary_language(lang_code)
                self.update_ui_texts()
                self._update_window_title()
                self._populate_category_combo()
                
                if self.is_linked:
                    self._render_hotkey_list()
                
                self._update_status_label()
    
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
        from ui.dialogs import ConfirmDialog, AlertDialog
        
        if not self.is_linked:
            self.dialog.accept()
            return
        
        if not self.hotkey_manager.is_modified():
            self.dialog.accept()
            return

        result = ConfirmDialog.ask(
            self.dialog,
            self.i18n_manager.get_text("dialogTitle_confirmSave", "确认保存"),
            self.i18n_manager.get_text("dialogContent_saveChanges", "是否保存对快捷键的修改？"),
            self.i18n_manager.get_text("btn_yes", "是"),
            self.i18n_manager.get_text("btn_no", "否"),
            self.i18n_manager.get_text("btn_cancel", "取消")
        )
        
        if result == ConfirmDialog.CANCEL:
            return
        
        if result == ConfirmDialog.YES:
            self.hotkey_manager.save_to_json()
            json_path = self.hotkey_manager.get_json_path()
            link_path = self.config_manager.get_link_path()
            
            if json_path and link_path:
                try:
                    FileConverter.json_to_txt(json_path, link_path)
                except Exception as e:
                    AlertDialog.show_alert(
                        self.dialog,
                        self.i18n_manager.get_text("dialogTitle_formatError", "错误"),
                        str(e),
                        self.i18n_manager.get_text("btn_ok", "确认")
                    )
                    return
        
        self.dialog.accept()
    
    def on_cancel(self):
        """处理取消操作"""
        self.dialog.reject()
