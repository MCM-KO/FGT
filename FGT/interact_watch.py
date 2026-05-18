"""监视项目根目录 Interact.txt，当其目标变更时回调"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QObject, QFileSystemWatcher


def read_drag_paths(interact_path: str | Path) -> list[str]:
    path = Path(interact_path)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("DRAG_FILE="):
            continue
        val = line.split("=", 1)[1].strip().strip('"').strip("'")
        if not val:
            return []




        parts = [p for p in val.split("|") if p]
        return [parts[0]] if parts else []
    return []


def watch_interact(
    path: str | Path,
    on_changed: Callable[[], None],
    *,
    parent: QObject | None = None,
) -> QFileSystemWatcher:
    p = Path(path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text('DRAG_FILE=""\n', encoding="utf-8")

    path_str = str(p)
    fs = QFileSystemWatcher(parent)

    def _on(changed_path: str) -> None:
        if changed_path != path_str:
            return
        if path_str not in fs.files():
            fs.addPath(path_str)
        on_changed()

    fs.fileChanged.connect(_on)
    fs.addPath(path_str)
    return fs
