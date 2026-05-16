import subprocess
import datetime

from FGT.InterSystem import Execute
from FGT.SonGraphic import WaitWindow, ErrorWindow
import cv2
#泛型定义
from typing import Callable, TypeVar, ParamSpec, Optional, List
from FGT.UGT import UQLabel
P = ParamSpec("P")
R = TypeVar("R")
import time
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QPixmap, QMovie, QPainterPath, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QPlainTextEdit, QWidget, QMessageBox
from PySide6.QtCore import QFile, QObject, Qt, QThread, Signal
from PySide6.QtUiTools import QUiLoader
import re
from FGT.ProcessCreator import Creator
from FGT.LOGGER import SignLogger
from FGT.paths import (
    BUFFER_PHOTO,
    CONCAT_TARGET,
    CONFIG_SETUP,
    FF_LOG,
    SYSTEM_LOG,
    UI_MAIN,
    WIKI_AUDIO,
    WIKI_VIDEO,
    ps,
    qt_url,
)
#构建最大主窗口
class MainWindow(QMainWindow,QObject):
    #局部类用于控制日志，传输日志
    class Logger_(SignLogger):
        #两个默认的日志路径
        system_log_path = SYSTEM_LOG
        ff_log_path = FF_LOG

        #将日志载入文件
        def Write_file(self):
            pass

        #上传系统日志
        def Commit_sl(self,ERROR):
            self.outer.sl_S.emit("\n\n")
            self.outer.sl_S.emit(str(datetime.datetime.now()))
            self.outer.sl_S.emit(str(ERROR))
            self.outer.sl_S.emit("\n\n\n")


        #上传命令日志
        def Commit_fl(self,result,FFLIST):
            self.outer.fl_S.emit("\n\n")
            self.outer.fl_S.emit(str(datetime.datetime.now()))
            self.outer.fl_S.emit("the command->:"+" ".join(FFLIST)+"\n")
            self.outer.fl_S.emit(str(result)+"\n")
            self.outer.fl_S.emit("\n\n\n")

        #上传历史日志
        def Commit_all(self,selection):
            try:
                path=None
                if selection==0:
                    path=self.system_log_path
                else:
                    path=self.ff_log_path
                    text=None
                with open(path,"r") as f:
                    text=str(f.read())
                if selection==0:
                    self.outer.sl_S.emit(text)
                else:
                    self.outer.fl_S.emit(text)
                self.outer.logstatus.emit("上传成功")
            except Exception:
                self.outer.logstatus.emit("上传失败")


        #删除历史日志
        def Delete_all(self,selection):
            try:
                path = None
                if selection == 0:
                    if not self.outer.ui.isdeletesl.isChecked():
                        self.outer.sl_S.emit("针对删除系统历史日志的请求，未勾选确认删除")
                        return
                    path = self.system_log_path
                    self.outer.sl_S.emit("用户执行：删除系统历史日志")
                else:
                    if  not self.outer.ui.isdeletefl.isChecked():
                        self.outer.sl_S.emit("针对删除命令历史日志的请求，未勾选确认删除")
                        return
                    self.outer.sl_S.emit("用户执行：删除系统历史日志")
                    path = self.ff_log_path
                    text = None
                with open(path, "w") as f:
                    f.write("")
                self.outer.logstatus.emit("删除成功")
            except Exception:
                self.outer.logstatus.emit("删除失败")




    #设置信号槽
    creat_son=Signal(str)#创建子窗口
    sl_S=Signal(str)
    fl_S=Signal(str)
    path_input_enter=Signal(str)
    path_input_2_enter=Signal(str)
    path_input_3_enter=Signal(str)
    path_input_4_enter=Signal(str)
    path_input_6_enter=Signal(str)
    path_input_7_enter=Signal(str)
    path_input_8_enter=Signal(str)
    path_input_9_enter = Signal(str)
    path_input_10_enter = Signal(str)
    path_input_11_enter = Signal(str)
    path_input_12_enter=Signal(str)
    path_input_13_enter=Signal(str)
    addpath_S=Signal(str)
    current_height=Signal(str)
    current_width=Signal(str)
    sheight=Signal(int)
    swidth=Signal(int)
    cx_s=Signal(int)
    cy_s=Signal(int)
    cheight=Signal(int)
    cwidth=Signal(int)
    cx_s_2 = Signal(int)
    cy_s_2 = Signal(int)
    cheight_2 = Signal(int)
    cwidth_2 = Signal(int)
    cwidth_begin=Signal(int)
    cwidth_end=Signal(int)
    cheight_begin=Signal(int)
    cheight_end=Signal(int)
    cx_begin=Signal(int)
    cx_end=Signal(int)
    cy_begin=Signal(int)
    cy_end=Signal(int)
    a_show_wiki_S=Signal(str)#百科文本框
    v_show_wiki_S=Signal(str)
    default_path_S=Signal(str)#高级设置区
    default_path_s_S=Signal(str)
    logstatus=Signal(str)

    #初始化UI数据
    def __init__(self):
        QMainWindow.__init__(self)
        Creator.__init__(self)
        self.ui=QUiLoader().load(UI_MAIN)
        self.ui.setWindowTitle("FGT")
        #读取科普内容
        self.Load_Wiki()

        #读取配置文件
        with open(CONFIG_SETUP, "r+", encoding="utf-8") as f:
            self.configuration=(f.read()).splitlines()
        self.default_path = (re.search("\"(.*)\"",self.configuration[2])).group(1)
        self.default_path_s = (re.search("\"(.*)\"",self.configuration[3])).group(1)


    #额外ui资源附着
        # #SHOW背景设置
        # self.ui.SHOW.setStyleSheet(f"QStackedWidget{{border-image: url({qt_url('picture', 'feibis.png')});}}")
        #gif动图区
        self.ui.feibi_1.setMinimumSize(350,300)
        self.feibi_fealty=(QPixmap(ps("picture", "feibi_fealty.png"))).scaled(
            self.ui.feibi_1.size(),
        )
        self.ui.feibi_1.setPixmap(self.feibi_fealty)
        #关于我们
        UQLabel.Round(self.ui.avator_MCMKO, ps("picture", "MCM_KO.ico"), 100, 100)
        UQLabel.Round(self.ui.avator, ps("picture", "hendiandian1525_cpu.ico"), 100, 100)

        self.ui.feibi_ffmpeg.setMinimumSize(524,312)
        self.ui.feibi_ffmpeg.setMaximumSize(524,312)
        self.ui.feibi_ffmpeg.setPixmap(QPixmap(ps("picture", "feibi_ffmpeg.png")).scaled(self.ui.feibi_ffmpeg.size()))

        self.ui.gear_1.setMinimumSize(30,30)
        self.ui.gear_2.setMinimumSize(30,30)
        self.ui.gear_1.setPixmap(QPixmap(ps("picture", "gear.png")).scaled(self.ui.gear_1.size()))
        self.ui.gear_2.setPixmap(QPixmap(ps("picture", "gear.png")).scaled(self.ui.gear_2.size()))


        #子窗口区(均为多例模式)
        self.WaitWindow:List[Optional[WaitWindow]]=[None for _ in range(100)]#等待百分比子窗口
        self.ErrorWindow:List[Optional[ErrorWindow]]=[None for _ in range(100)]#报错子窗口
        self.WindowIndex=None#记录每一个进程ID

        #播放线程池
        self.FPTP=[]

        #左右分区逻辑绑定
        self.ui.LIST.currentRowChanged.connect(self.Change_page)
        self.ui.loggersort.currentRowChanged.connect(self.Change_page_2)

        #信号绑定区
        self.creat_son.connect(self.Show_sonwidgt)
        self.sl_S.connect(self.ui.systemlogger.appendPlainText)
        self.fl_S.connect(self.ui.ffmpeglogger.appendPlainText)
        self.path_input_enter.connect(self.ui.input_file.setPlainText)#n个目录选择方法
        self.path_input_2_enter.connect(self.ui.input_file_2.setPlainText)
        self.path_input_3_enter.connect(self.ui.input_file_3.setPlainText)
        self.path_input_4_enter.connect(self.ui.input_file_4.setPlainText)
        self.path_input_6_enter.connect(self.ui.input_file_6.setPlainText)
        self.path_input_7_enter.connect(self.ui.input_file_7.setPlainText)
        self.path_input_8_enter.connect(self.ui.input_file_8.setPlainText)
        self.path_input_9_enter.connect(self.ui.input_file_9.setPlainText)
        self.path_input_10_enter.connect(self.ui.input_file_10.setPlainText)
        self.path_input_11_enter.connect(self.ui.input_file_11.setPlainText)
        self.path_input_12_enter.connect(self.ui.input_file_12.setPlainText)
        self.addpath_S.connect(self.ui.concat_target.appendPlainText)
        self.current_height.connect(self.ui.current_height.setPlainText)
        self.current_width.connect(self.ui.current_width.setPlainText)
        self.sheight.connect(self.ui.sheight.setValue)
        self.swidth.connect(self.ui.swidth.setValue)
        self.cx_s.connect(self.ui.cx.setValue)
        self.cy_s.connect(self.ui.cy.setValue)
        self.cheight.connect(self.ui.cheight.setValue)
        self.cwidth.connect(self.ui.cwidth.setValue)
        self.swidth.connect(self.ui.swidth.setValue)
        self.cx_s_2.connect(self.ui.cx_2.setValue)
        self.cy_s_2.connect(self.ui.cy_2.setValue)
        self.cheight_2.connect(self.ui.cheight_2.setValue)
        self.cwidth_2.connect(self.ui.cwidth_2.setValue)
        self.cwidth_begin.connect(self.ui.cwidth_begin.setValue)
        self.cwidth_end.connect(self.ui.cwidth_end.setValue)
        self.cheight_begin.connect(self.ui.cheight_begin.setValue)
        self.cheight_end.connect(self.ui.cheight_end.setValue)
        self.cx_begin.connect(self.ui.cx_begin.setValue)
        self.cx_end.connect(self.ui.cx_end.setValue)
        self.cy_begin.connect(self.ui.cy_begin.setValue)
        self.cy_end.connect(self.ui.cy_end.setValue)
        self.a_show_wiki_S.connect(self.ui.a_show_wiki.setPlainText)
        self.v_show_wiki_S.connect(self.ui.v_show_wiki.setPlainText)
        self.default_path_S.connect(self.ui.default_path.setPlainText)
        self.default_path_s_S.connect(self.ui.default_path_s.setPlainText)
        self.logstatus.connect(self.Raise_message)
        #按钮绑定区
        self.ui.start_transform.clicked.connect(lambda: Creator.Start_process(self.Get_transform))#创建ffmpeg转换线程
        self.ui.start_gif.clicked.connect(lambda: Creator.Start_process(self.Get_gif))#创建动图转换线程
        self.ui.input_enter.clicked.connect(lambda: Execute.Connect_path("path_input_enter",self,self.default_path))
        self.ui.input_enter_2.clicked.connect(lambda: Execute.Connect_path("path_input_2_enter",self,self.default_path))
        self.ui.input_enter_3.clicked.connect(lambda: Execute.Connect_path("path_input_3_enter",self,self.default_path))
        self.ui.input_enter_4.clicked.connect(lambda: Execute.Connect_path("path_input_4_enter",self,self.default_path))
        self.ui.input_enter_6.clicked.connect(lambda: Execute.Connect_path("path_input_6_enter",self,self.default_path))
        self.ui.input_enter_7.clicked.connect(lambda: Execute.Connect_path("path_input_7_enter",self,self.default_path))
        self.ui.input_enter_8.clicked.connect(lambda: Execute.Connect_path("path_input_8_enter",self,self.default_path))
        self.ui.input_enter_9.clicked.connect(lambda: Execute.Connect_path("path_input_9_enter",self,self.default_path))
        self.ui.input_enter_11.clicked.connect(lambda: Execute.Connect_path("path_input_11_enter",self,self.default_path))
        self.ui.input_enter_12.clicked.connect(lambda: Execute.Connect_path("path_input_12_enter",self,self.default_path))
        self.ui.browse_2.clicked.connect(lambda:Execute.Connect_dir("default_path_S",self,self.default_path))
        self.ui.browse_1.clicked.connect(lambda:Execute.Connect_dir("default_path_s_S",self,self.default_path))
        self.ui.addpath.clicked.connect(self.Add_path)
        self.ui.concat.clicked.connect(lambda: Creator.Start_process(self.Get_concat))
        self.ui.ensure_element.clicked.connect(lambda:Creator.Start_process(self.Set_current_hw))
        self.ui.selectsize.clicked.connect(lambda:Creator.Start_process(lambda :self.Select_size(self.cx_s,self.cy_s,self.cheight,self.cwidth)))
        self.ui.clear_path.clicked.connect(self.Clear_path)
        self.ui.start_cut.clicked.connect(lambda:Creator.Start_process(self.Get_cut))
        self.ui.selectsize_2.clicked.connect(lambda:Creator.Start_process(lambda: self.Select_size(self.cx_s_2, self.cy_s_2, self.cheight_2, self.cwidth_2)))
        self.ui.addwatermark.clicked.connect(lambda: Creator.Start_process(self.Get_watermark))
        self.ui.loggeremit0.clicked.connect(lambda:Creator.Start_process(lambda:self.Logger_(self).Commit_all(0)))
        self.ui.loggeremit1.clicked.connect(lambda: Creator.Start_process(lambda: self.Logger_(self).Commit_all(1)))
        self.ui.deletesl.clicked.connect(lambda: Creator.Start_process(lambda: self.Logger_(self).Delete_all(0)))
        self.ui.deletefl.clicked.connect(lambda: Creator.Start_process(lambda: self.Logger_(self).Delete_all(1)))
        self.ui.selectsize_3.clicked.connect(lambda: Creator.Start_process(lambda: self.Select_size(self.cx_begin, self.cy_begin, self.cheight_begin, self.cwidth_begin)))
        self.ui.selectsize_4.clicked.connect(lambda: Creator.Start_process(lambda: self.Select_size(self.cx_end, self.cy_end, self.cheight_end, self.cwidth_end)))
        self.ui.player.clicked.connect(lambda:Creator.Start_process(self.Get_player))
        self.ui.awiki.clicked.connect(lambda:Creator.Start_process(self.Set_awiki))
        self.ui.vwiki.clicked.connect(lambda:Creator.Start_process(self.Set_vwiki))
        self.ui.ensure_1.clicked.connect(lambda:Creator.Start_process(self.Change_default_path_s))
        self.ui.ensure_2.clicked.connect(lambda:Creator.Start_process(self.Change_default_path))
        self.ui.staticsolid.clicked.connect(lambda:self.ui.SHOW_SON.setCurrentIndex(0))#通过按钮绑定来分组
        self.ui.dynamicsolid.clicked.connect(lambda:self.ui.SHOW_SON.setCurrentIndex(1))
        self.ui.tackle_1.clicked.connect(lambda:Creator.Start_process(self.Get_s_audio))
        self.ui.tackle_2.clicked.connect(lambda:Creator.Start_process(self.Get_n_audio))
        #初始化信号发射区
        self.default_path_S.emit(self.default_path)
        self.default_path_s_S.emit(self.default_path_s)

#泛用方法区:
    #科普文件载入
    def Load_Wiki(self):
        with open(WIKI_AUDIO, "r", encoding="utf-8") as f:
            self.AWIKI_TEXT = (f.read()).splitlines()
        with open(WIKI_VIDEO, "r", encoding="utf-8") as f:
            self.VWIKI_TEXT = (f.read()).splitlines()

    #进程移交与日志返回
    def Tran_thread(self,FFLIST,duration):
        t = Creator.Start_process(lambda: self.creat_son.emit("W"))
        t.join()  # 手动阻塞
        time.sleep(0.2)  # 手动阻塞
        window = self.WaitWindow[self.WindowIndex]
        result = Creator.Carry_ff(FFLIST, window, duration, window.PP)
        self.Logger_(self).Commit_fl(result, FFLIST)
        # 完成时对窗口进行更新
        if window.isVisible():
            window.setpercentage.emit(100)
            window.ui.titleLabel.setText("Binggo!,转码已完成")
            window.ui.cancelButton.setText("完成")

    #开启子窗口
    def Show_sonwidgt(self,selection):
        if selection=='W':
            for i in range(0,100):
                if self.WaitWindow[i] is None:
                    self.WindowIndex=i
                    self.WaitWindow[i]=WaitWindow()
                    self.WaitWindow[i].show()
                    break
        else:
            for i in range(0,100):
                if self.ErrorWindow[i] is None:
                    self.ErrorWindow[i]=ErrorWindow()
                    self.ErrorWindow[i].ui.show()
                    break

    # 上传状态
    def Raise_message(self,TEXT):
        self.message = QMessageBox()
        self.message.setWindowTitle("提示")
        self.message.setText(TEXT)
        self.message.show()

    #左右界面绑定
    def Change_page(self,index):
        self.ui.SHOW.setCurrentIndex(index)
    def Change_page_2(self,index):
        self.ui.logger.setCurrentIndex(index)


    #获取裁切位置
    def Select_size(self,cx,cy,cheight,cwidth):
        image_path = BUFFER_PHOTO
        if not image_path.strip():
            print("未选择图片")
            return

        img = cv2.imread(image_path)
        if img is None:
            print("图片加载失败")
            return

        start_point = None
        end_point = None
        drawing = False
        temp_img = img.copy()

        # 鼠标回调
        def mouse_callback(event, x, y, flags, param):
            nonlocal start_point, end_point, drawing, temp_img
            if event == cv2.EVENT_LBUTTONDOWN:
                drawing = True
                start_point = (x, y)
                temp_img = img.copy()

            elif event == cv2.EVENT_MOUSEMOVE:
                if drawing:
                    temp_img = img.copy()
                    cv2.rectangle(temp_img, start_point, (x, y), (0, 255, 0), 2)

            elif event == cv2.EVENT_LBUTTONUP:
                drawing = False
                end_point = (x, y)
                temp_img = img.copy()
                cv2.rectangle(temp_img, start_point, end_point, (0, 255, 0), 2)
                cv2.imshow("image", temp_img)

                # 计算选框
                x0, y0 = start_point
                x1, y1 = end_point
                left = min(x0, x1)
                top = min(y0, y1)
                width = abs(x1 - x0)
                height = abs(y1 - y0)
                self.sl_S.emit(str(datetime.datetime.now()))
                self.sl_S.emit(f"发起区块选择命令：左上({left},{top}), 宽{width}, 高{height}" + "\n\n\n")
                cx.emit(left)
                cy.emit(top)
                cheight.emit(height)
                cwidth.emit(width)

        cv2.namedWindow("image")
        cv2.setMouseCallback("image", mouse_callback)

        # 主循环显示图像
        while True:
            cv2.imshow("image", temp_img)
            key = cv2.waitKey(1)
            if key == 27:  # ESC退出
                break

        cv2.destroyAllWindows()













#非泛用方法区：
    #文件转化区


    #开启ffmpeg转化线程
    def Get_transform(self):
        try:
            input_file=self.ui.input_file.toPlainText()
            output_file=self.default_path_s+"\\"+self.ui.file_name.toPlainText()+"."+self.ui.file_f.currentText()

            if input_file=="" or output_file=="":
                raise Exception("不允许源文件矢文件名称为空哦，啾！")

            duration =Creator.Get_duration(input_file)
            if duration=="N/A":
                duration=0.2
            else:
                duration=float(duration)

            FFLIST=[]
            FFLIST.append("ffmpeg")
            FFLIST.append("-i");FFLIST.append(input_file)
            FFLIST.append("-vf");FFLIST.append(f"setpts=PTS/{self.ui.setspeed.currentText()}")
            AF=[]
            AF.append(f"atempo={self.ui.setspeed.currentText()}")
            if self.ui.issetaudio.isChecked():
                if "特殊" in self.ui.audiomodel.currentText():
                    AF.append("lowpass=f=1500")
                    FFLIST.append("-ar");FFLIST.append("8000")
                    FFLIST.append("-b:a");FFLIST.append("8k")

                else:
                    volume=None
                    bits=None
                    if self.ui.audiomodel.currentText()=="微损音质":
                        volume=20
                        bits=4
                    elif self.ui.audiomodel.currentText()=="半损音质":
                        volume=30
                        bits=2
                    elif self.ui.audiomodel.currentText()=="全损音质":
                        volume=40
                        bits=1
                    AF.append(f"volume={volume}")
                    AF.append(f"acrusher=bits={bits}:mode=log")

            FFLIST.append("-af");FFLIST.append(",".join(AF))
            duration=duration/float(self.ui.setspeed.currentText())
            if self.ui.vn.currentText()=="是":
                FFLIST.append("-vn")
            if self.ui.an.currentText()=="是":
                FFLIST.append("-an")
            if self.ui.sn.currentText()=="是":
                FFLIST.append("-sn")
            if self.ui.issetdefinition.isChecked():
                FFLIST.append("-crf");FFLIST.append(str(self.ui.setdefinition.value()))
            if self.ui.issetframe.isChecked():
                FFLIST.append("-aframes");FFLIST.append(str(self.ui.setframe.value()))
                FFLIST.append("-vframes");FFLIST.append(str(self.ui.setframe.value()))
            if self.ui.isae.isChecked():
                FFLIST.append("-c:a");FFLIST.append(self.ui.ae.currentText())
            if self.ui.isve.isChecked():
                FFLIST.append("-c:v");FFLIST.append(self.ui.ve.currentText())
            if self.ui.isbalance.isChecked():
                FFLIST.append("-preset");FFLIST.append(self.ui.balance.currentText())
            FFLIST.append("-y")
            FFLIST.append(output_file)

            self.Tran_thread(FFLIST,duration)

        except Exception as ERROR:
            self.creat_son.emit("E")
            self.Logger_(self).Commit_sl(ERROR)


#开启动图转换进程
    def Get_gif(self):
        try:
            input_file=self.ui.input_file_2.toPlainText()
            output_file = self.default_path_s + "\\" + self.ui.file_name_2.toPlainText() + ".gif"

            if input_file=="" or output_file=="":
                raise Exception("不允许源文件矢文件名称为空哦，啾！")

            duration = Creator.Get_duration(input_file)
            if duration == "N/A":
                duration = 0.2
            else:
                duration = float(duration)

            FFLIST = []
            FFLIST.append("ffmpeg")
            FFLIST.append("-i");FFLIST.append(input_file)
            FFLIST.append("-filter_complex")
            FFLIST.append("[0:v] fps=15,split[a][b];[a]palettegen[p];[b][p]paletteuse")
            FFLIST.append("-y")
            FFLIST.append(output_file)

            self.Tran_thread(FFLIST,duration)

        except Exception as ERROR:
            self.creat_son.emit("E")
            self.Logger_(self).Commit_sl(ERROR)

#裁剪文件的函数区
    #用于显示当前文件的长宽高
    def Set_current_hw(self):
        input_file = self.ui.input_file_3.toPlainText()
        if input_file is None:
            return
        #获取第一帧
        FFLIST=["ffmpeg","-i",input_file,"-y","-frames:v","1", BUFFER_PHOTO]
        result = subprocess.run(
            FFLIST,
            capture_output=True,
            text=True
        )
        with open(SYSTEM_LOG, "a") as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write(result.stderr)
        #获取高宽
        im=cv2.imread(BUFFER_PHOTO)
        height, width = im.shape[:2]
        self.current_height.emit(str(height))
        self.current_width.emit(str(width))





    #开启裁切转化进程
    def Get_cut(self):
        try:
            input_file=self.ui.input_file_3.toPlainText()
            if input_file=="":
                raise Exception("不允许源文件矢文件名称为空哦，啾！")

            extension=re.search(r"\.(.*)",input_file)#获取后缀名
            output_file=self.default_path_s+"/"+self.ui.file_name_3.toPlainText()+"."+extension.group(1)

            duration = Creator.Get_duration(input_file)
            if duration == "N/A":
                duration = 0.2
            else:
                duration = float(duration)


            FFLIST=[]
            FFLIST.append("ffmpeg");FFLIST.append("-i");FFLIST.append(input_file)#输入流
            FFLIST.append("-y")
            VF=[]
            if self.ui.h_s.isChecked():
                VF.append(f"scale={self.ui.swidth.value()}:{self.ui.sheight.value()}")
            else:
                if self.ui.h_c.isChecked():
                    VF.append(f"crop={self.ui.cwidth.value()}:{self.ui.cheight.value()}:{self.ui.cx.value()}:{self.ui.cy.value()}")
            if self.ui.isreverse.isChecked():
                reverseindex=None
                if self.ui.reverseindex.currentText() =="逆90，并上下翻转":
                    reverseindex=0
                elif self.ui.reverseindex.currentText() =="顺90":
                    reverseindex=0
                elif self.ui.reverseindex.currentText() =="逆90":
                    reverseindex=0
                elif self.ui.reverseindex.currentText() =="顺90，并上下翻转":
                    reverseindex=0
                VF.append(f"transpose={reverseindex}")
            vf=",".join(VF)
            FFLIST.append("-vf");FFLIST.append(vf)#过滤器选项
            if self.ui.istime.isChecked():
                FFLIST.append("-ss");FFLIST.append(f"{self.ui.shour.value()}:{self.ui.sminute.value()}:{self.ui.ssecond.value()}")
                FFLIST.append("-t");FFLIST.append(f"{self.ui.dhour.value()}:{self.ui.dminute.value()}:{self.ui.dsecond.value()}")
            FFLIST.append(output_file)

            self.Tran_thread(FFLIST,duration)
        except Exception as ERROR:
            self.creat_son.emit("E")
            self.Logger_(self).Commit_sl(ERROR)









#合并文件的函数区
    #用于显示栏中中添加路径
    def Add_path(self):
        if self.ui.input_file_4 is not None:
            self.addpath_S.emit(f"{self.ui.input_file_4.toPlainText()}")

    #形成缓冲的目标文件
    def Form_path(self):
        TARGET=self.ui.concat_target.toPlainText()
        target_list=re.findall(r"[A-Z]:[^\s\n]*",TARGET)
        with open(CONCAT_TARGET, "w", encoding="utf-8") as f:
            for i in target_list:
                f.write("file"+"   "+i+"\n")

    #开启合并进程
    def Get_concat(self):
        try:
            self.Form_path()
            output_file = self.default_path_s + "/" + self.ui.file_name_4.toPlainText() + "." + self.ui.file_f_3.currentText()

            if output_file=="":
                raise Exception("不允许源文件矢文件名称为空哦，啾！")

            duration=0
            with open(CONCAT_TARGET, "r", encoding="utf-8") as f:
                for line in f:
                    target = re.search("file(\\s)*(.*)", line)
                    if target == "":
                        raise Exception("不允许源文件矢文件名称为空哦，啾！")
                    duration_s = Creator.Get_duration(target)
                    if duration_s == "N/A":
                        duration += 0.2
                    else:
                        duration += float(duration_s)



            FFLIST=[]
            FFLIST.append("ffmpeg");FFLIST.append("-f");FFLIST.append("concat")
            FFLIST.append("-i");FFLIST.append(CONCAT_TARGET)
            FFLIST.append("-y")
            FFLIST.append("-c");FFLIST.append("copy")
            FFLIST.append(output_file)

            self.Tran_thread(FFLIST,duration)

        except Exception as ERROR:
            self.creat_son.emit("E")
            self.Logger_(self).Commit_sl(ERROR)


    #清理掉加载的文件
    def Clear_path(self):
        self.ui.concat_target.clear()




#添加水印的函数区
    #生成缓冲图片
    def Set_current_hw_2(self):
            input_file = self.ui.input_file_6.toPlainText()
            if input_file is None:
                return
            #获取第一帧
            FFLIST=["ffmpeg","-i",input_file,"-y","-frames:v","1", BUFFER_PHOTO]
            result = subprocess.run(
                FFLIST,
                capture_output=True,
                text=True
            )
            with open(SYSTEM_LOG, "a") as f:
                f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                f.write(result.stderr)

    #创建添加水印的线程
    def Get_watermark(self):
        try:
            input_file_o=self.ui.input_file_6.toPlainText()
            input_file_w = self.ui.input_file_7.toPlainText()
            if input_file_o==""or input_file_w=="":
                raise Exception("不允许源文件矢文件名称为空哦，啾！")
            extension=(re.search(r"\.(.*)",input_file_o)).group(1)
            extension_s = (re.search(r"\.(.*)", input_file_w)).group(1)
            output_file=self.default_path_s+"/"+self.ui.file_name_6.toPlainText() + "." + extension
            duration =Creator.Get_duration(input_file_o)
            if duration == "N/A":
                duration = 0.2
            else:
                duration = float(duration)


            FFLIST=[]
            FFLIST.append("ffmpeg")
            FFLIST.append("-i");FFLIST.append(input_file_o)
            #只有动图才可以设置这个
            if extension_s == "gif":
                FFLIST.append("-ignore_loop");FFLIST.append("0")
            FFLIST.append("-i");FFLIST.append(input_file_w)
            FFLIST.append("-y")

            #通用设置
            if self.ui.istime_2.isChecked():
                FFLIST.append("-ss")
                FFLIST.append(f"{self.ui.shour_2.value()}:{self.ui.sminute_2.value()}:{self.ui.ssecond_2.value()}")
                FFLIST.append("-t")
                FFLIST.append(self.ui.dsecond_2.value())
            VF=[]
            VF.append("[1:v]format=rgba")
            if self.ui.settransparent.isChecked():
                VF.append(f"colorchannelmixer=aa={self.ui.transparent.value()}")


            #静态水印添加
            if self.ui.staticwatermark.isChecked():
                if self.ui.h_c_2.isChecked():
                    cwidth=int(self.ui.cwidth_2.value());cheight=int(self.ui.cheight_2.value())
                    cx = int(self.ui.cx_2.value());cy=int(self.ui.cy_2.value())
                    VF.append(f"scale={int(cwidth/2)*2}:{int(cheight/2)*2}[wm];[0:v][wm]overlay={int(cx/2)*2}:{int(cy/2)*2}")
                vf=",".join(VF)
                FFLIST.append("-filter_complex");FFLIST.append(vf)
                FFLIST.append(output_file)
            #动态水印添加
            elif self.ui.dynamicwatermark.isChecked():
                vf=""
                for i in VF:
                    vf+=str(i)+','
                w1=self.ui.cwidth_begin.value();w2=self.ui.cwidth_end.value()
                h1 = self.ui.cheight_begin.value();h2=self.ui.cheight_end.value()
                x1 = self.ui.cx_begin.value();x2 = self.ui.cx_end.value()
                y1 = self.ui.cy_begin.value();y2 = self.ui.cy_end.value()
                t1=self.ui.shour_2.value()*3600+self.ui.sminute_2.value()*60+self.ui.ssecond_2.value()
                t2=self.ui.dsecond_2.value()
                if t2==0.0:
                    t2=duration
                #震动模式
                if self.ui.curve.isChecked():
                    vf += f"scale={w1}:{h1}[wm];[0][wm]overlay=x={x1}+({x2}-{x1})*(t-{t1})/{t2}+12*sqrt(2)/2*sin(PI*6*t):y={y1}+({y2}-{y1})*(t-{t1})/{t2}+12*sqrt(2)/2*cos(6*PI*t):enable='between(t,{t1},{t1 + t2})'"
                #直线模式
                else:
                    vf +=f"scale={w1}:{h1}[wm];[0][wm]overlay=x={x1}+({x2}-{x1})*(t-{t1})/{t2}:y={y1}+({y2}-{y1})*(t-{t1})/{t2}:enable='between(t,{t1},{t1 + t2})'"
                FFLIST.append("-filter_complex");FFLIST.append(vf)
                FFLIST.append(output_file)
            else:
                raise Exception("请检查参数配置是否有误")


            self.Tran_thread(FFLIST,duration)
        except Exception as ERROR:
            self.creat_son.emit('E')
            self.Logger_(self).Commit_sl(ERROR)


#立体音效函数区
    #开启单音频处理进程
    def Get_s_audio(self):
        try:
            FFLIST=[]
            input_file=self.ui.input_file_9.toPlainText()
            output_file=self.default_path_s+"\\"+self.ui.input_file_10.toPlainText()+"."+(re.search("\\.(.*)",input_file)).group(1)
            if input_file=="" or output_file=="":
                raise Exception("路径文件不允许为空，啾！")
            duration = Creator.Get_duration(input_file)
            if duration == "N/A":
                duration = 0.2
            else:
                duration = float(duration)
            FFLIST.append("ffmpeg")
            FFLIST.append("-i");FFLIST.append(input_file)
            FFLIST.append("-y")
            if self.ui.dynamicsolid.isChecked():
                hz=None
                if self.ui.twist.isChecked():
                    if self.ui.switchspeed_2.currentText()=="缓慢":
                        hz=0.1
                    elif self.ui.switchspeed_2.currentText()=="正常":
                        hz=0.2
                    elif self.ui.switchspeed_2.currentText()=="快速":
                        hz=0.5
                    elif self.ui.switchspeed_2.currentText()=="晕眩":
                        hz=1
                    filter=f"-filter_complex asplit=2[a][b];[a]adelay=0|10,pan=stereo|c0=0.8*c0|c1=0.2*c0[left];[b]adelay=10|0,pan=stereo|c0=0.2*c0|c1=0.8*c0[right];[left][right]amix=inputs=2,apulsator=mode=sine:hz={hz}:amount=1 -ac 2"
                    FFLIST.extend(filter.split(" "))
                else:
                    if self.ui.switchspeed_2.currentText()=="缓慢":
                        hz=0.1
                    elif self.ui.switchspeed_2.currentText()=="正常":
                        hz=0.2
                    elif self.ui.switchspeed_2.currentText()=="快速":
                        hz=0.5
                    elif self.ui.switchspeed_2.currentText()=="晕眩":
                        hz=1
                    mode=None
                    if self.ui.switchmodel.currentText()=="机械切换":
                        mode="square"
                    elif self.ui.switchmodel.currentText()=="平滑切换":
                        mode="sine"
                    filter=f"-af apulsator=mode={mode}:hz={hz}:amount=1 -ac 2"
                    FFLIST.extend(filter.split(" "))


            else:
                if self.ui.staticmodel.currentText()=="轻音反射":
                    filter="ffmpeg -i dujiao.mp3 -af aecho=0.8:0.9:40|70:0.4|0.3,adelay=0|12,highpass=f=200,lowpass=f=6000,pan=stereo|c0=c0|c1=c1 v1.wav"
                    FFLIST.extend(filter.split(" "))
                elif self.ui.staticmodel.currentText()=="中度回响":
                    filter="-af aecho=0.8:0.88:120|180:0.5|0.4,adelay=0|30,highpass=f=150,lowpass=f=7000,stereotools=mode=ms>lr,apulsator=mode=sine:hz=0.2:amount=0.7"
                    FFLIST.extend(filter.split(" "))
                elif self.ui.staticmodel.currentText()=="迷幻狂欢":
                    filter="-af aecho=0.9:0.9:150|230:0.6|0.5,adelay=0|60,apulsator=mode=sine:hz=0.15:amount=1,stereotools=mode=ms>lr,highpass=f=120,lowpass=f=8000"
                    FFLIST.extend(filter.split(" "))

            FFLIST.append(output_file)

            self.Tran_thread(FFLIST,duration)
        except Exception as ERROR:
            self.creat_son.emit("E")
            self.Logger_(self).Commit_sl(ERROR)






    #多音频处理
    def Get_n_audio(self):
        try:
            input_file_left=self.ui.input_file_11.toPlainText()
            input_file_right=self.ui.input_file_12.toPlainText()
            output_file=self.default_path_s+"\\"+self.ui.input_file_13.toPlainText()+"."+self.ui.file_f_2.currentText()
            if input_file_left=="" or input_file_right=="" or  output_file=="":
                raise Exception("路径文件不允许为空，啾！")
            duration = Creator.Get_duration(input_file_left)
            if duration == "N/A":
                duration = 0.2
            else:
                duration = float(duration)
            FFLIST=[]
            FFLIST.append("ffmpeg")
            FFLIST.append("-i");FFLIST.append(input_file_left)
            FFLIST.append("-i");FFLIST.append(input_file_right)
            FFLIST.append("-y")
            if self.ui.secondmodel.currentText=="启用":
                filter="-filter_complex [0:a]pan=mono|c0=c0[a0];[1:a]pan=mono|c0=c0[a1];[a0][a1]amerge=inputs=2[a] -map [a] -ac 2"
                FFLIST.extend(filter.split(" "))
            else:
                filter="-filter_complex [0:a][1:a]amix=inputs=2:duration=longest[m];[m]apulsator=mode=sine:hz=0.08:amount=1[out] -map [out]"
                FFLIST.extend(filter.split(" "))
            FFLIST.append(output_file)

            self.Tran_thread(FFLIST,duration)
        except Exception as ERROR:
            self.creat_son.emit("E")
            self.Logger_(self).Commit_sl(ERROR)















#高级播放函数区(ffplay)
    def Get_player(self):
        try:
            self.ui.player.setEnabled(False)

            input_file=self.ui.input_file_8.toPlainText()
            if input_file=="":
                raise Exception("源文件路径不许为空，啾！")
            FFLIST=[]
            FFLIST.append("ffplay")
            FFLIST.append("-i")
            FFLIST.append(input_file)
            FFLIST.append("-stats")
            FFLIST.append("-loop")
            FFLIST.append("0")
            FFLIST.append("-showmode")
            if self.ui.playermodel.currentText()=="音频波形":
                FFLIST.append("1")
            elif self.ui.playermodel.currentText()=="音频频谱":
                FFLIST.append("2")


            Creator.Carry_fp(FFLIST,self.FPTP)
        except Exception as ERROR:
            self.creat_son.emit("E")
            self.Logger_(self).Commit_sl(ERROR)
        finally:
            self.ui.player.setEnabled(True)



#音频百科函数区
    #为了方便，在一开始时就会将文件的内容加载到类内
    #音频科普函数
    def Set_awiki(self):
        index=int(self.ui.astyle.currentIndex())
        TEXT="\n".join(self.AWIKI_TEXT[index*6:index*6+6])
        self.a_show_wiki_S.emit(TEXT)


    #视频科普函数
    def Set_vwiki(self):
        index=int(self.ui.vstyle.currentIndex())
        TEXT="\n".join(self.VWIKI_TEXT[index*6:index*6+6])
        self.v_show_wiki_S.emit(TEXT)



#高级设置函数区
    #修改默认浏览路径
    def Change_default_path(self):
        try:
            target=self.ui.default_path.toPlainText()
            if target=="":
                raise Exception("路径不能为空哦，啾！")
            self.configuration[2]=re.sub(re.search("\"(.*)\"",self.configuration[2]).group(1),target,self.configuration[2])
            with open(CONFIG_SETUP, "w", encoding="utf-8") as f:
                f.write("\n".join(self.configuration))
            self.default_path=target
            self.sl_S.emit("用户针对修改默认浏览路径的行为成功")
            self.logstatus.emit("设置成功")
        except Exception as ERROR:
            self.logstatus.emit("设置失败")
            Creator.Start_process(lambda: self.Show_sonwidgt('E'))
            self.Logger_(self).Commit_sl(ERROR)

    #修改存储路径
    def Change_default_path_s(self):
        try:
            target = self.ui.default_path_s.toPlainText()
            if target=="":
                raise Exception("路径不能为空哦，啾！")
            self.configuration[3]=re.sub(re.search("\"(.*)\"", self.configuration[3]).group(1), target, self.configuration[3])
            with open(CONFIG_SETUP, "w", encoding="utf-8") as f:
                f.write("\n".join(self.configuration))
            self.default_path_s=target
            self.logstatus.emit("设置成功")
        except Exception as ERROR:
            self.logstatus.emit("设置失败")
            Creator.Start_process(lambda: self.Show_sonwidgt('E'))
            self.Logger_(self).Commit_sl(ERROR)











