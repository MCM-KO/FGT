"""本程序最终入口"""
import os
import sys

from PySide6.QtWidgets import QApplication

from FGT.config_state import ensure_setup_file, is_configured
from FGT.paths import PKG_DIR
from FGT import SetupGraphic


os.chdir(PKG_DIR)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--feibi-pet":
        from main_feibi import main as feibi_main

        feibi_main()
        sys.exit(0)

    ensure_setup_file()
    app = QApplication(sys.argv)

    if not is_configured():
        w = SetupGraphic.MainWindow()
        w.resize(400, 300)
        w.show()
        w.raise_()
        w.activateWindow()
        app.exec()
        w.deleteLater()
        if not is_configured():
            sys.exit(0)

    from main import launch_main

    raise SystemExit(launch_main(app))
