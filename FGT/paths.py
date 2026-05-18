"""统一管理路径导入"""
import shutil
import sys
from pathlib import Path


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


if _is_frozen():
    BUNDLE_ROOT = Path(sys._MEIPASS)
    PKG_DIR = BUNDLE_ROOT / "FGT"
    APP_DIR = Path(sys.executable).resolve().parent
    PROJECT_ROOT = APP_DIR
else:
    BUNDLE_ROOT = None
    PKG_DIR = Path(__file__).resolve().parent
    APP_DIR = PKG_DIR
    PROJECT_ROOT = PKG_DIR.parent


def p(*parts: str) -> Path:
    """在包根目录下拼路径，返回 pathlib.Path"""
    return PKG_DIR.joinpath(*parts)


def ps(*parts: str) -> str:
    """和 p() 一样拼路径，但返回 普通字符串"""
    return str(p(*parts))


def _writable(*rel_parts: str, bundle_parts: tuple[str, ...] | None = None) -> str:
    """打包后写入 exe 同目录；开发态仍写在 FGT 包内"""
    if not _is_frozen():
        return ps(*rel_parts)
    dest = APP_DIR.joinpath(*rel_parts)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if bundle_parts is not None:
        src = PKG_DIR.joinpath(*bundle_parts)
        if not dest.exists() and src.is_file():
            shutil.copy2(src, dest)
    return str(dest)


def _interact_txt() -> Path:
    if not _is_frozen():
        return PROJECT_ROOT / "Interact.txt"
    dest = APP_DIR / "Interact.txt"
    src = BUNDLE_ROOT / "Interact.txt"
    if not dest.exists() and src.is_file():
        shutil.copy2(src, dest)
    return dest


def qt_url(*parts: str) -> str:
    """给 Qt样式返回路径字符串"""
    return p(*parts).resolve().as_posix()


# 资源路径（只读，始终来自包内）
UI_MAIN = ps("UI", "MAIN.ui")
UI_SETUP = ps("UI", "Setup.ui")
UI_WAIT = ps("UI", "WaitWindow.ui")
UI_ERROR = ps("UI", "ErrorWindow.ui")
UI_DETAIN = ps("UI", "DetainWindow.ui")
UI_LOG = ps("UI", "LogWindow.ui")
WIKI_AUDIO = ps("WIKI", "audio.txt")
WIKI_VIDEO = ps("WIKI", "video.txt")
APP_ICON = ps("picture", "Applcon.ico")

# 运行时会改写的路径（打包后落在 exe 旁）
CONFIG_SETUP = _writable(
    "Configuration", "setup_list.txt",
    bundle_parts=("Configuration", "setup_list.txt"),
)
SYSTEM_LOG = _writable("logger", "system_log.txt", bundle_parts=("logger", "system_log.txt"))
FF_LOG = _writable("logger", "ff_log.txt", bundle_parts=("logger", "ff_log.txt"))
BUFFER_PHOTO = _writable("buffer", "bufferphoto.jpg", bundle_parts=("buffer", "bufferphoto.jpg"))
CONCAT_TARGET = _writable("buffer", "concat_target.txt", bundle_parts=("buffer", "concat_target.txt"))
INTERACT_TXT = _interact_txt()
