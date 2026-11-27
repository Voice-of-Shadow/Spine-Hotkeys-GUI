import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QEvent, QPoint, Qt, QTimer
from PySide6.QtGui import QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QAbstractItemView, QDialogButtonBox, QLineEdit

from core.config_manager import ConfigManager
from core.controller import Controller
from ui.dialogs import AlertDialog, ConfirmDialog, KeyInputDialog
from ui.hotkey_dialog import HotkeyDialog
from ui.theme import apply_theme


class EditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["editor-tests", "-platform", "offscreen"])

    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        root = Path(stack.enter_context(tempfile.TemporaryDirectory()))
        stack.enter_context(patch("utils.resource_path.get_resource_base_path", return_value=str(root)))
        stack.enter_context(patch("ui.hotkey_dialog.get_bundled_resource_path", return_value=str(root / "warning.png")))
        stack.enter_context(patch("core.controller.apply_theme"))
        stack.enter_context(patch.object(AlertDialog, "show_alert", side_effect=AssertionError("Unexpected alert")))
        language = root / "language"
        language.mkdir()
        (language / "Interface.zh_CN.json").write_text("{}", encoding="utf-8")
        (language / "KeyDoc.zh_CN.json").write_text('{"Redo": "重做"}', encoding="utf-8")
        self.link = root / "hotkeys-test.txt"
        self.link.write_text(
            "--- General ---\nUndo: F8\nRedo: F2\nRedo: ctrl + shift + Y\n"
            "Rulers: ctrl + K\nNext Frame: 'r'\nNext Frame (10): 'R'\n"
            "Toggle Overlay: K\nKey List: F4\nSwitch View: TAB\nNext Tab: ctrl + TAB\n"
            "Confirm: ENTER\nPlay: SPACE\nSearch Editor: ctrl + shift + F\n\n"
            "--- Tools ---\nRotate Tool: F3\nRotate Tool: ctrl + K\n",
            encoding="utf-8",
        )
        self.dialog = HotkeyDialog()
        self.addCleanup(self.dialog.deleteLater)
        self.addCleanup(self.dialog.close)
        self.controller = Controller(self.dialog)
        self.manager = self.controller.hotkey_manager
        self.controller.config_manager.set_initialized(True)
        self.controller.config_manager.set_link_path(str(self.link))
        self.controller.initialize()
        self.dialog.show()
        self.app.processEvents()
        self.assertTrue(self.controller.is_linked)

    def select(self, category, command, index=0):
        rows = self.controller.row_data_map
        row = next(row for row, target in rows.items() if target == (category, command, index))
        self.dialog.hotkey_table.selectRow(row)

    def edit(self, binding):
        with patch.object(KeyInputDialog, "capture", return_value=binding):
            self.dialog.btn_edit_hotkey.click()

    def bindings(self, category, command):
        return self.manager.get_item(category, command)["shortcuts"]

    def capture_search(self, key, modifiers=Qt.KeyboardModifier.NoModifier, *, shortcut_focus=None):
        opened = []

        def press_key():
            modal = self.app.activeModalWidget()
            if modal is None:
                return
            opened.append(modal)
            modal.activateWindow()
            self.app.processEvents()
            target = self.app.focusWidget() or modal
            if isinstance(key, str):
                QTest.keyClicks(target, key, modifiers)
            else:
                QTest.keyClick(target, key, modifiers)
            if modal.isVisible():
                modal.reject()

        self.dialog.activateWindow()
        if shortcut_focus is not None:
            shortcut_focus.setFocus()
        self.app.processEvents()
        QTimer.singleShot(0, press_key)
        if shortcut_focus is not None:
            QTest.keyClick(shortcut_focus, Qt.Key.Key_F,
                           Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)
        else:
            self.dialog.btn_capture_search.click()
        self.app.processEvents()
        self.assertEqual(len(opened), 1, "The search capture dialog did not open")

    def test_recorded_shortcuts_match_only_the_exact_binding(self):
        before = deepcopy(self.manager.data)
        ctrl_shift = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
        for key, modifiers, command, index, focus in [
            (Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier, "Switch View", 0, self.dialog.search_edit),
            (Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier, "Confirm", 0, self.dialog.combo_category),
            (Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier, "Play", 0, None),
            (Qt.Key.Key_F, ctrl_shift, "Search Editor", 0, self.dialog.hotkey_table),
            (Qt.Key.Key_Y, ctrl_shift, "Redo", 1, None),
            (Qt.Key.Key_K, Qt.KeyboardModifier.NoModifier, "Toggle Overlay", 0, None),
        ]:
            with self.subTest(command=command):
                self.capture_search(key, modifiers, shortcut_focus=focus)
                self.assertEqual(list(self.controller.row_data_map.values()), [("General", command, index)])
        self.assertEqual(self.manager.data, before)
        self.assertFalse(self.manager.can_undo())
        self.assertFalse(self.manager.is_modified())

    def assert_popup_centered(self, frame):
        """弹窗的窗口框（含标题栏）应对齐父窗口中心。"""
        parent = self.dialog.frameGeometry()
        available = self.dialog.screen().availableGeometry()
        expected = QPoint(
            max(available.left(), min(parent.center().x() - frame.width() // 2,
                                      available.right() - frame.width() + 1)),
            max(available.top(), min(parent.center().y() - frame.height() // 2,
                                     available.bottom() - frame.height() + 1)),
        )
        # 离屏平台在原生窗口创建后才报告边框，允许几个像素的边框误差。
        self.assertLessEqual((frame.topLeft() - expected).manhattanLength(), 6)

    def record_show_events(self, dialog_class):
        """记录弹窗的 Show 位置，以及出现之后是否还被移动过。"""
        shown = []
        moves_after_show = []
        state = {"shown": False}
        original_event = dialog_class.event

        def record(dialog, event):
            if event.type() == QEvent.Type.Show:
                state["shown"] = True
                shown.append(dialog.frameGeometry())
            elif event.type() == QEvent.Type.Move and state["shown"]:
                moves_after_show.append(dialog.frameGeometry())
            return original_event(dialog, event)

        return shown, moves_after_show, patch.object(dialog_class, "event", record)

    @staticmethod
    def close_active_modal():
        popup = QApplication.activeModalWidget()
        if popup is not None:
            popup.reject()

    def test_edit_popup_is_centered_before_it_is_shown(self):
        self.dialog.move(174, 111)
        self.select("General", "Undo")
        shown, moves_after_show, patch_event = self.record_show_events(KeyInputDialog)

        with patch_event:
            QTimer.singleShot(0, self.close_active_modal)
            self.dialog.btn_edit_hotkey.click()

        self.assertEqual(len(shown), 1)
        self.assert_popup_centered(shown[0])
        self.assertEqual(moves_after_show, [], "弹窗出现后不应再被移动到中间")

    def test_edit_popup_does_not_show_an_extra_window(self):
        from PySide6.QtCore import QObject
        from PySide6.QtWidgets import QWidget

        class WindowObserver(QObject):
            def __init__(self):
                super().__init__()
                self.windows = []

            def eventFilter(self, widget, event):
                if event.type() == QEvent.Type.Show and isinstance(widget, QWidget) and widget.isWindow():
                    self.windows.append(type(widget))
                return False

        table = self.dialog.hotkey_table
        self.select("General", "Undo")
        row = self.dialog.get_selected_row()
        position = table.visualRect(table.model().index(row, 2)).center()
        observer = WindowObserver()
        self.app.installEventFilter(observer)
        self.addCleanup(self.app.removeEventFilter, observer)
        for open_editor in (
            self.dialog.btn_edit_hotkey.click,
            lambda: QTest.mouseClick(table.viewport(), Qt.MouseButton.LeftButton, pos=position),
        ):
            observer.windows.clear()
            QTimer.singleShot(0, self.close_active_modal)
            open_editor()
            self.assertEqual(observer.windows, [KeyInputDialog])

    def test_edit_popup_is_positioned_before_native_window_is_created(self):
        self.dialog.move(174, 111)
        self.select("General", "Undo")
        placements = []
        original_center = KeyInputDialog.center_over_parent

        def record_center(dialog):
            original_center(dialog)
            placements.append((dialog.internalWinId(), dialog.frameGeometry()))

        with patch.object(KeyInputDialog, "center_over_parent", record_center):
            QTimer.singleShot(0, self.close_active_modal)
            self.dialog.btn_edit_hotkey.click()

        self.assertEqual(len(placements), 1)
        native_handle, frame = placements[0]
        self.assertFalse(native_handle, "定位时不应提前创建原生窗口")
        self.assert_popup_centered(frame)

    def test_search_popup_is_centered_before_it_is_shown(self):
        self.dialog.move(174, 111)
        shown, moves_after_show, patch_event = self.record_show_events(KeyInputDialog)

        with patch_event:
            self.capture_search(Qt.Key.Key_K)

        self.assertEqual(len(shown), 1)
        self.assert_popup_centered(shown[0])
        self.assertEqual(moves_after_show, [])

    def test_confirmation_popup_is_centered_before_it_is_shown(self):
        self.dialog.move(174, 111)
        shown, moves_after_show, patch_event = self.record_show_events(ConfirmDialog)

        with patch_event:
            QTimer.singleShot(0, self.close_active_modal)
            ConfirmDialog.ask(self.dialog, "确认", "是否继续？", "是", "否", "取消")

        self.assertEqual(len(shown), 1)
        self.assert_popup_centered(shown[0])
        self.assertEqual(moves_after_show, [])

    def test_typing_after_capture_searches_names_and_partial_bindings_again(self):
        self.capture_search(Qt.Key.Key_K)
        search = self.dialog.search_edit
        search.setFocus()
        search.selectAll()
        QTest.keyClicks(search, "k")
        self.assertCountEqual(self.controller.row_data_map.values(), [
            ("General", "Toggle Overlay", 0), ("General", "Key List", 0),
            ("General", "Rulers", 0), ("Tools", "Rotate Tool", 1),
        ])

    def test_search_capture_respects_character_mode_and_case(self):
        self.dialog.btn_quote_mode.click()
        for character, command in [("r", "Next Frame"), ("R", "Next Frame (10)")]:
            with self.subTest(character=character):
                self.capture_search(character)
                self.assertEqual(self.dialog.search_edit.text(), f"'{character}'")
                self.assertEqual(list(self.controller.row_data_map.values()), [("General", command, 0)])
        self.assertEqual(self.controller.current_mode, "character")
        self.assertFalse(self.manager.can_undo())

    def test_capture_button_icon_has_contrast_in_both_themes(self):
        self.addCleanup(self.app.setStyleSheet, self.app.styleSheet())
        self.addCleanup(self.app.setPalette, self.app.palette())
        self.addCleanup(self.app.styleHints().setColorScheme, self.app.styleHints().colorScheme())
        button = self.dialog.btn_capture_search
        for theme in ("light", "dark"):
            with self.subTest(theme=theme):
                apply_theme(theme)
                icon = button.icon().pixmap(button.iconSize()).toImage()
                ink = max((icon.pixelColor(x, y) for x in range(icon.width()) for y in range(icon.height())),
                          key=lambda color: color.alpha())
                self.assertGreater(ink.alpha(), 200)
                background = self.app.palette().button().color().lightness()
                self.assertGreater(abs(ink.lightness() - background), 100)

    def test_cancel_search_capture_preserves_query_edits_and_undo_history(self):
        self.select("General", "Undo")
        self.edit("F9")
        self.dialog.search_edit.setText("重做")
        before = deepcopy(self.manager.data)
        visible = dict(self.controller.row_data_map)
        self.capture_search(Qt.Key.Key_Escape)
        self.assertEqual(self.dialog.search_edit.text(), "重做")
        self.assertEqual(self.controller.row_data_map, visible)
        self.assertEqual(self.manager.data, before)
        self.dialog.btn_undo_hotkey.click()
        self.assertEqual(self.bindings("General", "Undo"), ["F8"])
        self.assertFalse(self.manager.can_undo())

    def test_search_keeps_binding_indices_and_character_case(self):
        search = self.dialog.search_edit
        rows = self.controller.row_data_map
        search.setText("重做")
        self.assertEqual(list(rows.values()), [("General", "Redo", 0), ("General", "Redo", 1)])
        search.setText("CTRL+SHIFT+y")
        self.assertEqual(list(rows.values()), [("General", "Redo", 1)])
        self.select("General", "Redo", 1)
        self.edit("F5")
        self.assertEqual(self.bindings("General", "Redo"), ["F2", "F5"])
        self.assertFalse(rows)
        for query, command in [("'r'", "Next Frame"), ("'R'", "Next Frame (10)")]:
            search.setText(query)
            self.assertEqual(list(rows.values()), [("General", command, 0)])

    def test_shortcut_cells_keep_their_text_and_border_after_scrolling(self):
        self.addCleanup(self.app.setStyleSheet, self.app.styleSheet())
        self.addCleanup(self.app.styleHints().setColorScheme, self.app.styleHints().colorScheme())
        self.addCleanup(self.app.setPalette, self.app.palette())
        bindings = "".join(f"Sample {i}: ctrl + F{i}\n" for i in range(1, 21))
        original = self.link.read_text(encoding="utf-8")
        self.link.write_text(original.replace("--- Tools ---", bindings + "\n--- Tools ---"), encoding="utf-8")
        self.controller._do_import(str(self.link))
        table = self.dialog.hotkey_table
        table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        reference = QLineEdit()
        reference.setReadOnly(True)
        reference.resize(280, 28)
        for theme in ("light", "dark"):
            apply_theme(theme)
            for query in ("", "ctrl"):
                self.dialog.search_edit.setText(query)
                self.assertGreater(table.verticalScrollBar().maximum(), 73)
                for position in (0, 73, 11, 0):
                    with self.subTest(theme=theme, query=query, position=position):
                        table.verticalScrollBar().setValue(position)
                        self.app.processEvents()
                        viewport = table.viewport()
                        image = viewport.grab().toImage()
                        visible = 0
                        for row in self.controller.row_data_map:
                            index = table.model().index(row, 2)
                            rect = table.visualRect(index).adjusted(1, 4, -9, -4)
                            if not viewport.rect().contains(rect):
                                continue
                            visible += 1
                            reference.setFont(table.font())
                            reference.setText(index.data())
                            reference.setCursorPosition(0)
                            expected = reference.grab().toImage()
                            scale = image.devicePixelRatio()
                            points = ((rect.x() + 150, rect.y() - 1), (rect.x() + 150, rect.y()))
                            background, border = (
                                image.pixelColor(round(x * scale), round(y * scale))
                                for x, y in points
                            )
                            self.assertEqual(background, table.palette().base().color())
                            self.assertEqual(border, table.palette().mid().color())
                            text_area = (6, 3, 240, 22)
                            actual_text = image.copy(
                                round((rect.x() + text_area[0]) * scale),
                                round((rect.y() + text_area[1]) * scale),
                                round(text_area[2] * scale),
                                round(text_area[3] * scale),
                            )
                            expected_text = expected.copy(*(round(n * scale) for n in text_area))
                            rgb = QImage.Format.Format_RGB32
                            self.assertEqual(actual_text.convertToFormat(rgb), expected_text.convertToFormat(rgb),
                                             (row, index.data()))
                        self.assertGreater(visible, 0)

    def test_undo_restores_all_conflicting_bindings_in_one_step(self):
        before = deepcopy(self.manager.data)
        self.select("General", "Undo")
        with patch.object(ConfirmDialog, "ask", return_value=ConfirmDialog.YES):
            self.edit("ctrl + K")
        self.assertEqual(self.bindings("General", "Undo"), ["ctrl + K"])
        self.assertEqual(self.bindings("General", "Rulers"), [""])
        self.assertEqual(self.bindings("Tools", "Rotate Tool"), ["F3"])
        self.dialog.btn_undo_hotkey.click()
        self.assertEqual(self.manager.data, before)
        self.assertFalse(self.dialog.btn_undo_hotkey.isEnabled())
        self.assertFalse(self.manager.is_modified())

    def test_save_after_undo_writes_to_linked_file(self):
        self.select("General", "Undo")
        self.edit("F9")
        save = self.dialog.button_box.button(QDialogButtonBox.StandardButton.Save)
        with patch.object(ConfirmDialog, "ask", return_value=ConfirmDialog.YES):
            save.click()
            self.assertIn("Undo: F9", self.link.read_text(encoding="utf-8"))
            self.dialog.btn_undo_hotkey.click()
            self.assertTrue(self.manager.is_modified())
            save.click()
        self.assertIn("Undo: F8", self.link.read_text(encoding="utf-8"))
        self.assertFalse(self.manager.is_modified())

    def test_input_dialog_captures_ctrl_z_with_an_edit_pending(self):
        self.select("General", "Undo")
        self.edit("F9")
        self.select("General", "Redo")

        def press_ctrl_z():
            modal = self.app.activeModalWidget()
            QTest.keyClick(modal, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
            if modal.isVisible():
                modal.reject()

        QTimer.singleShot(0, press_ctrl_z)
        self.dialog.btn_edit_hotkey.click()
        self.assertEqual(self.bindings("General", "Redo")[0], "ctrl + Z")
        self.assertEqual(self.bindings("General", "Undo"), ["F9"])


class PackagedConfigTests(unittest.TestCase):
    def test_startup_preserves_metadata_from_existing_config(self):
        project = Path(__file__).resolve().parents[1]
        settings = json.loads((project / "config.json").read_text(encoding="utf-8"))
        settings["metadata"].update(version="custom-editor", build_date="2000.01.01",
                                    compatible_version="custom-spine", extra_field="custom-value")
        settings["localization"]["primary_language"] = "en_US"
        settings["system"].update(theme="dark", initialized=True, link_path="personal-hotkeys.txt")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps(settings), encoding="utf-8")
            with patch.object(sys, "frozen", True, create=True), patch.object(sys, "_MEIPASS", str(project), create=True):
                config = ConfigManager(str(path))
                self.assertEqual(config.get_version(), "custom-editor")
                self.assertEqual(config.get_build_date(), "2000.01.01")
                self.assertEqual(config.get_compatible_version(), "custom-spine")
                config.update_system_status()
            updated = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(updated["system"]["last_loaded"])
            updated["system"]["last_loaded"] = settings["system"]["last_loaded"]
            self.assertEqual(updated["system"], settings["system"])
            self.assertEqual(updated["localization"], settings["localization"])
            self.assertEqual(updated["metadata"], settings["metadata"])
