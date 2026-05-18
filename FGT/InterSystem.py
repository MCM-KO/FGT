from typing import NoReturn
import shutil
import sys
from pathlib import Path
import platform
import subprocess
from PySide6.QtWidgets import QFileDialog
import re

#解析操作系统信息
class Parse:
    def __new__(cls) -> NoReturn:
        raise Exception("not instances")

    @staticmethod
    def Get_OS() -> str:
        """返回操作系统界面"""
        return platform.system()




#向操作系统发出交互命令（ffmpeg相关指令封装在ProccessCreator中）
class Execute:
    def __new__(cls) -> NoReturn:
        """规范工具类"""
        raise Exception("not instances")
    def __init_subclass__(cls) -> None:
        raise Exception("not inherit")


    @staticmethod
    def Connect_path(sign,window,default_path) -> None:
        """文件绑定函数"""
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
    def Connect_dir(sign,window,default_path) -> None:
        """目录绑定函数"""
        directory = QFileDialog.getExistingDirectory(
            window,
            "选择目录位置",  # 对话框标题
            default_path,  # 设置默认路径
        )
        if directory=="":
            return
        getattr(window,f"{sign}").emit(str(directory))


    @staticmethod
    def Curl_target(command,window,PP) -> None:
        """拉取目标资源"""
        result=subprocess.Popen(
            command,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        PP.append(result)
        for line in result.stderr:
            #显示进度条
            percentage=re.search("(\\d*\\.\\d*)%",line)
            if percentage!=None:
                percentage=float(percentage.group(1))
                window.set_progressBar.emit(percentage)



    @staticmethod
    def Curl_target_size(command,PP) -> int | None:
        """拉取目标资源大小（方便进度条处理）"""
        result = subprocess.Popen(
            command,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        PP.append(result)
        for line in result.stderr:
            size = re.search("Content-Length:(.*)", line).group(1)
            if size != "":
                result.terminate()  # 终止进程
                return int(size)


    @staticmethod
    def Tar_file(file, FILE, PP) -> None:
        """解压目标资源：.zip 用系统 tar，.7z 用 7-Zip。"""
        archive = Path(file)
        dest = Path(FILE)
        suffix = archive.suffix.lower().lstrip(".")
        if suffix == "zip":
            command = f'tar -xf "{archive}" -C "{dest}"'
        elif suffix == "7z":
            seven_z = shutil.which("7z") or shutil.which("7z.exe")
            if not seven_z:
                candidate = Path(r"C:\Program Files\7-Zip\7z.exe")
                seven_z = str(candidate) if candidate.is_file() else None
            if not seven_z:
                raise FileNotFoundError(
                    "解压 .7z 需要安装 7-Zip，或将 7z.exe 加入 PATH（https://www.7-zip.org/）"
                )
            command = f'"{seven_z}" x "{archive}" -o"{dest}" -y'
        else:
            raise ValueError(f"不支持的压缩格式: .{suffix}")
        result = subprocess.Popen(
            command,
            shell=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        PP.append(result)
        result.wait()
        if result.returncode != 0:
            raise RuntimeError(f"解压失败（退出码 {result.returncode}）: {archive.name}")



    @staticmethod
    def Delete_file(file,PP) -> None:
        """删除文件"""
        command=f"del /f {file}"
        result=subprocess.Popen(
            command,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        PP.append(result)
        result.wait()


    @staticmethod
    def Set_PATH(file_path) -> None:
        """设置环境变量(处理时间极短且危险程度极低的暂不考虑维护进程)"""
        command=rf"setx PATH {file_path};%PATH%"
        result=subprocess.Popen(
            command.split(" "),
            stdout=subprocess.PIPE,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    @staticmethod
    def Set_ink() -> None:
        """在桌面为当前已打包的 exe 创建快捷方式 FGT.lnk。"""
        exe = Path(sys.executable).resolve()
        target = str(exe)
        work_dir = str(exe.parent)

        def _sq(value: str) -> str:
            return value.replace("'", "''")

        ps = (
            "$desktop = [Environment]::GetFolderPath('Desktop');"
            "$lnk = Join-Path $desktop 'FGT.lnk';"
            "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk);"
            f"$s.TargetPath = '{_sq(target)}';"
            f"$s.WorkingDirectory = '{_sq(work_dir)}';"
            "$s.Description = 'FGT';"
            "$s.Save()"
        )
        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )









