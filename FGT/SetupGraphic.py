#安装引导的界面

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
import re
from FGT.InterSystem import Execute
from FGT.ProcessCreator import Creator
from FGT.SonGraphic import DetainWindow
from FGT.paths import CONFIG_SETUP, UI_SETUP


class MainWindow(QMainWindow):
    #信号槽
    change_page_S=Signal(int)
    set_input_file_1=Signal(str)
    set_input_file_2=Signal(str)
    set_input_file_3=Signal(str)
    set_progressBar=Signal(int)
    setup_progressBar=Signal(int)
    change_label=Signal(str)

    #qt类析构函数(任何窗口在销毁之前都需要对由其创造的相关进程进行终止操作)
    def closeEvent(self,event):
        #清除进程池
        for t in self.PP:
            t.terminate()
        event.accept()


    def __init__(self):
        QMainWindow.__init__(self)
        Creator.__init__(self)
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



    #开启挽留子窗口
    def Make_son(self):
        self.DetainWindow.ui.resize(500,500)
        self.DetainWindow.ui.show()


    #抛出错误
    def Make_Error(self,ERROR):
        self.ui.label_5.setText("配置发生严重错误，被迫中断")
        self.ui.place_error.show()
        self.ui.place_error.setEnabled(True)
        self.ui.place_error.setPlainText(str(ERROR))
        self.ui.start_configuration.setText("重新配置")
        self.ui.start_configuration.show()
        self.ui.start_configuration.setEnabled(True)
        self.ui.backButton.setEnabled(True)
        self.ui.backButton.show()




    #修改对应页的按钮布局
    def change_page(self,data):
        index=self.ui.setupStack.currentIndex()+data
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
        self.change_label.emit(self.STEP[index])



    #开始配置进程
    def Get_configure(self):
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
            if self.ui.input_file_1=="" or self.ui.input_file_2.toPlainText()=="" or self.ui.input_file_3.toPlainText()=="":
                raise Exception("不要使用空路径，啾！")
            #拉取资源
            if self.ui.addff_y.isChecked():
                url="https://www.gyan.dev/ffmpeg/builds/packages"+r"//"+self.ui.ffversion.currentText()
                suffix=re.search("(.com)?(.*)\\.(.*)",url).group(3)
                self.ui.progressBar.show()
                command=rf"curl -L -o {self.ui.input_file_1.toPlainText()}/ffmpeg.{suffix} -# {url}"
                Execute.Curl_target(command,self,self.PP)
                #拉取完对窗口作相关调整
                self.set_progressBar.emit(100)#得改


            #配置初始默认路径
            with open(CONFIG_SETUP, "r", encoding="utf-8") as f:
                configuration=(f.read()).splitlines()
            configuration[2]=re.sub(re.search("\"(.*)\"",configuration[2]).group(1),self.ui.input_file_2.toPlainText(),configuration[2])
            configuration[3]=re.sub(re.search("\"(.*)\"",configuration[3]).group(1),self.ui.input_file_3.toPlainText(),configuration[3])
            with open(CONFIG_SETUP, "w", encoding="utf-8") as f:
                f.write("\n".join(configuration))

            #解压
            self.ui.label_5.setText("解压中")
            FILE=self.ui.input_file_1.toPlainText()
            file=f"{FILE}/ffmpeg.{suffix}"
            Execute.Tar_file(file,FILE,self.PP)

            #设置环境变量
            v_path=re.search("(.*)\\.(.*)",self.ui.ffversion.currentText()).group(1)
            Execute.Set_PATH(FILE+"/"+v_path+"/bin")


            #设置桌面快捷方式
            #此处相关操作仍需要等项目包装结构彻底定下来之后再做打算


            #结束收尾
            self.ui.label_5.setText("binggo！完成,请重启程序，啾！")
            self.ui.startButton.show()
            self.ui.startButton.setEnabled(True)
        except Exception as ERROR:
            #销毁进程
            for t in self.PP:
                t.terminate()
            #抛出错误
            self.Make_Error(ERROR)


#快捷方式保存形式
# powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\FF.lnk');$s.TargetPath='X:\FF.exe';$s.Save()"
# "X:\FF\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
# powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\FF.lnk');$s.TargetPath='X:\FF\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe';$s.Save()"


# powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut(\"$env:USERPROFILE\Desktop\TOSKY.lnk\");$s.TargetPath='X:\TOSKY';$s.Save()"
