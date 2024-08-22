# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],  # Cambia esta ruta al directorio de tu proyecto
    binaries=[],
    datas=[
        ('resources/*', 'resources'),  # Incluye todos los archivos dentro de la carpeta `resources`
        ('clone-dashboard_ui.py', '.'),
        ('uart_manager.py', '.'),
        ('clone-dashboard.ui', '.'),       # Incluye `dashboardUI.ui` en el directorio raíz del ejecutable
        ('resources_rc.py', '.'),      # Incluye `resources_rc.py` en el directorio raíz del ejecutable
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
)
