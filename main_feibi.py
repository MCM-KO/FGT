"""
===============================================================================
程序入口：启动菲比（《鸣潮》角色）桌面宠物
===============================================================================

一、运行前自检清单（建议按顺序核对）
-------------------------------------------------------------------------------
1. Python 版本：建议 3.11～3.13（PyQt6 在 Windows 上最稳）；若用 3.14 请优先用终端运行排查。
2. 依赖安装：在项目根目录执行 ``pip install -r requirements.txt``，
   其中核心是 ``PyQt6``，用于 GUI、透明窗口、拖放、定时器。
   **PyCharm 调试**若报 ``DLL load failed`` / ``找不到指定的程序``（导入 ``QtGui`` 时），
   或 ``ValueError: Unexpected qt support mode: none``：不要用环境变量 ``PYDEVD_PYQT_MODE=none``
   （当前 PyCharm 自带的 pydev 会因此直接崩溃）。请打开 **设置 → Python → Debugger**，
   **取消勾选「PyQt compatible」**（官方说明：未在代码里导入 PyQt 时反选可消除相关导入错误），
   保存后重新 Debug。平常也可用终端 ``python main.py`` 或 **运行（Shift+F10）** 验证。
3. **主图文件位置（最重要）**：
   常态立绘必须放在包内目录：

       feibi_pet/picture/feibi_main.png

   立绘与视频路径在 ``feibi_pet/config.py`` 中按 ``Path`` 配置（默认在 ``feibi_pet/picture`` 下）。
   窗口尺寸以主图为基准；常态循环由 ``FEIBI_COMMON`` 指定，
   无该视频时待机显示主图。
4. 随机片段：同目录 ``feibi_sing`` / ``feibi_sleep`` / ``feibi_wake``（.mov / .mp4）；无视频时用静态图。
5. 启动方式：在**项目根目录**执行 ``python main.py``（保证 ``import feibi_pet`` 能解析）。

二、本文件刻意保持「薄」
-------------------------------------------------------------------------------
``main`` 里不写业务：只创建 ``QApplication``、``FeibiPetWindow``、设定初始屏幕位置。
这样你以后加「托盘图标 / 单实例锁 / 日志」等，都集中改这里即可。

三、退出码
-------------------------------------------------------------------------------
使用 ``raise SystemExit(app.exec())`` 把 Qt 事件循环的返回值交给操作系统，
便于将来在脚本或 CI 里判断是否正常退出。

若进程以 ``0xC000041D``（十进制约 -1073740771）等码静默退出且无 Python 栈，
多为 **Qt / 多媒体在本机代码里崩溃**；请看控制台分阶段输出与 ``feibi_startup.log``。
"""

import sys
from pathlib import Path

try:
    _FEIBI_ROOT = Path(__file__).resolve().parent
except NameError:  # pragma: no cover
    _FEIBI_ROOT = Path.cwd()


def main() -> None:
    import os
    import warnings
    os.environ.setdefault(
        "QT_LOGGING_RULES",
        "*.debug=false;*.info=false;qt.qpa.*=false;qt.multimedia.*=false",
    )
    warnings.filterwarnings("ignore")

    # _feibi_log("导入 PyQt6 …")
    from PySide6.QtCore import QCoreApplication, Qt
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtWidgets import QApplication

    #尽量使用openGL来规避实现图形化进程卡死
    if sys.platform == "win32" and os.environ.get("FEIBI_SOFTWARE_OPENGL", "1").strip() != "0":
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")#跨平台统一外观

    from feibi_pet.window import FeibiPetWindow

    win = FeibiPetWindow()

    geo = QGuiApplication.primaryScreen().availableGeometry()
    win.move(geo.right() - win.width() - 48, geo.bottom() - win.height() - 48)
    win.show()

    from PySide6.QtCore import QTimer

    """置顶激活窗口"""
    def _bring_to_front() -> None:
        win.raise_()
        win.activateWindow()

    """和之前那个一样的道理等待循环安全再置顶"""
    QTimer.singleShot(0, _bring_to_front)

    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
