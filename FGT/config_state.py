"""setup_list.txt：固定行号 [0]注释 [1]ISSET [2]DEFAULT_PATH [3]DEFAULT_PATH_S，用来读取和检查错误"""
from __future__ import annotations

import re
from pathlib import Path

from FGT.paths import CONFIG_SETUP

_PLACEHOLDER_PATHS = frozenset({"", "X:/FF", "X:/FF/"})

# 与 FGT/Configuration/setup_list.txt 一致，共 4 行
SETUP_LINES = [
    "#配置文件",
    'ISSET="NO"',
    'DEFAULT_PATH="X:/FF"',
    'DEFAULT_PATH_S="X:/FF"',
]


def read_setup_file() -> str:
    return Path(CONFIG_SETUP).read_text(encoding="utf-8-sig")


def load_configuration() -> list[str]:
    """读入配置文件；不足 4 行时先修复再返回（供 [1][2][3] 使用）"""
    ensure_setup_file()
    return read_setup_file().splitlines()


def save_configuration(lines: list[str]) -> None:
    Path(CONFIG_SETUP).write_text("\n".join(lines), encoding="utf-8")


def ensure_setup_file() -> None:
    """文件缺失、为空或行数不够时，写回标准 4 行"""
    path = Path(CONFIG_SETUP)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file() or path.stat().st_size == 0:
        save_configuration(list(SETUP_LINES))
        return
    lines = read_setup_file().splitlines()
    if len(lines) >= 4:
        return
    # 尽量保留已有行，再补齐到 4 行
    padded = list(SETUP_LINES)
    for i, line in enumerate(lines):
        if i < 4:
            padded[i] = line
    save_configuration(padded)


def read_isset() -> str:
    lines = load_configuration()
    m = re.search(r"\"(.*)\"", lines[1])
    return m.group(1).strip().upper() if m else "NO"


def needs_setup() -> bool:
    try:
        lines = load_configuration()
    except OSError:
        return True
    if read_isset() != "YES":
        return True
    for idx in (2, 3):
        m = re.search(r"\"(.*)\"", lines[idx])
        val = m.group(1).strip() if m else ""
        if val in _PLACEHOLDER_PATHS:
            return True
    return False
