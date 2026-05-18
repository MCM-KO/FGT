"""打包文件"""
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# 运行期资源（与 FGT/paths.py、feibi_pet/config.py 路径一致）
datas = [
    ("FGT/UI", "FGT/UI"),
    ("FGT/picture", "FGT/picture"),
    ("FGT/Configuration", "FGT/Configuration"),
    ("FGT/WIKI", "FGT/WIKI"),
    ("FGT/logger", "FGT/logger"),
    ("FGT/buffer", "FGT/buffer"),
    ("feibi_pet/picture", "feibi_pet/picture"),
    ("Interact.txt", "."),
    ("LICENSE.txt", "."),
]

hiddenimports = [
    "PySide6.QtUiTools",
    "numpy",
    "cv2",
    "main",
    "main_feibi",
    "premain",
    "FGT.config_state",
] + collect_submodules("FGT") + collect_submodules("feibi_pet") + collect_submodules("PySide6")

binaries = []
cv2_datas, cv2_binaries, cv2_hidden = collect_all("cv2")
datas += cv2_datas
binaries += cv2_binaries
hiddenimports += cv2_hidden

a = Analysis(
    ["premain.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["try", "main_root"],
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
    name="FGT",
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
    icon=["FGT\\picture\\Applcon.ico"],
)
