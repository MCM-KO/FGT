"""无边框顶层窗：装PET对象"""
import sys

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPalette, QShowEvent
from PySide6.QtWidgets import QWidget

from feibi_pet import config
from feibi_pet.pet import Pet
from feibi_pet.qt_transparent import apply_fully_transparent
from feibi_pet.RandomScheduler import RandTimer, default_acts

_WM_MOUSEACTIVATE = 0x0021#鼠标激活配置
_MA_ACTIVATE = 1#激活窗口并正常传递信号定义


class FeibiPetWindow(QWidget):
    def __init__(self) -> None:
        """拉取配置进行初始化"""
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        if config.ON_TOP:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        super().__init__(None, flags)#初始化窗口

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setStyleSheet("QWidget{border:none;outline:none;background:transparent;}")
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        self.setPalette(pal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAcceptDrops(True)
        apply_fully_transparent(self)

        self._drag_anchor: QPoint | None = None#计算拖动位置
        self._drag_mouse_grabbed = False#标记是否已经位于顶层窗口

        self._pet = Pet(self)
        self._pet.move(0, 0)
        self._pet.request_window_drag.connect(self._on_drag)#将宠物的拖动与窗口的拖动绑定

        """配置随机器"""
        self._sched = RandTimer(
            self._pet,
            tick_ms=config.RANDOM_TICK_MS,
            chance=config.RANDOM_CHANCE,
            cooldown_ms=config.RANDOM_COOLDOWN_MS,
            acts=default_acts(),
        )
        self._pet.idle_motion_finished.connect(self._sched.mark_done)
        self._sched.start()
        self.resize(self._pet.size())
        apply_fully_transparent(self._pet)
        for child in self._pet.findChildren(QWidget):
            apply_fully_transparent(child)

    def showEvent(self, event: QShowEvent) -> None:
        """窗口显示构参，把事件交给qt"""
        super().showEvent(event)

    def nativeEvent(self, eventType, message):
        """
        激活窗口且不会把本次鼠标信号吞掉
        也就是处理信号事件的
        """
        #处理平台兼容的问题
        if sys.platform == "win32":
            try:
                et = bytes(eventType)
            except (TypeError, ValueError, AttributeError):
                try:
                    et = eventType.data()
                except Exception:
                    et = b""
            if et == b"windows_generic_MSG" and message:
                try:
                    import ctypes
                    from ctypes import wintypes

                    msg = ctypes.cast(int(message), ctypes.POINTER(wintypes.MSG)).contents
                    if msg.message == _WM_MOUSEACTIVATE:
                        return True, _MA_ACTIVATE
                except (OSError, ValueError, ctypes.ArgumentError):
                    pass
        return super().nativeEvent(eventType, message)

    def _grab_for_window_drag(self) -> None:
        """绑定鼠标捕获"""
        if self._drag_mouse_grabbed:
            return
        self.grabMouse()
        self._drag_mouse_grabbed = True

    def _release_window_drag_grab(self) -> None:
        """绑定鼠标释放"""
        if not self._drag_mouse_grabbed:
            return
        self.releaseMouse()
        self._drag_mouse_grabbed = False

    def _on_drag(self, phase: str, gp: QPoint) -> None:
        """将拖动信号上传最高控件"""
        if phase == "press":
            self._drag_anchor = gp - self.frameGeometry().topLeft()
            self._pet.set_dragging_visual(True)
            # 在顶层窗抓取鼠标：避免子控件（视频层）在拖动开始被 hide 后丢失捕获，导致必须连点两下。
            self._grab_for_window_drag()
        elif phase == "move" and self._drag_anchor is not None:
            self.move(gp - self._drag_anchor)
        elif phase == "release":
            self._release_window_drag_grab()
            self._drag_anchor = None
            self._pet.set_dragging_visual(False)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.raise_()
            self.activateWindow()
            self._drag_anchor = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._pet.set_dragging_visual(True)
            self._grab_for_window_drag()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """鼠标移动"""
        if self._drag_anchor is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_anchor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """鼠标释放"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._release_window_drag_grab()
            self._drag_anchor = None
            self._pet.set_dragging_visual(False)
        super().mouseReleaseEvent(event)
