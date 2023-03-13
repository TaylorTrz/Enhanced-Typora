import sys
import func.win as win
import gui.board as board
import gui.resources_rc  # type: ignore
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

default_interval = 10 * 1000


class WorkThread(QtCore.QThread):
    prop = {}

    def __init__(self, file, name, exe, tabWidget):
        self.file = file
        self.name = name
        self.exe = exe
        self.tabWidget = tabWidget
        super(WorkThread, self).__init__()

    def open_exe(self):
        """Open typora in this thread."""
        try:
            process = QtCore.QProcess()
            process.start(self.exe, [self.file])
            (title, handle) = win.start(file=self.file, name=self.name,
                                        parent=self.tabWidget)
            print("processId: " + str(process.processId()))
            print("handle hex: " + hex(handle))
        except Exception as e:
            print(e.__traceback__)
            raise e

        self.prop.update({'title': title})
        self.prop.update({'process': process})
        self.prop.update({'handle': handle})

    def run(self):
        self.open_exe()


class MainWindow(QtWidgets.QMainWindow):
    bin_dict = {
        "cmd": r"C:\Windows\System32\cmd.exe",
        "typora": r"C:\Users\taylor Tao\gateway\software\Typora\Typora.exe"
    }
    proc_dict = {}
    thr_dict = {}

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = board.Ui_MainWindow()
        self.ui.setupUi(self)
        self.add_action()

    def start_thread(self, file=None, name='typora'):
        """Running subProcess in a thread in case of blocking."""
        exe = self.bin_dict.get(name, None)
        if not exe:
            self.statusBar().showMessage("Set your Typora path correctly!", 2000)
            return
        thr = WorkThread(file, name, exe, self.ui.tabWidget)
        thr.start()
        thr.wait(10 * 1000)
        # wait until process and title
        handle = thr.prop.get('handle')
        title = thr.prop.get('title')
        process = thr.prop.get('process')
        # Set parent window
        from ctypes import windll
        windll.user32.SetParent(handle, int(self.ui.tabWidget.winId()))
        # Set window to QWidget
        window = QtGui.QWindow.fromWinId(handle)
        window.setFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        window.setFlag(QtCore.Qt.CustomizeWindowHint, True)
        widget = QtWidgets.QWidget.createWindowContainer(window)
        # Set layout
        self.ui.horizontalLayout.addWidget(widget)
        self.ui.tabWidget.addTab(widget, title)
        self.ui.tabWidget.setCurrentWidget(widget)
        index = self.ui.tabWidget.currentIndex()
        self.ui.tabWidget.setTabIcon(index, QtGui.QIcon(":/icon"))
        # Bind widget with process and thread
        self.proc_dict.update({id(widget): process})
        self.thr_dict.update({id(widget): thr})

    def open_file(self, file_type="*.*"):
        file_tuple = QtWidgets.QFileDialog.getOpenFileName(self, "Choose file", '', 'Markdown files(*.md)')
        print("tuple: " + str(file_tuple))
        return file_tuple[0]

    def open_config(self):
        file_tuple = QtWidgets.QFileDialog.getOpenFileName(self, "Choose file", '', 'Typora可执行文件(*.*)')
        print("tuple: " + str(file_tuple))
        self.bin_dict.update({'typora': file_tuple[0]})

    def add_action(self):
        self.ui.tabWidget.tabCloseRequested['int'].connect(self.tab_close)
        self.ui.actionOpen.triggered.connect(lambda: self.start_thread((self.open_file())))
        self.ui.actionNew.triggered.connect(lambda: self.start_thread())
        self.ui.actionConfig.triggered.connect(lambda: self.open_config())
        self.ui.actionClose.triggered.connect(lambda: sys.exit(0))
        # self.ui.actionClose.triggered.connect(lambda: QtCore.QCoreApplication.instance().exit(0))

    def tab_close(self, index: int):
        """Close cursor-focus tab widget and kill sub process."""
        print("close tab index: " + str(index))
        widget = self.ui.tabWidget.widget(index)
        if self.ui.tabWidget.tabsClosable():
            process = self.proc_dict.get(id(widget), None)
            if process and isinstance(process, QtCore.QProcess):
                # TODO: Send signal (SIGTERM instead of SIGKILL)
                # Wait for process to totally shutdown
                # count = 0
                # interval = 0.1
                # while not process.waitForFinished(int(interval * 1000)):
                #     if count > 10:
                #         self.statusBar().showMessage("Wait for user to close.", 2000)
                #         process.kill()
                #         break
                #     print("wait for process {} to be shutdown gracefully.".format(
                #         str(process.processId())))
                #     count += 1
                print("remove process: %s" % str(process.processId()))
                process.terminate()
                del process
                self.proc_dict.pop(id(widget))
            # Also exit thread in case of unexpected shutdown all action
            thread = self.thr_dict.get(id(widget))
            if thread and isinstance(thread, QtCore.QThread):
                thread.deleteLater()
                thread.exit(0)
                self.thr_dict.pop(id(widget))
                del thread
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
    window.setWindowIcon(QtGui.QIcon(":/icon"))
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run()
