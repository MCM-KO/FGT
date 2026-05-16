import subprocess
import re
import time
import datetime
from idlelib.pyparse import trans
#泛型定义
from threading import Thread
from typing import Callable, TypeVar, ParamSpec
P = ParamSpec("P")
R = TypeVar("R")


#用于存放ffmpeg交互线程启动口和非操作系统交互型启动口
class Creator:
    def __new__(cls):
        raise Exception("no instances")

    def __init_subclass__(cls):
        raise Exception("no herit")


    @staticmethod
    def Start_process(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> Thread:
        #泛型线程启动函数
        t = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t


    @staticmethod
    def Get_duration(input_file):
        # 获取视频时长的进程函数
        result=subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                input_file
            ],
            stdout=subprocess.PIPE,
            text=True
        ).stdout.strip()
        return result

    #P-I
    @staticmethod
    def Carry_ff(FFLIST,WaitWindow,duration,PP):
        # 执行ffmpeg命令行函数
        time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
        result=subprocess.Popen(
            FFLIST,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
            encoding="utf-8"
        )
        PP.append(result)
        LOG=""
        for line in result.stderr:
            LOG+=line
            match = time_pattern.search(line)
            if match and duration:
                h, m, s = match.groups()
                current = int(h) * 3600 + int(m) * 60 + float(s)
                percent = int(current / duration * 100)
                percent = max(0, min(100, percent))
                WaitWindow.setpercentage.emit(percent)
        result.wait()
        return LOG


    #P-I
    @staticmethod
    def Carry_fp(FFLIST,FPTP):
        # 执行ffplay的播放函数
        print(FFLIST)
        result=subprocess.Popen(
            FFLIST,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        FPTP.append(result)




