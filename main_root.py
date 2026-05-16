"""
main的测试版本
程序的测试入口，仅限开发者使用
"""
import sys
from pathlib import Path

from PySide6.QtCore import QtMsgType, qInstallMessageHandler

try:
    _FEIBI_ROOT = Path(__file__).resolve().parent
except NameError:  # pragma: no cover
    _FEIBI_ROOT = Path.cwd()


def _feibi_log(msg: str) -> None:
    line = f"[feibi] {msg}\n"
    try:
        sys.stderr.write(line)
        sys.stderr.flush()
    except OSError:
        pass
    try:
        p = _FEIBI_ROOT / "feibi_startup.log"
        prev = p.read_text(encoding="utf-8") if p.is_file() else ""
        p.write_text(prev + line, encoding="utf-8")
    except OSError:
        pass


def _install_diagnostics() -> None:
    """仅测试开发时使用，用于监控程序，追溯报错原因"""
    import atexit
    import faulthandler
    import traceback
    import threading

    log_path = _FEIBI_ROOT / "feibi_startup.log"
    try:
        _diag_log_fp = open(log_path, "a", encoding="utf-8")
        faulthandler.enable(file=_diag_log_fp, all_threads=True)
        atexit.register(_diag_log_fp.close)
    except OSError:
        faulthandler.enable(all_threads=True)

    def _excepthook(exc_type, exc, tb) -> None:
        _feibi_log(f"未捕获异常: {exc_type.__name__}: {exc}")
        try:
            traceback.print_exception(exc_type, exc, tb, file=sys.stderr)
        except OSError:
            pass

    sys.excepthook = _excepthook

    def _thread_hook(args: threading.ExceptHookArgs) -> None:
        _feibi_log(f"线程内未捕获异常: {args.exc_type!r}: {args.exc_value}")
        if args.exc_type is not None and args.exc_traceback is not None:
            try:
                traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback, file=sys.stderr)
            except OSError:
                pass

    threading.excepthook = _thread_hook

    def _on_exit() -> None:
        _feibi_log("atexit：进程即将退出（若为异常结束，上面应有栈或本机崩溃码）")

    atexit.register(_on_exit)


def main() -> None:
    import os
    import warnings

    _feibi_log("开始启动（若随后静默崩溃，请查看本段之后最后一条日志定位阶段）")

    os.environ.setdefault(
        "QT_LOGGING_RULES",
        "*.debug=false;*.info=false;qt.qpa.*=false;qt.multimedia.*=false",
    )
    warnings.filterwarnings("ignore")

    _feibi_log("导入 PyQt6 …")
    from PySide6.QtCore import QCoreApplication, Qt
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtWidgets import QApplication

    # 透明桌宠 + 多媒体在部分显卡驱动上于首次合成时本机崩溃；软件 OpenGL 常可规避。
    if sys.platform == "win32" and os.environ.get("FEIBI_SOFTWARE_OPENGL", "1").strip() != "0":
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)
        _feibi_log("已启用 AA_UseSoftwareOpenGL（环境变量 FEIBI_SOFTWARE_OPENGL=0 可关闭）")

    def _qt_log(mode: QtMsgType, _ctx, msg: str) -> None:
        if mode in (
            QtMsgType.QtWarningMsg,
            QtMsgType.QtCriticalMsg,
            QtMsgType.QtFatalMsg,
            QtMsgType.QtSystemMsg,
        ):
            _feibi_log(f"Qt: {getattr(mode, 'name', str(mode))} {msg}")

    qInstallMessageHandler(_qt_log)

    _feibi_log("创建 QApplication …")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    _feibi_log("导入并创建 FeibiPetWindow …")
    from feibi_pet.window import FeibiPetWindow

    win = FeibiPetWindow()

    _feibi_log("计算屏幕位置 …")
    geo = QGuiApplication.primaryScreen().availableGeometry()
    win.move(geo.right() - win.width() - 48, geo.bottom() - win.height() - 48)
    _feibi_log("调用 win.show() …")
    win.show()
    _feibi_log("win.show() 已返回；推迟 raise_/activate 到下一事件，避免 0xC000041D")

    from PySide6.QtCore import QTimer

    def _bring_to_front() -> None:
        win.raise_()
        win.activateWindow()
        _feibi_log("已执行 raise_/activateWindow（延迟）")

    QTimer.singleShot(0, _bring_to_front)

    _feibi_log("进入事件循环 app.exec() …")
    raise SystemExit(app.exec())


if __name__ == "__main__":
    _install_diagnostics()
    main()
    try:
        main()
    except BaseException:
        import traceback

        traceback.print_exc()
        sys.stderr.flush()
        raise

