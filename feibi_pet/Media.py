"""

配置媒体生成器

"""

import time

from collections.abc import Callable

from pathlib import Path



from PySide6.QtCore import QObject, Qt, QUrl

from PySide6.QtGui import QColor, QImage, QPixmap

from PySide6.QtMultimedia import QMediaPlayer, QVideoFrame, QVideoSink

from PySide6.QtWidgets import QLabel, QWidget



from feibi_pet import config

from feibi_pet.qt_transparent import apply_fully_transparent





def make_player(host: QWidget):
    """返回播放器对象，并与窗口绑定"""
    return ClipPlayer(host)





def _scale_fill(pm: QPixmap, w: int, h: int) -> QPixmap:
    if pm.isNull() or w < 1 or h < 1:
        return pm
    sc = pm.scaled(
        w,
        h,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = max(0, (sc.width() - w) // 2)
    y = max(0, (sc.height() - h) // 2)
    return sc.copy(x, y, w, h)





def _chroma_key_image(img: QImage, key: tuple[int, int, int], tol: int) -> QImage:
    out = img.convertToFormat(QImage.Format.Format_ARGB32)
    kr, kg, kb = key
    w, h = out.width(), out.height()
    for y in range(h):
        for x in range(w):
            c = QColor(out.pixel(x, y))
            if (
                abs(c.red() - kr) <= tol
                and abs(c.green() - kg) <= tol
                and abs(c.blue() - kb) <= tol
            ):
                out.setPixelColor(x, y, QColor(0, 0, 0, 0))
    return out





def _frame_to_pixmap(frame: QVideoFrame) -> QPixmap | None:
    if not frame.isValid():
        return None
    mapped = frame.map(QVideoFrame.MapMode.ReadOnly)

    if not mapped:
        return None

    try:
        img = frame.toImage()

    finally:
        frame.unmap()

    if img.isNull():
        return None

    if img.format() not in (
        QImage.Format.Format_ARGB32,
        QImage.Format.Format_ARGB32_Premultiplied,
    ):
        img = img.convertToFormat(QImage.Format.Format_ARGB32)
    key = getattr(config, "VIDEO_KEY_RGB", None)
    tol = int(getattr(config, "VIDEO_KEY_TOL", 0) or 0)
    if key is not None and tol >= 0:
        img = _chroma_key_image(img, key, tol)
    return QPixmap.fromImage(img)





class ClipPlayer(QObject):
    def __init__(self, host: QWidget) -> None:
        super().__init__(host)#父子绑定可以同时销毁
        self._host = host
        self._player = QMediaPlayer(self)#设置播放器
        self._player.setAudioOutput(None)#禁止视频输出声音，为自定义语音提供选择
        self._player.mediaStatusChanged.connect(self._on_status)
        self.next_step: Callable[[], None] | None = None#控制下一步该调用的方法，模拟队列



        """下级控件：QVideoSink + QLabel（QVideoWidget 在 Windows 上会丢掉透明通道显示黑底）"""
        self._lbl = QLabel(host)
        self._lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)#设置鼠标穿透事件
        apply_fully_transparent(self._lbl)
        self._sink = QVideoSink(self)
        self._sink.videoFrameChanged.connect(self._on_video_frame)
        self._player.setVideoOutput(self._sink)
        fps = float(getattr(config, "VIDEO_TARGET_FPS", 30.0) or 30.0)
        self._min_frame_ms = max(1, int(1000.0 / fps)) if fps > 0 else 1
        self._last_frame_ms = 0.0
        #先降低显示（初始化视频播放区）
        self._lbl.hide()
        self._lbl.lower()



    def set_drag_dy(self, _dy: int) -> None:
        pass



    def layout(self) -> None:
        """设置布局"""
        r = self._host.rect()#返回四维对象，x/y/w/h
        self._lbl.setGeometry(r)#进行大小设置



    def _on_video_frame(self, frame: QVideoFrame) -> None:
        now = time.monotonic() * 1000.0
        if now - self._last_frame_ms < self._min_frame_ms:
            return
        self._last_frame_ms = now
        pm = _frame_to_pixmap(frame)
        if pm is None or pm.isNull():
            return
        r = self._host.rect()
        if r.width() > 0 and r.height() > 0:
            pm = _scale_fill(pm, r.width(), r.height())
        self._lbl.setPixmap(pm)



    def play_loop(self, path: Path) -> None:
        """无限播放视频资源"""
        self.next_step = None
        self._player.stop()
        self._player.setLoops(QMediaPlayer.Loops.Infinite)
        self._player.setSource(QUrl.fromLocalFile(str(path.resolve())))
        self.layout()
        self._lbl.show()
        self._lbl.lower()
        self._player.play()
        """无限播放的切断只能由随机事件或者主动点击来切断"""



    def play_once(self, path: Path, on_end: Callable[[], None]) -> None:
        """一次性播放"""
        self._player.stop()
        self.next_step = on_end
        self._player.setLoops(QMediaPlayer.Loops.Once)
        self._player.setSource(QUrl.fromLocalFile(str(path.resolve())))
        self.layout()
        self._lbl.show()
        self._lbl.lower()
        self._player.play()



    def stop(self) -> None:
        self.next_step = None
        self._player.stop()
        self._lbl.hide()
        self._lbl.clear()



    def is_once(self) -> bool:
        return self.next_step is not None



    def finish_once(self) -> None:
        if self.next_step is None:
            return
        step = self.next_step
        self.next_step = None
        self._player.stop()
        self._lbl.hide()
        self._lbl.clear()
        step()



    def _on_status(self, status: QMediaPlayer.MediaStatus) -> None:
        """遍历媒体槽，当状态符合要求，回调，否则继续执行"""
        if self.next_step is None:
            return
        if status != QMediaPlayer.MediaStatus.EndOfMedia:
            return
        step = self.next_step
        self.next_step = None
        self._player.stop()
        self._lbl.hide()
        self._lbl.clear()
        step()