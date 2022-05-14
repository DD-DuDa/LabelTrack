from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import torch
import time
sys.path.append("./Tracking")
from demo.bytetrack import frames_track, Predictor
from yolox.exp import get_exp
from yolox.utils import get_model_info
from configs.configs import configs

class trackWorker(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, canvas):
        super().__init__()
        self.imgFrames = []
        self.canvas = canvas
        self.model = None

    def load_frames(self, imgframes):
        self.imgFrames = imgframes
		
    def load_model(self, model):
        self.model = model
        print(self.model)

    def run(self):
        self.track_frame()

    # TODO: config, print -> logger, 第一帧不会变化, 若无视频则退出
    def track_frame(self):
        if self.model is not None:
            if "byte" in self.model:
                cfg = configs("./Tracking/configs/bytetrack_m.yaml")
            elif "tiny_vd" in self.model:
                cfg = configs("./Tracking/configs/yolox_tiny_vd.yaml")
            elif "m_vd" in self.model:
                cfg = configs("./Tracking/configs/yolox_m_vd.yaml")
            elif "l_vd" in self.model:
                cfg = configs("./Tracking/configs/yolox_l_vd.yaml")

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
        self.imgFrames = frames_track(exp, predictor, self.imgFrames, cfg, self.sinOut, self.canvas)