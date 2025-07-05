# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['harmony.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Filter out OpenSSL libraries to avoid version conflicts
# Keep Python's SSL module but exclude the binary libraries
a.binaries = [x for x in a.binaries if not (
    x[0].startswith('libssl') or 
    x[0].startswith('libcrypto') or
    'libssl.so' in x[0] or 
    'libcrypto.so' in x[0]
)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='harmony',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)