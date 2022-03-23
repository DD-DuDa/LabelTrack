import sys

from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QApplication,QGraphicsScene,QGraphicsView,QGraphicsRectItem,QMainWindow,QLabel,QGraphicsItem,QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtCore import Qt,pyqtSignal,QPoint,QRectF

class QMyGraphicsView(QGraphicsView):
    sigMouseMovePoint=pyqtSignal(QPoint)
    sigMousePressPoint = pyqtSignal(QPoint)
    sigMouseReleasePoint = pyqtSignal(QPoint)
    #自定义信号sigMouseMovePoint，当鼠标移动时，在mouseMoveEvent事件中，将当前的鼠标位置发送出去
    #QPoint--传递的是view坐标
    def __init__(self,parent=None):
        super(QMyGraphicsView,self).__init__(parent)
        self.flag = False

    def mousePressEvent(self, evt):
        self.item = self.get_item_at_click(evt)
        if self.item is not None:
            self.flag = True
            print('self.item: ', self.item)
        else:
            self.flag = False
            print('self.item is None')

        pt=evt.pos()  #获取鼠标坐标--view坐标
        self.sigMousePressPoint.emit(pt) #发送鼠标位置
        QGraphicsView.mousePressEvent(self, evt)

    def mouseMoveEvent(self, evt):
        pt=evt.pos()  #获取鼠标坐标--view坐标
        self.sigMouseMovePoint.emit(pt) #发送鼠标位置
        QGraphicsView.mouseMoveEvent(self, evt)

    def mouseReleaseEvent(self, evt):
        pt=evt.pos()  #获取鼠标坐标--view坐标
        self.sigMouseReleasePoint.emit(pt) #发送鼠标位置
        QGraphicsView.mouseReleaseEvent(self, evt)

    def get_item_at_click(self, e):
        pos = e.pos()
        item = self.itemAt(pos)
        return item


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(600,400)
        self.view=QMyGraphicsView()  #创建视图窗口
        self.setCentralWidget(self.view) # 设置中央控件
        self.statusbar=self.statusBar()  #添加状态栏
        self.labviewcorrd=QLabel('view坐标:')
        self.labviewcorrd.setMinimumWidth(150)
        self.statusbar.addWidget(self.labviewcorrd)
        self.labscenecorrd=QLabel('scene坐标：')
        self.labscenecorrd.setMinimumWidth(150)
        self.statusbar.addWidget(self.labscenecorrd)
        self.labitemcorrd = QLabel('item坐标：')
        self.labitemcorrd.setMinimumWidth(150)
        self.statusbar.addWidget(self.labitemcorrd)


        rect = QRectF(-200, -100, 400, 200)
        self.scene=QGraphicsScene(rect)  #创建场景
        #参数：场景区域
        #场景坐标原点默认在场景中心---场景中心位于界面中心
        self.view.setScene(self.scene)  #给视图窗口设置场景
        item1=QGraphicsRectItem(rect)  #创建矩形---以场景为坐标
        item1.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)  #给图元设置标志
        #QGraphicsItem.ItemIsSelectable---可选择
        #QGraphicsItem.ItemIsFocusable---可设置焦点
        #QGraphicsItem.ItemIsMovable---可移动
        #QGraphicsItem.ItemIsPanel---
        self.scene.addItem(item1)  #给场景添加图元
        for pos,color in zip([rect.left(),0,rect.right()],[Qt.red,Qt.yellow,Qt.blue]):
            item=QGraphicsEllipseItem(-50,-50,100,100)  #创建椭圆--场景坐标
            #参数1 参数2  矩形左上角坐标
            #参数3 参数4 矩形的宽和高
            item.setPos(pos,0)  #给图元设置在场景中的坐标(移动图元)--图元中心坐标
            item.setBrush(color)  #设置画刷
            item.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)
            self.scene.addItem(item)
        self.scene.clearSelection()  #【清除选择】
        self.view.sigMouseMovePoint.connect(self.slotMouseMovePoint)
        self.view.sigMousePressPoint.connect(self.slotMousePressPoint)
        self.view.sigMouseReleasePoint.connect(self.slotMouseReleasePoint)

        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.x_real = 0
        self.y_real = 0
        # self.edges = []
        # self.flag=False

    def slotMouseMovePoint(self,pt):

        self.labviewcorrd.setText('view坐标:{},{}'.format(pt.x(),pt.y()))
        ptscene=self.view.mapToScene(pt)  #把view坐标转换为场景坐标

        self.x_real = ptscene.x()
        self.y_real = ptscene.y()

        self.labscenecorrd.setText('scene坐标:{:.0f},{:.0f}'.format(ptscene.x(),ptscene.y()))

        item=self.scene.itemAt(ptscene,self.view.transform())  #在场景某点寻找图元--最上面的图元
        #返回值：图元地址
        #参数1 场景点坐标
        #参数2 ？？？？
        if item != None:
            ptitem=item.mapFromScene(ptscene)  #把场景坐标转换为图元坐标
            self.labitemcorrd.setText('item坐标:{:.0f},{:.0f}'.format(ptitem.x(),ptitem.y()))
            # 这里可以设旗子
            # edge = Edge(self.scene, [self.x1, self.y1], [self.x_real, self.y_real])
            # edge.repaint(self.x1, self.y1, self.x_real, self.y_real)
        # if not self.view.flag:
        #     edge = Edge(self.scene, [self.x1, self.y1], [self.x_real, self.y_real])
            # edge.repaint(self.x1, self.y1, self.x_real, self.y_real)

    def slotMousePressPoint(self,pt):
        ptscene = self.view.mapToScene(pt)  # 把view坐标转换为场景坐标

        if not self.view.flag:
            e = MyQGraphicsEllipseItem()
            e.setPos(ptscene.x(), ptscene.y())
            e.pos = 1  # 标志是左上角
            self.scene.addItem(e)
            print('press: ', ptscene)

        self.x1 = ptscene.x()
        self.y1 = ptscene.y()
        print('x1:', self.x1, 'y1', self.y1)
        # self.x1 = pt.x()
        # self.y1 = pt.y()

    def slotMouseReleasePoint(self,pt):
        ptscene = self.view.mapToScene(pt)  # 把view坐标转换为场景坐标

        self.x2 = ptscene.x()
        self.y2 = ptscene.y()
        print('x2:', self.x2, 'y2', self.y2)

        if not self.view.flag:
            e = MyQGraphicsEllipseItem()
            e.setPos(ptscene.x(), ptscene.y())
            e.pos = 2
            self.scene.addItem(e)
            self.edge = Edge(self.scene, [self.x1, self.y1], [self.x2, self.y2])
            self.edge.drawEdges()
        else:
            if self.view.item.pos == 1:
                print('pos: ', self.view.item.pos)
                self.edge.repaint1(self.x2, self.y2)
                # 有时候鼠标选中的是左上或右下点，但实际选中的是线，所以也要给线赋值
            elif self.view.item.pos == 2:
                self.edge.repaint2(self.x2, self.y2)
                print('release:', self.view.item)

    # def get_item_at_click(self, e):
    #     pos = e.pos()
    #     item = self.itemAt(pos)
    #     return item


class MyQGraphicsEllipseItem(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setRect(0, 0, 10, 10)
        self.pos = 0  # 等于1是左上角，等于2是右下角

        pen = QPen()
        pen.setColor(Qt.blue)
        self.setPen(pen)


class Edge:

    def __init__(self, scene, star_point, end_point, parent=None):
        self.start_point = star_point
        self.end_point = end_point
        self.scene = scene

        self.x1 = self.start_point[0]
        self.y1 = self.start_point[1]
        self.x2 = self.end_point[0]
        self.y2 = self.end_point[1]

    def drawEdges(self):
        self.l1 = QGraphicsLineItem(self.x1, self.y1, self.x2, self.y1)
        self.scene.addItem(self.l1)
        self.l1.pos = 1

        self.l2 = QGraphicsLineItem(self.x2, self.y1, self.x2, self.y2)
        self.scene.addItem(self.l2)
        self.l2.pos = 2

        self.l3 = QGraphicsLineItem(self.x1, self.y1, self.x1, self.y2)
        self.scene.addItem(self.l3)
        self.l3.pos = 1

        self.l4 = QGraphicsLineItem(self.x1, self.y2, self.x2, self.y2)
        self.scene.addItem(self.l4)
        self.l4.pos = 2

    def repaint2(self, x2, y2):
        self.x2 = x2
        self.y2 = y2

        self.repaint()

    def repaint1(self, x1, y1):
        self.x1 = x1
        self.y1 = y1
        self.repaint()

    def repaint(self):
        self.scene.removeItem(self.l1)
        self.l1.setLine(self.x1, self.y1, self.x2, self.y1)
        self.scene.addItem(self.l1)

        self.scene.removeItem(self.l2)
        self.l2.setLine(self.x2, self.y1, self.x2, self.y2)
        self.scene.addItem(self.l2)

        self.scene.removeItem(self.l3)
        self.l3.setLine(self.x1, self.y1, self.x1, self.y2)
        self.scene.addItem(self.l3)

        self.scene.removeItem(self.l4)
        self.l4.setLine(self.x1, self.y2, self.x2, self.y2)
        self.scene.addItem(self.l4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
