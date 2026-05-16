#初始化总入口,用于首次安装时,真正的主入口
import os
import re
import sys
from PySide6.QtWidgets import QApplication

from FGT.paths import CONFIG_SETUP, PKG_DIR
import FGT.SetupGraphic as SetupGraphic

os.chdir(PKG_DIR)

if __name__ == '__main__':
    with open(CONFIG_SETUP, "r", encoding="utf-8") as f:
        lines=f.readlines()
        ISSET=re.search("\"(.*)\"",lines[1]).group(1)
        if ISSET=="NO":
            app=QApplication(sys.argv)
            w= SetupGraphic.MainWindow()
            w.resize(400,300)#设置初始化大小
            w.show()
            app.exec()
        elif ISSET=="YES":
            pass

