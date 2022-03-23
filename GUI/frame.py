import cv2
import sys
import re
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QThread, pyqtSignal
from tools import img_cv_to_qt

import torch

sys.path.append("../Tracking")
from demo.bytetrack import frames_track, Predictor
from yolox.exp import get_exp
from yolox.utils import get_model_info
from configs.configs import configs

import time

class frame():
    def __init__(self, framelabel, statusbar, labelTotalFrame, vedioSlider):
        self.videoCapture = None
        self.numFrames = 0
        self.imgFrames = []     # 储存所有图像帧
        self.frameId = 0
        self.statusBar = statusbar
        self.frameLabel = framelabel
        self.labelTotalFrame = labelTotalFrame
        self.vedioSlider = vedioSlider

        self.trackWorker = trackWorker(self) # 跟踪线程
        self.trackWorker.sinOut.connect(self.update_status)
        self.trackWorker.finished.connect(self.update_frames)

    # TODO: 适配文件夹; 状态栏加载
    def init_frame(self, path):
        self.imgFrames = []
        self.videoCapture = cv2.VideoCapture(path)
        rval = self.videoCapture.isOpened()
        
        while rval: 
            rval, frame = self.videoCapture.read()  
            if rval:
                self.imgFrames.append(frame)
        self.trackWorker.load_frames(self.imgFrames) # 跟踪加载图片帧
        self.numFrames = len(self.imgFrames) # 获取视频的总帧数
        frame_0 = self.imgFrames[0]
        Qframe_0 = img_cv_to_qt(frame_0)
        return Qframe_0, self.numFrames

    def change_frame(self, num):
        n = num - 1
        frame_n = self.imgFrames[n]
        Qframe_n = img_cv_to_qt(frame_n)
        return Qframe_n
    
    def track_frame(self):
        self.trackWorker.start()

    def update_status(self, message):
        self.statusBar.showMessage(message)
        if re.search(r'.*(0).+/.*', message):
            self.frameLabel.setPixmap(QtGui.QPixmap.fromImage(img_cv_to_qt(self.imgFrames[0])))
        self.labelTotalFrame.setText(str(len(self.imgFrames)))
        self.vedioSlider.setMaximum(len(self.imgFrames))
        
    def update_frames(self):
        self.imgFrames = self.trackWorker.imgFrames
    

class trackWorker(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, frame):
        super().__init__()
        self.imgFrames = []
        self.frame = frame

    def load_frames(self, imgframes):
        self.imgFrames = imgframes
		
    def run(self):
        self.track_frame()

    # TODO: config, print -> logger, 第一帧不会变化, 若无视频则退出
    def track_frame(self):
        cfg = configs("../Tracking/configs/bytetrack_m.yaml")
        exp = get_exp(cfg.exp_file, cfg.name)
        cfg.device = torch.device("cuda" if cfg.device == "gpu" else "cpu")
        self.sinOut.emit("初始化模型")
        model = exp.get_model().to(cfg.device)
        print("Model Summary: {}".format(get_model_info(model, exp.test_size)))
        model.eval()
        
        # main()
        ckpt_file = cfg.ckpt
        print("loading checkpoint")
        self.sinOut.emit("加载模型权重")

        ckpt = torch.load(ckpt_file, map_location="cpu")
        model.load_state_dict(ckpt["model"])
        print("loaded checkpoint done.")
        self.sinOut.emit("模型权重加载完成")

        trt_file = None
        decoder = None
        predictor = Predictor(model, exp, trt_file, decoder, cfg.device, cfg.fp16)
        self.imgFrames = frames_track(exp, predictor, self.imgFrames, cfg, self.sinOut, self.frame)
        






