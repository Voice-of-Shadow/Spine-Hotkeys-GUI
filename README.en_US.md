<div align="center">

<img src="icon/icon%20(00000).png" alt="居中图片" align="center" />

<br />

# Spine Hotkeys Editor

</div>

<br />
<br />

[简体中文](README.md) | **English**

Spine Hotkeys Editor is a GUI tool for edit Spine shortcuts, developed with PySide6. It aims to replace Spine's extremely primitive method of shortcut customization.

<br />

# Features

- **Visual Shortcut Editing**
- **Shortcut Conflict Detection**
- **Dual Input Modes**
- **Multi-language Support**
- **Path Linking and Temporary Backup**

<br />

# Screenshots

<div align="center">
<img src="https://img.reimu.net/uploads/2026/01/696f9a4880fa52.82162354.png" alt="居中图片" align="center" />
</div>

<br />

# Run

#### Run by executing the Python code

```shell
pip install -r requirements.txt
python main.py
```

#### Obtain the executable program Spine Hotkeys Editor.exe through payment

- **[Afdian → 6CNY](https://afdian.com/item/848b53def54411f0b8845254001e7c00)**
- **[BOOTH → 240JPY](https://vosaa2a3.booth.pm/items/7895722)**

 **(Special note: Due to regional restrictions and other reasons, I am temporarily unable to provide sponsorship channels on platforms such as "Buy Me a Coffee")**

 **(Special Note: This build will be release once the promotional video reaches 50,000 views or this project reaches 50 stars. This sale will be considered a pure sponsorship.)**

<br />

# Usage Instructions

#### Core Usage Guide

1. **Link the shortcut file**: On first launch, click the "Link" button and select the Spine shortcut file. `hotkeys-1.txt (v4.0+)`
2. **Select input mode**: Activate character mode or switch back to general input mode by clicking the "Character Mode" button.
3. **Edit shortcuts**: Select a row of entries to edit.
4. **View instructions**: Click the corresponding button on the right to view User Guide, Shortcuts Guide, Key Mapping, About.
5. **Save changes and reload**: After clicking "OK" in the main window, restart Spine or reload shortcuts in the Spine editor settings.

#### Other Operation Instructions

- **Backup**: Click the "Open Folder" button to open the path of the linked file and back up the shortcut file.
- **Restore the shortcut before editing**: Replace Spine's shortcut file with the one in the .`/processing/` directory.
- **Restore default shortcuts**: Delete the shortcut file or click "Restore Default" in the Spine editor settings.
- **Switch languages**: Select the corresponding language from the dropdown on the right. Ensure the corresponding language pack exists and is enabled in the configuration.

<br />

# **Shortcuts Guide**

- In General Mode, hotkey combinations can use modifier keys such as "Ctrl", "Shift", and "Alt".
- In Character Mode (Single-quote Mode), only the "Alt" modifier key can be used in hotkey combinations.
- When using Character Mode, hotkeys gain long-press functionality: after an initial trigger and a short delay, the action will repeat continuously.
- Character Mode accepts single typable characters ('a'、'ア'、'啊'、'↓'). Some characters have corresponding keywords.
- Special characters not present on a standard keyboard require key mapping in Single-quote Mode; please avoid entering unexpected or unsupported characters.

<br />

# compatibility instructions

The GUI program works by parsing the structure of Spine shortcut files and performing data conversion. Therefore, its functionality theoretically covers shortcut files for all current versions of Spine.

Displayed text uses corresponding values from the language pack. Since shortcuts vary across different Spine versions, some shortcut names are not recorded in the language pack, and in such cases, the original name is displayed.

As shortcuts are primarily added with version updates, the currently provided language pack is created using the shortcut file from the latest version of Spine.

<br />

# Changelog

[Changelog_Chinese](CHANGELOG.md)

<br />

# Other instructions

- Development Motivation：70% plenty of free time(long-term unemployment), 20% frustration with Spine's extremely primitive shortcut editing method, 9% as the final act of cutting ties with 2D animation production, **100‰ for contributing to the community**.
- Development Direction：Overall reference to Live2D's shortcut GUI modification logic and layout.
- Special Note：I am not a professional software developer. Code, configuration, and program logic design may be unreasonable, non-standard, or non-standardized. Feature additions, code improvements, and project optimizations will be left to future contributors (I still hope the official team would develop one, it has been pending for years).
- Special Note: I do not know English. The default English documentation is machine-translated. English localization optimization is needed.
- Special Note: This program is only compatible with standard US keyboards.
- Special Note: Under the current latest beta version (4.3.39-beta), in Character Mode, 'PLUS' → will be flagged as an invalid character by the Spine editor, and '+' will cause a direct error, rendering all hotkeys unusable. Although input is not prohibited by design, please treat this character as unexpected input and avoid using it. Official feedback confirms it will be fixed in the next version.
- Special Note: The current program's preprocessing stage cannot exclude all unexpected shortcuts (i.e., syntactically valid but with invalid keys or unrecognizable by the Spine editor).
- Special Note: Due to Windows limitations, `Shift + NUMPAD_(0~9/.)` is always converted to navigation keys regardless of the `NumLock` state. This is a system-level restriction. Spine, unlike software such as After Effects (AE), does not implement low-level system hooks and thus cannot recognize the navigation keys on the numpad. Therefore, if you need to force the input, you must modify the system-wide key mapping. This can be done by binding key remappings using tools like AutoHotkey or PowerToys. However, in this scenario, only the right Shift key (RShift) can be registered, while the left Shift key (LShift) will be blocked. For smoother usage, it is recommended to avoid hotkeys in the `Shift + NUMPAD_(0~9/.)` series.

<br />

# Contributions

Code contributions and additional localized language packs are welcome.

#### Areas for Improvement:

1. **Features**:

   - Search functionality: search shortcut names and shortcuts.
   - Step-by-step undo (revert the previous edit operation).
   - Integrate import, export, reset functions into the program.
   - Test and adapt support for more input devices (e.g., software control panels like TourBox, game controllers, etc.).
2. **Aesthetics**:

   - Add theme functionality, including a dark theme matching Spine editor's default appearance.
   - Implement a custom title bar with visual feedback for link status.
3. **Internationalization**:

   - Fix potential machine-translation errors in the English language pack.
   - Expand shortcut description texts (`[KeyName].note`).
   - Add more internationalized language packs.

<br />

# Support

If this project is helpful to you, please feel free to share it.

you can support it by **[sponsoring on Afdian](https://afdian.com/a/VOSAA2A3)** or **[via Bilibili charging](https://space.bilibili.com/23488880)**. I'd be happy if you could treat me to a cup of milk tea.

You can follow my Bilibili account, where I will post my works and tutorials.

Link: [https://space.bilibili.com/23488880](https://space.bilibili.com/23488880)

<br />

# License

This project is open-sourced under the [MIT](LICENSE) license. See the LICENSE file for details.
