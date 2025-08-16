# mycases_app.spec

# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # --- EDIT 1: Add all data folders ---
    # This copies your asset folders into the final application bundle.
    # The format is ('source_on_disk', 'destination_in_bundle').
    datas=[
        ('assets', 'assets'),
        ('fonts', 'fonts'),
        ('icons', 'icons'),
        ('styles', 'styles')
    ],
    # --- EDIT 2: Add hidden imports ---
    # Proactively tells PyInstaller about modules it might miss.
    hiddenimports=['reportlab.graphics.barcode'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mycases_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    # --- EDIT 3: Add the application icon ---
    # Make sure you have converted your PNG to an ICO file
    # and it is located at 'icons/app_icon.ico'.
    icon='icons\\app_icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas, # This line uses the 'datas' list we defined above.
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mycases_app',
)
