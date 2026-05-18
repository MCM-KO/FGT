#安装引导的界面

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
import re
from FGT.InterSystem import Execute
from FGT.ProcessCreator import Creator
from FGT.SonGraphic import DetainWindow
from FGT.config_state import (
    ensure_setup_file,
    load_configuration,
    mark_setup_complete,
    save_configuration,
)
from FGT.paths import UI_SETUP


class MainWindow(QMainWindow):
    #信号槽
    change_page_S=Signal(int)
    set_input_file_1=Signal(str)
    set_input_file_2=Signal(str)
    set_input_file_3=Signal(str)
    set_progressBar=Signal(int)
    setup_progressBar=Signal(int)
    change_label=Signal(str)

    def closeEvent(self,event) -> None:
        """qt类析构函数(任何窗口在销毁之前都需要对由其创造的相关进程进行终止操作)"""
        #清除进程池
        for t in self.PP:
            t.terminate()
        event.accept()


    def __init__(self) -> None:
        """安装引导界面初始化"""
        QMainWindow.__init__(self)
        Creator.__init__(self)
        ensure_setup_file()
        self.ui=QUiLoader().load(UI_SETUP)
        self.default_path=str(Path.home() / "Desktop")
        from PySide6.QtCore import Qt
        self.STEP=["步骤一：添加环境变量","步骤二：配置默认路径","步骤三：加载相关配置"]
        #配置进程池
        self.PP=[]
        #设置一体化
        self.setCentralWidget(self.ui)
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint
        )
        # 配置子窗口
        self.DetainWindow=DetainWindow()
        self.DetainWindow.ui.resize(600,600)
        self.SetupErrorWindow=None
        #初始状态
        self.ui.startButton.hide()
        self.ui.startButton.setEnabled(False)
        self.ui.backButton.hide()
        self.ui.backButton.setEnabled(False)
        self.ui.label_5.hide()
        self.ui.label_5.setEnabled(False)
        self.ui.progressBar.hide()
        self.ui.addff_y.setChecked(True)
        self.ui.place_error.hide()
        self.ui.place_error.setEnabled(False)
        #信号绑定
        self.change_page_S.connect(self.ui.setupStack.setCurrentIndex)
        self.set_input_file_1.connect(self.ui.input_file_1.setPlainText)
        self.set_input_file_2.connect(self.ui.input_file_2.setPlainText)
        self.set_input_file_3.connect(self.ui.input_file_3.setPlainText)
        self.set_progressBar.connect(self.ui.progressBar.setValue)
        self.setup_progressBar.connect(self.ui.setupProgressBar.setValue)
        self.change_label.connect(self.ui.stepCurrent.setText)
        #按钮绑定
        self.ui.nextButton.clicked.connect(lambda:self.change_page(1))
        self.ui.backButton.clicked.connect(lambda:self.change_page(-1))
        self.ui.browse_1.clicked.connect(lambda:Execute.Connect_dir("set_input_file_1",self,self.default_path))
        self.ui.browse_2.clicked.connect(lambda:Execute.Connect_dir("set_input_file_2",self,self.default_path))
        self.ui.browse_3.clicked.connect(lambda:Execute.Connect_dir("set_input_file_3",self,self.default_path))
        self.ui.addff_y.clicked.connect(lambda:self.ui.addff_n.setChecked(False))
        self.ui.addff_n.clicked.connect(lambda:self.ui.addff_y.setChecked(False))
        self.ui.cancelButton.clicked.connect(self.Make_son)
        self.ui.start_configuration.clicked.connect(lambda:Creator.Start_process(self.Get_configure))
        self.ui.startButton.clicked.connect(self.close)
        self.DetainWindow.ui.Cancel.clicked.connect(self.DetainWindow.ui.close)
        self.DetainWindow.ui.Cancel.clicked.connect(self.DetainWindow.Default_picture)
        self.DetainWindow.ui.Delete.clicked.connect(self.DetainWindow.ui.close)
        self.DetainWindow.ui.Delete.clicked.connect(self.close)



    def Make_son(self) -> None:
        """开启挽留子窗口"""
        self.DetainWindow.ui.resize(500,500)
        self.DetainWindow.ui.show()


    def Make_Error(self,ERROR) -> None:
        """抛出错误"""
        self.ui.label_5.setText("配置发生严重错误，被迫中断")
        self.ui.place_error.show()
        self.ui.place_error.setEnabled(True)
        self.ui.place_error.setPlainText(str(ERROR))
        self.ui.start_configuration.setText("重新配置")
        self.ui.start_configuration.show()
        self.ui.start_configuration.setEnabled(True)
        self.ui.backButton.setEnabled(True)
        self.ui.backButton.show()




    def change_page(self,data) -> None:
        """修改对应页的按钮布局"""
        last = max(0, self.ui.setupStack.count() - 1)
        index = max(0, min(self.ui.setupStack.currentIndex() + data, last))
        if index==0:
            self.ui.startButton.hide()
            self.ui.startButton.setEnabled(False)
            self.ui.backButton.hide()
            self.ui.backButton.setEnabled(False)
            self.ui.nextButton.show()
            self.ui.nextButton.setEnabled(True)
        elif index==1:
            self.ui.startButton.hide()
            self.ui.startButton.setEnabled(False)
            self.ui.backButton.show()
            self.ui.backButton.setEnabled(True)
            self.ui.nextButton.show()
            self.ui.nextButton.setEnabled(True)
        elif index==2:
            self.ui.startButton.hide()
            self.ui.startButton.setEnabled(False)
            self.ui.backButton.show()
            self.ui.backButton.setEnabled(True)
            self.ui.nextButton.hide()
            self.ui.nextButton.setEnabled(False)
        self.change_page_S.emit(index)
        self.setup_progressBar.emit((index+1)*33)
        self.change_label.emit(self.STEP[min(index, len(self.STEP) - 1)])



    def Get_configure(self) -> None:
        """开始配置进程"""
        #读取选项配置
        try:
            isink=0
            if self.ui.isink.isChecked():
                isink=1
            #防止线程混乱
            self.ui.place_error.hide()
            self.ui.place_error.setEnabled(False)
            self.ui.backButton.hide()
            self.ui.backButton.setEnabled(False)
            self.ui.isink.hide()
            self.ui.isink.setEnabled(False)
            self.ui.label_4.hide()
            self.ui.label_4.setEnabled(False)
            self.ui.start_configuration.hide()
            self.ui.start_configuration.setEnabled(False)
            self.ui.label_5.setText("配置中")
            self.ui.label_5.show()
            #验证资源目标
            if (
                not self.ui.input_file_1.toPlainText().strip()
                or not self.ui.input_file_2.toPlainText().strip()
                or not self.ui.input_file_3.toPlainText().strip()
            ):
                raise Exception("不要使用空路径，啾！")
            pkg = self.ui.ffversion.currentText()
            suffix = pkg.rsplit(".", 1)[-1].lower()

            #拉取资源（GyanD 官方包，经国内 GitHub 加速镜像，文件名与下拉框一致）
            if self.ui.addff_y.isChecked():
                ver = re.search(r"^ffmpeg-([\d.]+)-", pkg).group(1)
                url = (
                    f"https://ghfast.top/https://github.com/GyanD/codexffmpeg"
                    f"/releases/download/{ver}/{pkg}"
                )
                self.ui.progressBar.show()
                dest_dir = self.ui.input_file_1.toPlainText()
                command = rf'curl -L -o "{dest_dir}/ffmpeg.{suffix}" -# {url}'
                Execute.Curl_target(command, self, self.PP)
                self.set_progressBar.emit(100)

                self.ui.label_5.setText("解压中")
                archive = f"{dest_dir}/ffmpeg.{suffix}"
                Execute.Tar_file(archive, dest_dir, self.PP)

                v_path = re.search(r"(.*)\.", pkg).group(1)
                Execute.Set_PATH(f"{dest_dir}/{v_path}/bin")

            configuration = load_configuration()
            configuration[2] = re.sub(
                re.search(r"\"(.*)\"", configuration[2]).group(1),
                self.ui.input_file_2.toPlainText().strip(),
                configuration[2],
            )
            configuration[3] = re.sub(
                re.search(r"\"(.*)\"", configuration[3]).group(1),
                self.ui.input_file_3.toPlainText().strip(),
                configuration[3],
            )
            save_configuration(configuration)

            #设置桌面快捷方式
            if self.ui.addff_y.isChecked():
                Execute.Set_ink()

            configuration = load_configuration()
            configuration[1] = 'ISSET="YES"'
            save_configuration(configuration)
            mark_setup_complete()
            self.ui.label_5.setText("Bingo！完成，请点击开始进入主界面，啾！")
            self.ui.startButton.show()
            self.ui.startButton.setEnabled(True)
        except Exception as ERROR:
            #销毁进程
            for t in self.PP:
                t.terminate()
            #抛出错误
            self.Make_Error(ERROR)



