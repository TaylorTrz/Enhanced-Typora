import os
import sys
import time
import types

from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class FileInfoTableWidget(QTableWidget):
    global_row_font = QFont('微软雅黑', 8)

    def __init__(self, parent=None, rootdir=None):
        super(FileInfoTableWidget, self).__init__(parent=parent)
        self.parent = parent
        self.rootDir = rootdir
        self._initUI()

    def _initUI(self):
        self.setGeometry(2, 32, 394, 364)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setColumnCount(4)
        headerLabels = ['文件名', '大小', '类型', '修改时间']
        for index, h in enumerate(headerLabels):
            item = QTableWidgetItem()
            item.setFont(self.global_row_font)
            item.setText(h)
            self.setHorizontalHeaderItem(index, item)

    def mouseDoubleClickEvent(self, evt: QMouseEvent):
        if evt.button() == Qt.LeftButton:
            dir = self.item(self.currentRow(), 0).text()
            type = self.item(self.currentRow(), 2).text()
            tmp = os.path.join(self.rootDir, dir)
            if type == 'File Folder':
                self.rootDir = tmp
                UpdateRowsThread(self, self.parent.update_callback, [self.rootDir, ]).start()
            else:
                print(tmp)
                os.system(tmp)


class UpdateRowsThread(QThread):
    _rowSignal = pyqtSignal(str, list)

    def __init__(self, parent=None, callback=None, args=[]):
        super(UpdateRowsThread, self).__init__(parent=parent)
        if type(callback) is not types.MethodType:
            raise Exception('callback is`t function')
        self._rowSignal.connect(callback)
        self.args = args

    def run(self):
        dir = self.args[0]
        if os.path.isdir(dir):
            files = os.listdir(dir)
            print(files)
            if files:
                self._rowSignal.emit(os.path.abspath(dir), files)


class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self._initUI()

    def _initUI(self):
        self.setFixedSize(QSize(400, 400))
        self.combox = QComboBox(self)
        self.combox.setGeometry(0, 2, 200, 22)
        self.combox.setStyleSheet('border: 2px solid white;'
                                  'border-radius: 3px;'
                                  'padding: 1px 2px 1px 2px;'  # 针对于组合框中的文本内容
                                  'min-width: 9em;'
                                  )  # 组合框的最小宽度')
        self.combox.setEditable(True)
        dirs = QDir.drives()
        for fi in dirs:
            self.combox.addItem(fi.filePath())
        # ================浏览按钮
        self.btn_browser = QPushButton(self)
        self.btn_browser.setGeometry(210, 2, 60, 22)
        self.btn_browser.setText('浏览')
        self.btn_browser.setIcon(QIcon('./imgs/browser.png'))
        self.btn_browser.clicked.connect(self._btn_browser_clicked)
        # =================列表框
        self.currentPath = self.combox.currentText()
        self.fileInfoWidget = FileInfoTableWidget(self, self.currentPath)
        # ====更新线程
        UpdateRowsThread(self, self.update_callback, [self.currentPath]).start()
        self.show()

    def update_callback(self, absPath, rows):

        if self.fileInfoWidget.rowCount() > 0:
            for row in range(self.fileInfoWidget.rowCount()):
                self.fileInfoWidget.removeRow(0)
        for index, file in enumerate(rows):
            absFilePath = os.path.join(absPath, file)
            self.fileInfoWidget.insertRow(index)
            item0 = QTableWidgetItem()
            item0.setFont(self.fileInfoWidget.global_row_font)
            item0.setText(file)
            provider = QFileIconProvider()
            item0.setIcon(provider.icon(QFileInfo(absFilePath)))
            mtime = os.path.getmtime(absPath)
            self.fileInfoWidget.setRowHeight(index, 20)
            self.fileInfoWidget.setItem(index, 0, item0)
            # ============最后修改时间
            item1 = QTableWidgetItem()
            item1.setFont(self.fileInfoWidget.global_row_font)
            item1.setText(time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(int(mtime))))
            self.fileInfoWidget.setItem(index, 3, item1)
            # =============文件类型
            item2 = QTableWidgetItem()
            item2.setFont(self.fileInfoWidget.global_row_font)
            fileType = provider.type(QFileInfo(absFilePath))
            item2.setText(fileType)
            self.fileInfoWidget.setItem(index, 2, item2)
            # =============文件大小
            item3 = QTableWidgetItem()
            item3.setFont(self.fileInfoWidget.global_row_font)
            item3.setText(str(os.path.getsize(absPath)) + 'KB')
            self.fileInfoWidget.setItem(index, 1, item3)
        self.combox.setCurrentText(absPath)

    def _btn_browser_clicked(self):
        fileDialog = QFileDialog()
        fileDialog.setViewMode(QFileDialog.Detail)
        fileDir = QFileDialog.getExistingDirectory(self, '浏览文件', os.environ['USERPROFILE'] + '\\desktop')

    # signal


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
