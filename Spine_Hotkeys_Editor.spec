# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Spine Hotkeys Editor
用于打包生成独立可执行文件
"""

import json
from pathlib import Path
from shutil import copyfile

from PyInstaller.compat import is_win

# 项目根目录
root = Path(SPECPATH)
application_icon = str(root / 'icon' / 'icon (00000).ico')

# 不将开发机已链接的热键文件路径和使用状态带入发布包。
config = json.loads((root / 'config.json').read_text(encoding='utf-8'))
config.setdefault('system', {}).update(initialized=False, theme='light', last_loaded='', link_path='')
default_config = Path(workpath) / 'config.json'
default_config.write_text(json.dumps(config, ensure_ascii=False, indent='\t'), encoding='utf-8')

# 需要包含的数据文件
datas = [
    (application_icon, 'icon'),
    (str(root / 'icon' / '*.png'), 'icon'),
    (str(root / 'styles'), 'styles'),
    (str(root / 'language' / '*.json'), 'language'),
    (str(default_config), '.'),
]

# 需要排除的模块（减小体积）
excluded_modules = [
    # 排除不必要的Qt模块
    'PySide6.Qt3DAnimation',
    'PySide6.Qt3DCore',
    'PySide6.Qt3DExtras',
    'PySide6.Qt3DInput',
    'PySide6.Qt3DLogic',
    'PySide6.Qt3DRender',
    'PySide6.QtBluetooth',
    'PySide6.QtCharts',
    'PySide6.QtDataVisualization',
    'PySide6.QtDBus',
    'PySide6.QtDesigner',
    'PySide6.QtHelp',
    'PySide6.QtLocation',
    'PySide6.QtMultimedia',
    'PySide6.QtMultimediaWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtNetworkAuth',
    'PySide6.QtNfc',
    'PySide6.QtOpenGL',
    'PySide6.QtOpenGLWidgets',
    'PySide6.QtPositioning',
    'PySide6.QtPrintSupport',
    'PySide6.QtQml',
    'PySide6.QtQuick',
    'PySide6.QtQuick3D',
    'PySide6.QtQuickWidgets',
    'PySide6.QtRemoteObjects',
    'PySide6.QtSensors',
    'PySide6.QtSerialPort',
    'PySide6.QtSpatialAudio',
    'PySide6.QtSql',
    'PySide6.QtStateMachine',
    'PySide6.QtSvg',
    'PySide6.QtSvgWidgets',
    'PySide6.QtTest',
    'PySide6.QtTextToSpeech',
    'PySide6.QtWebChannel',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineQuick',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebSockets',
    'PySide6.QtXml',
    # 排除测试相关模块
    'pytest',
    'unittest',
    'doctest',
    # 排除其他不必要的模块
    'numpy',
    'pandas',
    'matplotlib',
    'scipy',
    'PIL',
    'tkinter',
]

a = Analysis(
    [str(root / 'main.py')],
    pathex=[str(root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    noarchive=False,
)

pyz = PYZ(a.pure)

windows_version = None
if is_win:
    from PyInstaller.utils.win32 import versioninfo as vi

    version = config['metadata']['version'].lstrip('v')
    parts = tuple(int(part) for part in version.split('.'))
    file_version = parts + (0,) * (4 - len(parts))
    windows_version = vi.VSVersionInfo(
        ffi=vi.FixedFileInfo(filevers=file_version, prodvers=file_version),
        kids=[
            vi.StringFileInfo([vi.StringTable('040904B0', [
                vi.StringStruct('ProductName', 'Spine Hotkeys Editor'),
                vi.StringStruct('FileVersion', version),
                vi.StringStruct('ProductVersion', version),
            ])]),
            vi.VarFileInfo([vi.VarStruct('Translation', [0x0409, 1200])]),
        ],
    )

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Spine Hotkeys Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=application_icon,
    version=windows_version,
)

# 首次构建时提供可编辑的配置与翻译，后续构建保留已有文件。
dist = Path(DISTPATH)
if not (dist / 'config.json').exists():
    copyfile(default_config, dist / 'config.json')
for source in (root / 'language').glob('*.json'):
    destination = dist / 'language' / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        copyfile(source, destination)
