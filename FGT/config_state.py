"""setup_list.txt：固定行号 [0]注释 [1]ISSET [2]DEFAULT_PATH [3]DEFAULT_PATH_S"""
from __future__ import annotations

import re
from pathlib import Path

from FGT.paths import CONFIG_SETUP

SETUP_LINES = [
    "#配置文件",
    'ISSET="NO"',
    'DEFAULT_PATH="X:/FF"',
    'DEFAULT_PATH_S="X:/FF"',
]

_ISSET_LINE = re.compile(r'^\s*ISSET\s*=\s*"([^"]*)"\s*$', re.IGNORECASE)

# 向导点「开始」并写回配置后才创建；premain 以此判断是否跳过向导
INSTALL_OK = Path(CONFIG_SETUP).parent / "installed.ok"


def read_setup_file() -> str:
    return Path(CONFIG_SETUP).read_text(encoding="utf-8-sig")


def load_configuration() -> list[str]:
    ensure_setup_file()
    return read_setup_file().splitlines()


def save_configuration(lines: list[str]) -> None:
    Path(CONFIG_SETUP).write_text("\n".join(lines), encoding="utf-8")


def _parse_isset_line(line: str) -> str | None:
    m = _ISSET_LINE.match(line.strip())
    return m.group(1).strip().upper() if m else None


def read_isset() -> str:
    """从文件中查找 ISSET= 行（优先 [1]，否则扫描全文）。"""
    try:
        lines = read_setup_file().splitlines()
    except OSError:
        return "NO"
    if len(lines) >= 2:
        val = _parse_isset_line(lines[1])
        if val is not None:
            return val
    for line in lines:
        val = _parse_isset_line(line)
        if val is not None:
            return val
    return "NO"


def ensure_setup_file() -> None:
    path = Path(CONFIG_SETUP)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file() or path.stat().st_size == 0:
        save_configuration(list(SETUP_LINES))
        return
    lines = read_setup_file().splitlines()
    if len(lines) < 4 or _parse_isset_line(lines[1]) is None:
        save_configuration(list(SETUP_LINES))


def mark_setup_complete() -> None:
    """安装向导成功结束后调用（与 ISSET=\"YES\" 一起）。"""
    INSTALL_OK.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_OK.write_text("1\n", encoding="utf-8")


def is_configured() -> bool:
    """
    必须同时满足：
    1) installed.ok 存在（说明向导完整跑完并点了开始）
    2) ISSET 为 YES
    避免仅有旧的 setup_list.txt 里写着 YES 却跳过向导。
    """
    try:
        ensure_setup_file()
        if not INSTALL_OK.is_file():
            return False
        return read_isset() == "YES"
    except OSError:
        return False


def needs_setup() -> bool:
    return not is_configured()
