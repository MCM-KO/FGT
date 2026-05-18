import os
import sys
import warnings
from pathlib import Path

try:
    _FEIBI_ROOT = Path(__file__).resolve().parent
except NameError:
    _FEIBI_ROOT = Path.cwd()


def main() -> None:
    """过滤掉多余输出信息 """
    os.environ.setdefault(
        "QT_LOGGING_RULES",
        "*.debug=false;*.info=false;qt.qpa.*=false;qt.multimedia.*=false",
    )
    warnings.filterwarnings("ignore")

    from PySide6.QtCore import QCoreApplication, QTimer, Qt
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtWidgets import QApplication

    if sys.platform == "win32" and os.environ.get("FEIBI_SOFTWARE_OPENGL", "1").strip() != "0":
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    from feibi_pet.window import FeibiPetWindow

    win = FeibiPetWindow()
    geo = QGuiApplication.primaryScreen().availableGeometry()
    win.move(geo.right() - win.width() - 48, geo.bottom() - win.height() - 48)
    win.show()

    def _bring_to_front() -> None:
        win.raise_()
        win.activateWindow()

    QTimer.singleShot(0, _bring_to_front)
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
