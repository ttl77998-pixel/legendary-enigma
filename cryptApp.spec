# CryptFile.spec


# ➜ Build comand :
#    pyinstaller cryptApp.spec

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

try:
    from PyInstaller.utils.hooks import collect_dynamic_libs
    _has_collect_dynamic_libs = True
except Exception:
    _has_collect_dynamic_libs = False

# Take all the modules of tkinterdnd2
tkdnd_datas = collect_data_files("tkinterdnd2", include_py_files=True)
hiddenimports = collect_submodules("tkinterdnd2")
if _has_collect_dynamic_libs:
    tkdnd_bins = collect_dynamic_libs("tkinterdnd2")
else:
    tkdnd_bins = []

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=tkdnd_bins,
    datas=tkdnd_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="CryptFile",
    icon="lock.ico",          
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,            
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Onefile version. If you prefer "onedir", comment COLLECT .
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="CryptFile",
)

# OneFile:
# exe = EXE(
#     pyz,
#     a.scripts,
#     [],
#     exclude_binaries=True,
#     name="CryptFile",
#     icon="lock.ico",
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     console=False,
# )
# app = BUNDLE(exe, name="CryptFile.app")  # macOS 
