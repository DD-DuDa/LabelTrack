import cv2
from PyQt5 import QtGui

# cv2读取的图片转成qt格式
def img_cv_to_qt(cv_img):
    # BGR => RGB 文件格式
    shrink = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    # cv 图片转换成 qt图片
    qtImg = QtGui.QImage(shrink.data, # 数据源
                          shrink.shape[1],  # 宽度
                          shrink.shape[0],	# 高度
                          shrink.shape[1] * 3, # 行字节数
                          QtGui.QImage.Format_RGB888)

    return qtImg
