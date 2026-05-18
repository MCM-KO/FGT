# 启动图形化界面
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from FGT import Graphic
from FGT.interact_watch import watch_interact
from FGT.paths import APP_ICON, INTERACT_TXT, PKG_DIR


def launch_main(app: QApplication | None = None) -> int:
    """由 premain 在安装向导结束后调用；勿在 import 时自动启动界面。"""
    if getattr(sys, "frozen", False):
        pet_cmd = [sys.executable, "--feibi-pet"]
        pet_cwd = str(Path(sys.executable).resolve().parent)
    else:
        project_root = Path(__file__).resolve().parent
        pet_cmd = [sys.executable, str(project_root / "main_feibi.py")]
        pet_cwd = str(project_root)

    pet = subprocess.Popen(
        pet_cmd,
        cwd=pet_cwd,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    os.chdir(PKG_DIR)
    if app is None:
        app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APP_ICON))

    w = Graphic.MainWindow(pet)
    w._interact_watch = watch_interact(INTERACT_TXT, w.apply_interact_drop, parent=w)
    w.ui.show()

    if QSystemTrayIcon.isSystemTrayAvailable():
        app.setQuitOnLastWindowClosed(False)
        tray = QSystemTrayIcon(QIcon(APP_ICON))
        tray.setToolTip("FGT")
        tray_menu = QMenu()
        act_show = QAction("显示主窗口")
        act_show.triggered.connect(w.show_main_window)
        act_quit = QAction("退出")
        act_quit.triggered.connect(w.Detain_show)
        tray_menu.addAction(act_show)
        tray_menu.addSeparator()
        tray_menu.addAction(act_quit)
        tray.setContextMenu(tray_menu)
        tray.activated.connect(
            lambda reason: w.show_main_window()
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )
        tray.show()
    else:
        print("系统托盘不可用，关闭窗口将直接退出程序。")

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(launch_main())
