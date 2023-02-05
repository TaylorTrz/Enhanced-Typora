import os
import sys
import time

from ctypes import windll, c_char_p


def start_typora(file=None, parent=None):
    """ start typora sub process

    :param parent:
    :param file:
    :return: window_class_name, window_handle
    """
    # 获取窗口名
    lClassName = str(os.path.split(file)[-1] + ' - Typora') \
        if file else "Typora"
    # 即使进程状态Running，但仍需要等待未知时间，且小时间间隔会导致异常结果，因此自旋
    handle = 0x0
    interval = 0.1
    while not handle and interval <= 10.0:
        handle = windll.user32.FindWindowW(c_char_p(None), lClassName)
        time.sleep(interval)
    # 设置父窗口
    windll.user32.SetParent(handle, int(parent.winId()))
    # NOTE(Taylor):
    # 1. Typora有个BUG，有时候必须先打开一个typora进程，才能正常在窗口内嵌入
    # 2. 进程kill后，可能无法触发Typora本身的优雅关闭，因此重启Typora后自动弹出
    return lClassName, handle


def start(name='typora', file=None, parent=None):
    return getattr(sys.modules[__name__], 'start_' + name)(file, parent)
