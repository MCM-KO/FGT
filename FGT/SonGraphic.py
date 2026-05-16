from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QPlainTextEdit, QWidget
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog
import sys
from PySide6.QtCore import QFile, QObject, Qt, QThread, Signal, QEvent
from PySide6.QtUiTools import QUiLoader

from FGT.paths import UI_DETAIN, UI_ERROR, UI_WAIT, ps, qt_url



"""用于构建独立子窗口的模块
   包含独立的等待进程和抛错进程等"""


#核心子窗口
class WaitWindow(QMainWindow):
    setpercentage=Signal(int)
    delete_me=Signal()
    set_label=Signal(str)
    set_button=Signal(str)


    def closeEvent(self,event):
        for t in self.PP:
            t.terminate()
        event.accept()

    def __init__(self):
        super().__init__()
        self.ui=QUiLoader().load(UI_WAIT)
        self.setpercentage.connect(self.ui.percentage.setValue)
        #设置中心权限
        self.setCentralWidget(self.ui)
        #配置独立进程池
        self.PP=[]
        #信号绑定
        self.delete_me.connect(self.Delete_me)
        self.set_label.connect(self.ui.titleLabel.setText)
        self.set_button.connect(self.ui.cancelButton.setText)
        #方法绑定
        self.ui.cancelButton.clicked.connect(self.delete_me.emit)

    def Delete_me(self):
        self.close()
        self.deleteLater()#等app循环安全时再彻底销毁


class ErrorWindow(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.ui=QUiLoader().load(UI_ERROR)



#配置子窗口
class DetainWindow(QMainWindow):
    #因其按钮的选择与父窗口的状态有关，所以其关于按钮选择的方法列在其父窗口中
    def __init__(self):
        super().__init__()
        self.ui=QUiLoader().load(UI_DETAIN)
        self.pmap={}


        #设置背景
        self.ui.setStyleSheet(f"QMainWindow {{border-image: url({qt_url('picture', 'feibis.png')});}}")
        self.ui.setWindowTitle("非比啾比——————")
        #禁用放大键关闭键等

        self.ui.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint
        )
        #配置图片路径
        self.pmap[0]=ps("picture", "feibi_wait.jpg")
        self.pmap[1]=ps("picture", "feibi_cry.jpg")
        self.pmap[2]=ps("picture", "feibi_smile.jpg")

        #默认显示
        self.Default_picture()

        self.ui.Cancel.installEventFilter(self)
        self.ui.Delete.installEventFilter(self)

    def Default_picture(self):
        #设置默认路径
        self.ui.dafeizhu.setScaledContents(True)
        self.ui.dafeizhu.setPixmap(QPixmap(self.pmap[0]))

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Enter:

            if obj == self.ui.Cancel:
                self.ui.dafeizhu.setPixmap(QPixmap(self.pmap[2]))

            elif obj == self.ui.Delete:
                self.ui.dafeizhu.setPixmap(QPixmap(self.pmap[1]))

        elif event.type() == QEvent.Leave:
            self.Default_picture()

        return super().eventFilter(obj, event)
