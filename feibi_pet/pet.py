"""
本包最核心的模块
桌宠实例
"""
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QTimer,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QWidget

from feibi_pet import config
from feibi_pet.Media import make_player
from feibi_pet.qt_transparent import apply_fully_transparent


class Pet(QWidget):
    idle_motion_finished = Signal()
    request_window_drag = Signal(str, QPoint)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        """初始化和其他包逻辑类似"""
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
        self.setMouseTracking(True)


        """状态配置"""
        self._busy = False
        self._sched: str | None = None
        self._dragging = False
        self._drop_prev = False

        """"静态图的配置static_picture"""
        self._spr = QLabel(self)
        self._spr.setFrameShape(QFrame.Shape.NoFrame)
        self._spr.setLineWidth(0)
        self._spr.setAutoFillBackground(False)
        self._spr.setStyleSheet("border:none;background:transparent;outline:none;")
        self._spr.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._spr.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self._spr.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        apply_fully_transparent(self._spr)

        """overlay覆盖层，默认不显示，留着后续的升级使用"""
        self._ov = QLabel(self)
        self._ov.hide()
        self._ov.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        apply_fully_transparent(self._ov)

        """配置静态图片"""
        self._pc_main = self._load_main(config.CHARACTER_MAIN)#可以用来过渡，先放张照片再启动视频，防止还没show就播放视频导致崩溃
        self._pc_bite = self._load_opt_file(config.CHARACTER_BITE)
        self._pc_hang = self._load_opt_file(config.CHARACTER_HANG)

        self._cw = max(1, self._pc_main.width())
        self._ch = max(1, self._pc_main.height())

        """设置简单动画"""
        self._motion: QSequentialAnimationGroup | None = None

        """单次定时器"""
        self._drag_vis_timer = QTimer(self)
        self._drag_vis_timer.setSingleShot(True)
        self._drag_vis_timer.timeout.connect(self._apply_window_drag_visual)

        """视频播放器配置"""
        self._clips = make_player(self)

        """统一设置透明底"""
        apply_fully_transparent(self)
        for child in self.findChildren(QWidget):
            apply_fully_transparent(child)

        """接受拖入路径"""
        self._dropped_paths:list[str]=[]
        """显示初始图"""
        self._apply(self._pc_main)

        #_idle是用来进入待机状态的，而singleShot则是用来等待app.exec()稳定后才执行这个待机状态
        QTimer.singleShot(0, self._idle)

    #状态传递
    def is_busy(self) -> bool:
        """返回状态信息"""
        return self._busy

    def begin_external_action(self, name: str) -> None:
        """开始新动作"""
        self._busy = True
        self._sched = name

    def set_dragging_visual(self, on: bool) -> None:
        """拎起角色的动态处理"""
        """其实可以理解成是拖动按帧处理，图片也按帧上传"""
        self._dragging = on
        if self._clips:
            self._clips.set_drag_dy(0)
        if on:
            self._drag_vis_timer.stop()
            self._drag_vis_timer.start(0)
        else:
            self._drag_vis_timer.stop()
            if self._drop_prev and self._pc_bite and not self._pc_bite.isNull():
                if self._clips:
                    self._clips.stop()
                self._apply(self._pc_bite)
                self._spr.raise_()
                self._spr.show()
            elif not self._busy:
                self._idle()
        #重新绘制
        self.update()

    def _apply_window_drag_visual(self) -> None:
        """显示拎起时的画面"""
        if not self._dragging:
            return
        #停止播放视频
        if self._clips:
            self._clips.stop()
        pc = (
            self._pc_hang
            if (self._pc_hang is not None and not self._pc_hang.isNull())
            else self._pc_main
        )
        self._apply(pc)
        self._spr.raise_()
        self._spr.show()
        self.update()

    """播放区，无需多言"""
    def play_sing(self) -> None:
        self._play_rand(config.CHARACTER_SING_CLIP)

    def play_sleep(self) -> None:
        self._play_rand(config.CHARACTER_SLEEP_CLIP)

    def play_sleep_2(self) -> None:
        self._play_rand(config.CHARACTER_SLEEP_2_CLIP)

    def play_wake(self) -> None:
        self._play_rand(config.CHARACTER_WAKE_CLIP)


    def play_bite(self) -> None:
        had_rand = self._sched is not None
        if self._clips:
            self._clips.stop()
        self._stop_pose_motion()
        if had_rand:
            self._busy = False
            self._sched = None
            self._spr.show()
            self._spr.move(0, 0)
            self.idle_motion_finished.emit()
        self._busy = True
        if self._pc_bite and not self._pc_bite.isNull():
            self._apply(self._pc_bite)
        else:
            self._apply(self._pc_main)
        geo = self._spr.geometry()
        g = QSequentialAnimationGroup(self)
        up = QPropertyAnimation(self._spr, b"pos", self)
        up.setDuration(120)
        up.setStartValue(geo.topLeft())
        up.setEndValue(QPoint(geo.x(), geo.y() + 10))
        up.setEasingCurve(QEasingCurve.Type.OutQuad)
        dn = QPropertyAnimation(self._spr, b"pos", self)
        dn.setDuration(120)
        dn.setStartValue(QPoint(geo.x(), geo.y() + 10))
        dn.setEndValue(geo.topLeft())
        dn.setEasingCurve(QEasingCurve.Type.InQuad)
        g.addAnimation(up)
        g.addAnimation(dn)
        g.addPause(100)
        g.addAnimation(up)
        g.addAnimation(dn)

        def done() -> None:
            self._busy = False
            self._motion = None
            self._idle()

        g.finished.connect(done)
        self._motion = g
        g.start()

    #随机函数配置
    def _play_rand(self, clip: Path) -> None:
        """播放随机视频"""
        if clip.is_file() and self._clips:
            self._stop_pose_motion()#停止待机循环
            self._clips.stop()#停播放
            self._spr.hide()#静态图层隐藏

            def after() -> None:
                """交给播放器结束后执行"""
                self._spr.show()
                self._done_sched()

            self._clips.play_once(clip, after)
            return
        self._spr.show()
        self._done_sched()

    def _done_sched(self) -> None:
        """统一收尾"""
        self._busy = False
        self._sched = None
        self._spr.move(0, 0)
        self._ov.hide()
        self._idle()
        self.idle_motion_finished.emit()

    def _user_stop_rand(self) -> None:
        """点击介入打断播放"""
        if self._busy and self._sched is None:
            return
        if self._sched is None:
            if self._clips and self._clips.is_once():
                self._clips.finish_once()
            return
        if self._clips and self._clips.is_once():
            self._clips.finish_once()
            return
        if self._clips:
            self._clips.stop()
        if self._motion:
            self._motion.blockSignals(True)
            self._motion.stop()
            self._motion.deleteLater()
            self._motion = None
        self._spr.show()
        self._spr.move(0, 0)
        self._ov.hide()
        self._done_sched()

    def _idle(self) -> None:
        """待机循环"""
        self._stop_pose_motion()
        p = config.CHARACTER_COMMON
        if self._clips and p.is_file():
            self._spr.hide()
            self._clips.play_loop(p)
        else:
            if self._clips:
                self._clips.stop()
            self._apply(self._pc_main)
            self._spr.show()

    def _stop_pose_motion(self) -> None:
        """停止待机"""
        if self._clips and not self._clips.is_once():
            self._clips.stop()
        if self._motion:
            self._motion.stop()
            self._motion.deleteLater()
            self._motion = None

    def _apply(self, pc: QPixmap) -> None:
        """设置图片的唯一入口"""
        pc = self._fill(pc)
        self._spr.show()
        self._spr.setPixmap(pc)
        self._spr.resize(self._cw, self._ch)
        self.resize(self._cw, self._ch)
        self._spr.move(0, 0)
        self._ov.setGeometry(self.rect())
        pw = self.parentWidget()
        if pw:
            pw.resize(self.width(), self.height())

    def _fill(self, pc: QPixmap) -> QPixmap:
        """第二次调节尺寸"""
        if pc.isNull():
            return pc
        sc = pc.scaled(
            self._cw,
            self._ch,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max(0, (sc.width() - self._cw) // 2)
        y = max(0, (sc.height() - self._ch) // 2)
        return sc.copy(x, y, self._cw, self._ch)

    def _fit(self, pc: QPixmap) -> QPixmap:
        """第一次调节尺寸"""
        if pc.isNull():
            return pc
        mw, mh = max(32, config.PET_MAX_W), max(32, config.PET_MAX_H)
        if pc.width() <= mw and pc.height() <= mh:
            return pc
        return pc.scaled(mw, mh, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    def _load_main(self, path: Path) -> QPixmap:
        if path.is_file():
            pc = QPixmap(str(path))
            if not pc.isNull():
                return self._fit(pc)
        return self._fit(self._placeholder())


    def _load_opt_file(self, path: Path) -> QPixmap | None:
        """加载可选图"""
        if path.is_file():
            pc = QPixmap(str(path))
            if not pc.isNull():
                return self._fit(pc)
        return None

    def _placeholder(self) -> QPixmap:
        """在图片缺失时使用，自动生成占位图"""
        w, h = 180, 220
        pc = QPixmap(w, h)
        pc.fill(Qt.GlobalColor.transparent)
        p = QPainter(pc)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor("#1a1a1a"))
        p.setBrush(QColor("#f5f0c4"))
        p.drawRoundedRect(8, 60, w - 16, h - 68, 18, 18)
        p.end()
        return pc

    """下面两个都是调节窗口大小的"""
    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._ov.setGeometry(self.rect())
        if self._clips:
            self._clips.layout()

    def paintEvent(self, e) -> None:
        super().paintEvent(e)



    """拖入文件函数区"""
    @staticmethod
    def _local_urls(ev) -> bool:
        """过滤拖入的信息，只能是本地文件路径"""
        for u in ev.mimeData().urls():
            if u.isLocalFile() and u.toLocalFile():
                return True
        return False


    def _hover_enter(self) -> None:
        if self._dragging or self._busy or self._drop_prev:
            return
        if not self._pc_bite or self._pc_bite.isNull():
            return
        if self._clips:
            self._clips.stop()
        self._drop_prev = True
        self._apply(self._pc_bite)
        self._spr.show()

    def _hover_leave(self) -> None:
        if not self._drop_prev:
            return
        self._drop_prev = False
        if not self._busy:
            self._idle()

    def dragEnterEvent(self, ev) -> None:
        self._user_stop_rand()
        if ev.mimeData().hasUrls() and self._local_urls(ev):
            self._hover_enter()
            ev.acceptProposedAction()
        else:
            ev.ignore()

    def dragMoveEvent(self, ev) -> None:
        self._user_stop_rand()
        if ev.mimeData().hasUrls() and self._local_urls(ev):
            self._hover_enter()
            ev.acceptProposedAction()
        else:
            ev.ignore()

    def dragLeaveEvent(self, ev) -> None:
        self._hover_leave()
        super().dragLeaveEvent(ev)

    def dropEvent(self, ev) -> None:
        """文件确定拖入时，"""
        if self._busy:
            ev.ignore()
            return
        paths = [u.toLocalFile() for u in ev.mimeData().urls() if u.toLocalFile()]

        if paths:
            self._drop_prev = False
            first = paths[0]
            self._dropped_paths = [first]
            config.INTERACT_TXT.write_text(
                f'DRAG_FILE="{first}"\nSHOW_MAIN=1\n',
                encoding="utf-8",
            )
            self.play_bite()
            ev.acceptProposedAction()
        else:
            self._hover_leave()
            ev.ignore()




    """鼠标绑定事件无需多言"""
    def mousePressEvent(self, ev) -> None:
        self._user_stop_rand()
        if ev.button() == Qt.MouseButton.LeftButton:
            top = self.window()
            if top is not None:
                top.raise_()
                top.activateWindow()
            self.request_window_drag.emit("press", ev.globalPosition().toPoint())
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev) -> None:
        if ev.buttons() & Qt.MouseButton.LeftButton:
            self.request_window_drag.emit("move", ev.globalPosition().toPoint())
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.request_window_drag.emit("release", ev.globalPosition().toPoint())
        super().mouseReleaseEvent(ev)
