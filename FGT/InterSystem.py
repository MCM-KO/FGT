import platform
import subprocess
from PySide6.QtWidgets import QFileDialog
import re

#解析操作系统信息
class Parse:
    def __new__(cls):
        raise Exception("not instances")

    #返回操作系统界面
    @staticmethod
    def Get_OS():
        return platform.system()




#向操作系统发出交互命令（ffmpeg相关指令封装在ProccessCreator中）
class Execute:
    #规范工具类
    def __new__(cls):
        raise Exception("not instances")
    def __init_subclass__(cls):
        raise Exception("not inherit")


    @staticmethod
    #文件绑定函数
    def Connect_path(sign,window,default_path):
        directory,_ = QFileDialog.getOpenFileName(
            window,
            "选择文件位置",  # 对话框标题
            default_path,  # 设置默认路径
            "All Files (*)"
        )
        if directory=="":
            return
        getattr(window,f"{sign}").emit(str(directory))

    @staticmethod
    #目录绑定函数
    def Connect_dir(sign,window,default_path):
        directory = QFileDialog.getExistingDirectory(
            window,
            "选择目录位置",  # 对话框标题
            default_path,  # 设置默认路径
        )
        if directory=="":
            return
        getattr(window,f"{sign}").emit(str(directory))


    #拉取目标资源
    @staticmethod
    def Curl_target(command,window,PP):
        result=subprocess.Popen(
            command,
            stderr=subprocess.PIPE,
            text=True,
        )
        PP.append(result)
        for line in result.stderr:
            #显示进度条
            percentage=re.search("(\\d*\\.\\d*)%",line)
            if percentage!=None:
                percentage=float(percentage.group(1))
                window.set_progressBar.emit(percentage)



    #拉取目标资源大小（方便进度条处理）
    @staticmethod
    def Curl_target_size(command,PP):
        result = subprocess.Popen(
            command,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        PP.append(result)
        for line in result.stderr:
            size = re.search("Content-Length:(.*)", line).group(1)
            if size != "":
                result.terminate()  # 终止进程
                return int(size)


    #解压目标资源
    @staticmethod
    def Tar_file(file,FILE,PP):
        command=f"tar -xf {file} -C {FILE}"
        result=subprocess.Popen(
            command,
        )
        PP.append(result)
        result.wait()



    #删除文件
    @staticmethod
    def Delete_file(file,PP):
        command=f"del /f {file}"
        result=subprocess.Popen(
            command,
        )
        PP.append(result)
        result.wait()


    #设置环境变量(处理时间极短且危险程度极低的暂不考虑维护进程)
    @staticmethod
    def Set_PATH(file_path):
        command=rf"setx PATH {file_path};%PATH%"
        result=subprocess.Popen(
            command.split(" "),
            stdout=subprocess.PIPE,
        )









