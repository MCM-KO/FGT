"""
日志通用模块
"""

from abc import abstractmethod

class SignLogger:
    """
    持久型信号日志
    适配于大多数pyside6信号接受型窗口日志
    要求信号传输与显示应当严格分离
    且将会以父类对象作为参数传递
    """
    def __init__(self, outer):
        self.outer = outer

    @abstractmethod
    def Write_file(self):
        """写入日志入口"""
        pass


    @abstractmethod
    def Delete_all(self, selection)->None:
        """删除日志入口"""
        pass


class SSignLogger:
    """
    一次性信号日志
    适配于配置于一次性安装写在界面
    """
    pass




