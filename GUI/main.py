import os
import sys
import cv2
import logging
from multiprocessing import freeze_support

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget

from qt_material import apply_stylesheet, QtStyleTools, density

from tools import img_cv_to_qt
from label_combox import DefaultLabelComboBox
# from frame import frame
from canvas import canvas
from zoomWidget import ZoomWidget
from utils import *
from ustr import ustr
from tqdm import tqdm
from load_worker import loadWorker

# GPU渲染，加速
if hasattr(Qt, 'AA_ShareOpenGLContexts'):
    try:
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    except:
        QCoreApplication.set_attribute(Qt.AA_ShareOpenGLContexts)
else:
    print("'Qt' object has no attribute 'AA_ShareOpenGLContexts'")

freeze_support()


class MyWindow(QMainWindow, QtStyleTools):
    def __init__(self):
        super().__init__()

        self = uic.loadUi('ui_window.ui', self)
        self.setWindowTitle('Auto - LabelTrack')
        
        # 视频播放器
        self.player = QMediaPlayer() 
        # TODO 自定义Widget
        self.videoWiget = QVideoWidget()  # 独立窗口播放视频
        self.videoWiget.setMinimumSize(800, 600)
        self.videoFileUrl = ""
        self.filePath = ""
        self.labelPath = ""

        self.loadWorker = loadWorker(self.canvas)
        self.loadWorker.sinOut.connect(self.update_load_status)

        # 状态栏
        self.statusBar = self.statusBar() # 状态栏
        # Display cursor coordinates at the right of status bar
        self.label_coordinates = QLabel('Hello')
        self.statusBar.addPermanentWidget(self.label_coordinates)

        # 大小比例
        self.zoom_widget = ZoomWidget()

        # 按钮
        self.pushButtonPlay.pressed.connect(self.video_play)  # 播放按钮
        self.playTimer = QTimer(self)
        self.playTimer.timeout.connect(self.play_frame)
        self.isPlaying = False
        
        # 工具栏
        self.actionFile.triggered.connect(self.open_file)  # 打开文件
        self.actionSave.triggered.connect(self.save_file)
        self.actionDict.triggered.connect(self.open_dict)

        self.toolBarVertical.addWidget(self.zoom_widget)
        self.zoom_widget.setValue(100)
        self.zoom_widget.valueChanged.connect(self.paint_canvas)
        self.toolBarVertical.addAction(self.actionFit)
        self.toolBarVertical.addSeparator()

        self.actionFit.triggered.connect(self.adjust_scale)
        # 标签
        # TODO
        self.labelHint = ['person', 'car']
        self.defaultLabel = self.labelHint[0]
        self.labelCombobox = DefaultLabelComboBox(self, items = self.labelHint)
        self.toolBarVertical.addWidget(self.labelCombobox)
        self.toolBarVertical.addAction(self.actionAnnot)
        self.toolBarVertical.addSeparator()
        self.toolBarVertical.addAction(self.actionTrack)
        self.actionAnnot.triggered.connect(self.set_create_mode)
        self.actionTrack.triggered.connect(self.canvas.track_frame)  # 自动跟踪

        # 输入帧数栏
        self.lineCurFrame.returnPressed.connect(self.jump_frame)
        
        # 滑动条
        self.vedioSlider.setMinimum(1)
        self.vedioSlider.sliderMoved.connect(self.move_slider) 
        self.vedioSlider.valueChanged.connect(self.move_slider)

        # canvas 信号
        self.canvas.newShape.connect(self.new_shape)

        self.prev_label_text = ''

    # 打开文件
    def open_file(self):
        self.filePath, _ = QFileDialog.getOpenFileName(self, "Open file", "", "mp4 Video (*.mp4); files Directory(*.*)")
        if self.filePath.endswith('.mp4'):
            self.videoFileUrl = QUrl.fromLocalFile(self.filePath)
            # 初始化所有图像帧
            self.canvas.init_frame(self.filePath)
            self.adjust_scale()
            self.lineCurFrame.setText("1")
            self.labelTotalFrame.setText(str(self.canvas.numFrames))
            self.vedioSlider.setMaximum(self.canvas.numFrames)

    def open_dict(self):
        target_dir_path = ustr(QFileDialog.getExistingDirectory(self, 'Open Directory', '.', QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        self.canvas.init_frame(target_dir_path)
        self.adjust_scale()
        self.lineCurFrame.setText("1")
        self.labelTotalFrame.setText(str(self.canvas.numFrames))
        self.vedioSlider.setMaximum(self.canvas.numFrames)

    def play_frame(self):
        # self.playTimer.start(100 / 3)
        self.canvas.curFramesId += 1
        self.lineCurFrame.setText(str(self.canvas.curFramesId))
        self.vedioSlider.setValue(self.canvas.curFramesId)
        self.canvas.change_frame(self.canvas.curFramesId)
        if self.canvas.curFramesId > self.canvas.numFrames - 1:
            self.playTimer.stop()
            self.pushButtonPlay.setIcon(QIcon("resources/svg/play.svg"))
            self.pushButtonPlay.setText(" PLAY")

    # 加载标注文件 .txt
    def load_file(self):
        self.statusBar.showMessage("正在加载标注文件，请稍后")
        self.labelPath, _ = QFileDialog.getOpenFileName(self, "Choose annotation file", "", "txt(*.txt)")  
        self.loadWorker.load_path(self.labelPath)
        self.loadWorker.start()

    def update_load_status(self, message):
        self.statusBar.showMessage(message)

    # 图像帧滑条
    def move_slider(self, position):
        self.lineCurFrame.setText(str(position))
        self.jump_frame()

    # TODO 条件：没有文件时，超出范围
    # 跳转到某帧
    def jump_frame(self):
        num = int(self.lineCurFrame.text())
        self.canvas.curFramesId = num
        self.vedioSlider.setValue(num)
        self.canvas.change_frame(num)
        self.adjust_scale()

    # 播放视频
    def video_play(self):
        # self.player.setVideoOutput(self.videoWiget)  
        # self.player.setMedia(QMediaContent(self.videoFileUrl))  # 选取视频文件
        # self.videoWiget.show()
        # self.player.play()
        # self.canvas.curFramesId = 1
        if self.isPlaying is False:
            self.isPlaying = True
            self.pushButtonPlay.setIcon(QIcon("resources/svg/stop.svg"))
            self.pushButtonPlay.setText(" STOP")
            self.playTimer.start(33)
        else:
            self.isPlaying = False
            self.pushButtonPlay.setIcon(QIcon("resources/svg/play.svg"))
            self.pushButtonPlay.setText(" PLAY")
            self.playTimer.stop()

    def paint_canvas(self):
        # assert not self.image.isNull(), "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoom_widget.value()
        # self.canvas.label_font_size = int(0.02 * max(self.image.width(), self.image.height()))
        self.canvas.adjustSize()
        self.canvas.update()

    # 调节比例
    def adjust_scale(self, initial=False):
        # value = self.scalers[self.FIT_WINDOW if initial else self.zoom_mode]()
        self.canvas.pointPos = QPointF(0, 0)
        self.canvas.deltaPos = QPointF(0, 0)
        value = self.scale_fit_window()
        self.zoom_widget.setValue(int(100 * value))
        self.canvas.repaint()

    # 适应窗口
    def scale_fit_window(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.canvas.width()
        h1 = self.canvas.height()
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def toggle_draw_mode(self, edit=True):
        self.canvas.set_editing(edit)
        self.actionAnnot.setEnabled(edit)

    def set_create_mode(self):
        # assert self.advanced()
        self.toggle_draw_mode(False)

    def default_label_combo_selection_changed(self, index):
        self.defaultLabel = self.labelHint[index]

    # Callback functions:
    def new_shape(self):
        """Pop-up and give focus to the label editor.

        position MUST be in global coordinates.
        """
        # TODO
        text = self.defaultLabel
        self.prev_label_text = text
        generate_line_color, generate_fill_color = generate_color_by_text(text)
        shape = self.canvas.set_last_label(text, generate_line_color, generate_fill_color)
        # self.add_label(shape)
        self.canvas.set_editing(True) # edit mode
        self.actionAnnot.setEnabled(True)
        # self.set_dirty() # 发生更新，可以保存

    def current_path(self):
        return os.path.dirname(self.filePath) if self.filePath else '.'

    def save_file(self):
        # image_file_dir = os.path.dirname(self.filePath)
        # image_file_name = os.path.basename(self.filePath)
        # saved_file_name = os.path.splitext(image_file_name)[0]
        savedPath = self.save_file_dialog(remove_ext=False)
        self.save_labels(savedPath)
    
    def save_file_dialog(self, remove_ext=True):
        caption = 'Choose Path to save annotation'
        filters = 'Files Directory(*.*)'
        # TODO
        open_dialog_path = self.current_path()
        dlg = QFileDialog(self, caption, open_dialog_path, filters)
        # dlg.setDefaultSuffix(LabelFile.suffix[1:])
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        filename = os.path.splitext(self.filePath)[0] + '.txt'
        dlg.selectFile(filename)
        dlg.setOption(QFileDialog.DontUseNativeDialog, False)
        if dlg.exec_():
            full_file_path = ustr(dlg.selectedFiles()[0])
            if remove_ext:
                return os.path.splitext(full_file_path)[0]  # Return file path without the extension.
            else:
                return full_file_path
        return ''
        
    def save_labels(self, savedPath):
        results = []
        for shape in self.canvas.shapes:
            min_x = sys.maxsize
            min_y = sys.maxsize
            max_x = 0
            max_y = 0
            for point in shape.points:
                min_x = round(min(min_x, point.x()))
                min_y = round(min(min_y, point.y()))
                max_x = round(max(max_x, point.x()))
                max_y = round(max(max_y, point.y()))
            w = max_x - min_x
            h = max_y - min_y
            results.append(
                f"{shape.frameId},{shape.id},{min_x},{min_y},{w},{h},{shape.score:.2f},1,0,0\n"
            )
        with open(savedPath, 'w') as f:
            f.writelines(results)
            print(f"save results to {savedPath}")

    # 删除选中的框
    def delete_selected_shape(self):
        self.canvas.delete_selected()

    def keyPressEvent(self, ev):
        key = ev.key()
        if key == Qt.Key_Delete or key == Qt.Key_S:
            self.delete_selected_shape()

    def closeEvent(self, event):
        sys.exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MyWindow = MyWindow()
    apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)

    MyWindow.showMaximized()
    sys.exit(app.exec_())

