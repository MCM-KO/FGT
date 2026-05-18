from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QPixmap, QPalette, QBrush, QMovie
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QPlainTextEdit, QWidget
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog
import sys
from PySide6.QtCore import QFile, QObject, Qt, QThread, Signal, QEvent
from PySide6.QtUiTools import QUiLoader

from FGT.paths import UI_DETAIN, UI_ERROR, UI_LOG, UI_WAIT, ps, qt_url



"""用于构建独立子窗口的模块
   包含独立的等待进程和抛错进程等"""


#核心子窗口
class WaitWindow(QMainWindow):
    setpercentage=Signal(int)
    delete_me=Signal()
    set_label=Signal(str)
    set_button=Signal(str)


    def closeEvent(self,event) -> None:
        for t in self.PP:
            t.terminate()
        event.accept()

    def __init__(self) -> None:
        """等待窗口初始化"""
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
        #配置动图
        self.ui.feibi_run.setMinimumSize(100,100)
        self.ui.feibi_run.setMaximumSize(100,100)
        self.movie = QMovie("picture/feibi_run.gif")
        self.movie.setScaledSize(self.ui.feibi_run.size())
        self.ui.feibi_run.setMovie(self.movie)
        self.movie.start()

    def Delete_me(self) -> None:
        """关闭并延迟销毁窗口"""
        self.close()
        self.deleteLater()#等app循环安全时再彻底销毁


class ErrorWindow(QObject):
    def __init__(self) -> None:
        """错误窗口初始化"""
        QObject.__init__(self)
        self.ui=QUiLoader().load(UI_ERROR)



#配置子窗口
class DetainWindow(QMainWindow):
    def __init__(self) -> None:
        """因其按钮的选择与父窗口的状态有关，所以其关于按钮选择的方法列在其父窗口中"""
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

    def Default_picture(self) -> None:
        """设置默认路径"""
        self.ui.dafeizhu.setScaledContents(True)
        self.ui.dafeizhu.setPixmap(QPixmap(self.pmap[0]))

    def eventFilter(self, obj, event) -> bool:

        if event.type() == QEvent.Enter:

            if obj == self.ui.Cancel:
                self.ui.dafeizhu.setPixmap(QPixmap(self.pmap[2]))

            elif obj == self.ui.Delete:
                self.ui.dafeizhu.setPixmap(QPixmap(self.pmap[1]))

        elif event.type() == QEvent.Leave:
            self.Default_picture()

        return super().eventFilter(obj, event)#不是点击靠近的直接放行，方便后面css的触发之类的


#日志通用子窗口(其实就是用来展示所有历史记录的)
class LogWindow(QObject):
    commit = Signal(str)
    show=Signal()

    _instance = None

    def __new__(cls):
        """开启单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self) -> None:
        """日志窗口初始化（单例模式，仅首次构造时加载 UI）"""
        if getattr(self, "_initialized", False):
            return

        super().__init__()
        self._initialized = True
        self.ui = QUiLoader().load(UI_LOG)

        #信号配置
        self.commit.connect(self.ui.loggershow.setPlainText)
        self.show.connect(self.ui.show)

