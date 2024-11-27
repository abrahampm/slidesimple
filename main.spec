# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Include all data and modules from PySide6
datas = collect_data_files('PySide6')

# Include libopenslide
import os
import openslide_bin
openslide_bin_dir = os.path.dirname(openslide_bin.__file__)

# Detect libopenslide path
libopenslide_path = None
if os.name == 'nt':
    #Windows
    libopenslide_path = os.path.join(openslide_bin_dir, "libopenslide-1.dll")
    datas += [(libopenslide_path, "static/openslide-win64/bin/")]
elif os.name == 'posix':
    if os.uname().sysname == 'Darwin':
       #macOS
       libopenslide_path = os.path.join(openslide_bin_dir, "libopenslide.1.dylib")
       datas += [(libopenslide_path, "static/")]
    elif os.uname().sysname == 'Linux':
       #Linux
       libopenslide_path = os.path.join(openslide_bin_dir, "libopenslide.so.1")
       datas += [(libopenslide_path, "static/")]

assert libopenslide_path is not None and os.path.exists(libopenslide_path)


# Include additional data files if needed
datas += [
    ('main.qml', '.'),
    ('resources', 'resources'),
    ('qml', 'qml'),
]

hiddenimports = collect_submodules('PySide6')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SlideSimple',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
