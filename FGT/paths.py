"""统一管理路径导入"""
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent


def p(*parts: str) -> Path:
    """在包根目录下拼路径，返回 pathlib.Path"""
    return PKG_DIR.joinpath(*parts)


def ps(*parts: str) -> str:
    """和 p() 一样拼路径，但返回 普通字符串"""
    return str(p(*parts))


def qt_url(*parts: str) -> str:
    """给 Qt样式返回路径字符串"""
    return p(*parts).resolve().as_posix()



#资源路径统一处理
UI_MAIN = ps("UI", "MAIN.ui")
UI_SETUP = ps("UI", "Setup.ui")
UI_WAIT = ps("UI", "WaitWindow.ui")
UI_ERROR = ps("UI", "ErrorWindow.ui")
UI_DETAIN = ps("UI", "DetainWindow.ui")
CONFIG_SETUP = ps("Configuration", "setup_list.txt")
SYSTEM_LOG = ps("logger", "system_log.txt")
FF_LOG = ps("logger", "ff_log.txt")
BUFFER_PHOTO = ps("buffer", "bufferphoto.jpg")
CONCAT_TARGET = ps("buffer", "concat_target.txt")
WIKI_AUDIO = ps("WIKI", "audio.txt")
WIKI_VIDEO = ps("WIKI", "video.txt")
APP_ICON = ps("picture", "Applcon.ico")
