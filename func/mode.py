import os
import glob
import re
from abc import ABC


class Explore(ABC):

    def recurse_dirs(self, file=None):
        format = '{} {} {} {}'
        for f in os.listdir(file):
            if os.path.isdir(os.path.join(file, f)):
                print("Dir %s" % f)
            else:
                print("File %s" % f)
        print("---end")
        self.recurse_dirs(os.path.join(file, input()))

    def lookup(self, file=None):
        with open(file, 'rb') as f:
            print(f.read())

    def create(self, file=None, content=None):
        with open(file, "r+") as f:
            f.write(str(content))

    def delete(self, path=None):
        os.unlink(path)


class CommandMode(ABC):

    def __init__(self):
        super(CommandMode, self).__init__();

    def find(self, pattern):
        regex = re.Pattern(pattern, pattern)
        return regex.findall()


if __name__ == '__main__':
    Explore().recurse_dirs("/home/taylor")
