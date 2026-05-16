
"""
高级图形库，是对pyside6中原生控件
不足或难以实现的复杂ui功能所设计的工具库
"""

from PySide6.QtGui import QPixmap, QPainter, QPainterPath, Qt


class UQLabel:
    def __new__(self):
        raise Exception("no instance")

    """
    对目标标签设置大小，并裁剪成圆
    """
    @staticmethod
    def Round(Label,picture_file,width,length):
        Label.setMinimumSize(width, length)
        Label.setMaximumSize(width, length)
        size = Label.size()
        src = QPixmap(f"{picture_file}").scaled(
            size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        result = QPixmap(size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size.width(), size.height())
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, src)
        painter.end()
        Label.setPixmap(result)

