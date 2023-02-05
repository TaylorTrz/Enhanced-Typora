import sys
import typing

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from PyQt5.QtGui import QWindow
from PyQt5 import QtCore
from ctypes import *

"""https://blog.csdn.net/hodors/article/details/105999738 """


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.left = 50
        self.top = 50
        self.width = 1200
        self.height = 800
        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()


if __name__ == '__main__':
    FindWindow = windll.user32.FindWindowW
    SetParent = windll.user32.SetParent
    SetWindowPos = windll.user32.SetWindowPos
    # 这里得提前打开一个名为Typora的文件，在任务管理器看看，名字必须一致，然后才能嵌入
    notepad_handle = FindWindow(0, "Typora")
    print(notepad_handle)

    app = QApplication(sys.argv)
    ex = App()
    SetParent(notepad_handle, int(ex.winId()))
    SetWindowPos(notepad_handle, 0, 100, 100, 400, 600, 0)
    widget = QWidget.createWindowContainer(QWindow.fromWinId(notepad_handle), ex,
                                           QtCore.Qt.WindowType.FramelessWindowHint)
    gridLayout = QGridLayout(ex)
    gridLayout.setObjectName("gridLayout")
    gridLayout.addWidget(widget, 0, 0, 1, 1)
    ex.show()
    sys.exit(app.exec_())
