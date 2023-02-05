import os


def abs_path():
    return \
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))


def icon_path():
    return r"resources/icon/typora.ico"
