# -*- coding: utf-8 -*-
"""顶层/子控件统一透明背景（无系统底色、无填充）。"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget


def apply_fully_transparent(widget: QWidget) -> None:
    widget.setAutoFillBackground(False)
    widget.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
    widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    pal = widget.palette()
    clear = QColor(0, 0, 0, 0)
    for role in (
        QPalette.ColorRole.Window,
        QPalette.ColorRole.Base,
        QPalette.ColorRole.Button,
    ):
        pal.setColor(role, clear)
    widget.setPalette(pal)
    ss = (widget.styleSheet() or "").strip()
    if "transparent" not in ss:
        extra = "background:transparent;border:none;outline:none;"
        widget.setStyleSheet(f"{ss};{extra}" if ss else extra)
