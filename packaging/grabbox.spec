# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for GrabBox. Build one binary per OS:
#   pyinstaller packaging/grabbox.spec
# The web UI is bundled next to the executable, not inside it, so the server can
# still hot-serve style/app updates without a rebuild.

import os

block_cipher = None

# SPEC lives in <repo>/packaging/, so the repo root is one level up.
HERE = os.path.abspath(os.path.dirname(os.path.dirname(SPEC)))
WEB = os.path.join(HERE, "grabbox", "web")

a = Analysis(
    [os.path.join(HERE, "launch.py")],
    pathex=[HERE],
    binaries=[],
    datas=[(WEB, os.path.join("grabbox", "web"))],
    hiddenimports=["yt_dlp", "yt_dlp.extractor", "yt_dlp.postprocessor"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "scipy", "pandas"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GrabBox",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(HERE, "extension", "icons", "icon-128.png"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GrabBox",
)
