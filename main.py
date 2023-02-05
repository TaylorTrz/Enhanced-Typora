import sys
import func.win as win
import gui.board as board

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    bin_dict = {
        "cmd": r"C:\Windows\System32\cmd.exe",
        "typora": r"C:\Users\taylor Tao\gateway\software\Typora\Typora.exe"
    }

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = board.Ui_MainWindow()
        self.ui.setupUi(self)
        self.add_action()

    def open_exe(self, file=None, name='typora'):
        process = QtCore.QProcess()
        process.start(self.bin_dict.get(name), [file])
        (title, handle) = win.start(file=file, name=name, parent=self.ui.tabWidget)
        print("processId: " + str(process.processId()))
        print("handle hex: " + hex(handle))
        tWindow = QtGui.QWindow.fromWinId(handle)
        tWindow.setFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        tWindow.setFlag(QtCore.Qt.CustomizeWindowHint, True)
        tWidget = QtWidgets.QWidget.createWindowContainer(tWindow)
        tWidget.setProperty("process", process)
        process.setParent(tWidget)
        self.ui.horizontalLayout.addWidget(tWidget)
        self.ui.tabWidget.addTab(tWidget, title)
        self.ui.tabWidget.setCurrentWidget(tWidget)

    def open_file(self, file_type="*.*"):
        file_tuple = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", '', 'Markdown files(*.md)')
        print("tuple: " + str(file_tuple))
        return file_tuple[0]

    def open_config(self):
        file_tuple = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", '', 'Typora可执行文件(*.*)')
        print("tuple: " + str(file_tuple))
        self.bin_dict.update({'typora': file_tuple[0]})

    def add_action(self):
        self.ui.tabWidget.tabCloseRequested['int'].connect(self.tab_close)
        self.ui.actionOpen.triggered.connect(lambda: self.open_exe(self.open_file()))
        self.ui.actionNew.triggered.connect(lambda: self.open_exe())
        self.ui.actionConfig.triggered.connect(lambda: self.open_config())
        self.ui.actionClose.triggered.connect(lambda: self.ui.statusbar.showMessage("tool close?", 500))

    def tab_close(self, index: int):
        """Close cursor-focus tab widget and kill sub process."""
        print("close tab index: " + str(index))
        widget = self.ui.tabWidget.widget(index)
        if self.ui.tabWidget.tabsClosable():
            process = widget.property("process")
            if type(process) == QtCore.QProcess:
                print("remove process: " + str(process.processId()))
                process.kill()
                del process
            self.ui.tabWidget.removeTab(index)
            widget.close()

    def init_tree(self):
        self.fileSystem = QtWidgets.QFileSystemModel()
        self.fileSystem.setRootPath("C:\\")
        self.ui.exploreTree.setModel(self.fileSystem)
        self.ui.exploreTree.setAnimated(True)
        self.ui.exploreTree.setIndentation(20)
        self.ui.exploreTree.setSortingEnabled(True)

    # def keyPressEvent(self, event):
    #     key = event.key()
    #     info = lambda k: \
    #         self.statusBar().showMessage(str(k), 500)
    #     if QtCore.Qt.Key_A <= key <= QtCore.Qt.Key_Z:
    #         if event.modifiers() & QtCore.Qt.ShiftModifier:
    #             info("shift+%s" % chr(key))
    #         elif event.modifers() & QtCore.Qt.ControlModifier:
    #             info("control+%s" % chr(key))
    #         else:
    #             info("abc")
    #     elif key == QtCore.Qt.Key_Home:
    #         info("home")
    #     elif key == QtCore.Qt.Key_Colon:
    #         info("colon")
    #     elif key == QtCore.Qt.Key_Slash:
    #         info("slash")
    #     elif key == QtCore.Qt.Key_Escape:
    #         info("escape")
    #     else:
    #         super().keyPressEvent(event)


def run():
    # 高分屏适配
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    # 启动
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    # 加载Icon
    icon = QtGui.QIcon(r"resources/icon/typora-file-icon@2x.png")
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run()
