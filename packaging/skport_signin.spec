# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import os

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


project_root = Path(SPEC).resolve().parents[1]
build_mode = os.environ.get("SKPORT_SIGNIN_PYINSTALLER_MODE", "onedir")

datas = [
    (str(project_root / "config" / "settings.example.json"), "config"),
    (str(project_root / "register_logon_task.ps1"), "."),
]
datas += collect_data_files("playwright")
datas += collect_data_files("tzdata")

hiddenimports = collect_submodules("playwright")
hiddenimports += collect_submodules("greenlet")

a = Analysis(
    [str(project_root / "skport_signin" / "__main__.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

if build_mode == "onefile":
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name="skport_signin",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=True,
        disable_windowed_traceback=False,
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="skport_signin",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=True,
        disable_windowed_traceback=False,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name="skport_signin",
    )
