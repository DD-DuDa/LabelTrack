from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import time

class loadWorker(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, canvas):
        super().__init__()
        self.labelPath = ""
        self.canvas = canvas

    def run(self):
        self.load_label()
    
    def load_path(self, labelPath):
        self.labelPath = labelPath

    def load_label(self):
        with open(self.labelPath, "r") as f:
            count = len(open(self.labelPath,'rU').readlines())
            for i, line in enumerate(f.readlines(), 1):
                line = line.strip('\n').split(',')
                tlwh = [int(line[2]), int(line[3]), int(line[4]), int(line[5])]
                self.canvas.update_shape(int(line[1]), int(line[0]), "person", tlwh, float(line[6]), 'L')
                if i % 10 == 0:
                    self.sinOut.emit("标注框已加载 {} / {}".format(i, count))
        self.sinOut.emit("标注文件已加载完成")
