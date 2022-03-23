from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import cv2
from GUI.tools import img_cv_to_qt
from GUI.trackworker import trackWorker
from GUI.shape import Shape
from GUI.color import *
from GUI.utils import *

from GUI.label_dialog import LabelDialog

CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor

class canvas(QWidget):
    newShape = pyqtSignal()
    drawingPolygon = pyqtSignal(bool)

    CREATE, EDIT = list(range(2))

    epsilon = 11.0

    def __init__(self, *args, **kwargs):
        super(canvas, self).__init__(*args, **kwargs)
        self.trackWorker = trackWorker(self) # 跟踪线程
        self.trackWorker.sinOut.connect(self.update_status)
        self.numFrames = 0
        self.imgFrames = []  # 储存所有图像帧
        self.curFramesId = 1

        self.pixmap = QPixmap()
        self._painter = QPainter()
        self.drawing_line_color = QColor(0, 0, 255)
        self.drawing_rect_color = QColor(0, 0, 255)
        self.line = Shape(line_color=self.drawing_line_color)
        self.deltaPos = QPointF()
        self.prev_point = QPointF()
        self.prevRightPoint = QPointF()
        self.offsets = QPointF(), QPointF()
        self.scale = 1.0
        self.current = None
        self.mode = self.EDIT
        self.shapeId = 0
        self.selected_shape = None  # save the selected shape here
        self.shapes = []
        self.h_shape = None
        self.h_vertex = None
        self.window = self.parent().window()
        self.label_dialog = LabelDialog(parent=self, list_item=[])
        # TODO: 初始图片
        self.image = img_cv_to_qt(cv2.imread("./GUI/resources/images/MOT.png"))
        self.load_pixmap(QPixmap.fromImage(self.image))

        # Set widget options.
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)
    
    # TODO: 适配文件夹; 状态栏加载
    def init_frame(self, path):
        
        if os.path.isdir(path):
            files = get_image_list(path)
            for file in files:
                frame = cv2.imread(file)
                self.imgFrames.append(frame)
        else:
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
        self.load_pixmap(QPixmap.fromImage(Qframe_0))

    def change_frame(self, num):
        n = num - 1
        self.curFramesId = num
        frame_n = self.imgFrames[n]
        Qframe_n = img_cv_to_qt(frame_n)
        self.load_pixmap(QPixmap.fromImage(Qframe_n))

    def track_frame(self):
        self.trackWorker.load_frames(self.imgFrames)
        self.trackWorker.start()

    def update_status(self, message):
        self.window.statusBar.showMessage(message)
        # if re.search(r'.*(0).+/.*', message):
        #     self.frameLabel.setPixmap(QtGui.QPixmap.fromImage(img_cv_to_qt(self.imgFrames[0])))
        self.window.labelTotalFrame.setText(str(self.numFrames))
        self.window.vedioSlider.setMaximum(self.numFrames)
        self.repaint()

    def transform_pos(self, point):
        """Convert from widget-logical coordinates to painter-logical coordinates."""
        return point / self.scale - self.offset_to_center()

    def offset_to_center(self):
        s = self.scale
        area = super(canvas, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)

    def out_of_pixmap(self, p):
        w, h = self.pixmap.width(), self.pixmap.height()
        return not (0 <= p.x() <= w and 0 <= p.y() <= h)

    def finalise(self):
        assert self.current
        if self.current.points[0] == self.current.points[-1]:
            self.current = None
            self.drawingPolygon.emit(False)
            self.update()
            return

        self.shapeId += 1
        self.current.id = self.shapeId
        self.current.label = self.window.defaultLabel
        self.current.frameId = self.curFramesId
        self.current.score = 1
        self.current.close()
        self.shapes.append(self.current)
        self.current = None
        # self.set_hiding(False)
        self.newShape.emit()
        self.update()

    def update_shape(self, id, frameId, label, tlwh, score, auto = 'M'):
        detectPos = Shape()
        detectPos.id = id
        detectPos.frameId = frameId
        detectPos.label = label
        detectPos.score = score
        detectPos.auto = auto
        generate_line_color, generate_fill_color = generate_color_by_text(detectPos.label)
        self.set_shape_label(detectPos, detectPos.label, detectPos.id, generate_line_color, generate_fill_color)
        leftTop = QPointF(tlwh[0], tlwh[1])
        rightTop = QPointF(tlwh[0] + tlwh[2], tlwh[1])
        rightDown = QPointF(tlwh[0] + tlwh[2], tlwh[1] + tlwh[3])
        leftDown = QPointF(tlwh[0], tlwh[1] + tlwh[3])
        pointPos = [leftTop, rightTop, rightDown, leftDown]
        for pos in pointPos:
            if self.out_of_pixmap(pos):
                size = self.pixmap.size()
                clipped_x = min(max(0, pos.x()), size.width())
                clipped_y = min(max(0, pos.y()), size.height())
                pos = QPointF(clipped_x, clipped_y)
            detectPos.add_point(pos)
        
        detectPos.close()
        self.shapes.append(detectPos)
        detectPos = None
        # self.set_hiding(False)
        self.newShape.emit()
        self.update()

    def load_pixmap(self, pixmap):
        self.pixmap = pixmap
        # self.shapes = []
        self.repaint()

    def drawing(self):
        return self.mode == self.CREATE

    def handle_drawing(self, pos):
        if self.current and self.current.reach_max_points() is False:
            init_pos = self.current[0]
            min_x = init_pos.x()
            min_y = init_pos.y()
            target_pos = self.line[1]
            max_x = target_pos.x()
            max_y = target_pos.y()

            self.current.add_point(QPointF(max_x, min_y))
            self.current.add_point(target_pos)
            self.current.add_point(QPointF(min_x, max_y))

            self.finalise()
        elif not self.out_of_pixmap(pos):
            self.current = Shape()
            self.current.add_point(pos)
            self.line.points = [pos, pos]
            # self.set_hiding()
            self.drawingPolygon.emit(True)
            self.update()

    def set_editing(self, value=True):
        self.mode = self.EDIT if value else self.CREATE
        if not value:  # Create
            self.un_highlight()
            self.de_select_shape()
        self.prev_point = QPointF()
        self.repaint()

    def current_cursor(self):
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            cursor = cursor.shape()
        return cursor

    def override_cursor(self, cursor):
        self._cursor = cursor
        if self.current_cursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)

    def select_shape(self, shape):
        self.de_select_shape()
        shape.selected = True
        self.selected_shape = shape
        # self.set_hiding()
        # self.selectionChanged.emit(True)
        self.update()

    def bounded_move_vertex(self, pos):
        index, shape = self.h_vertex, self.h_shape
        point = shape[index]
        if self.out_of_pixmap(pos):
            size = self.pixmap.size()
            clipped_x = min(max(0, pos.x()), size.width())
            clipped_y = min(max(0, pos.y()), size.height())
            pos = QPointF(clipped_x, clipped_y)

        shift_pos = pos - point

        shape.move_vertex_by(index, shift_pos)

        left_index = (index + 1) % 4
        right_index = (index + 3) % 4
        left_shift = None
        right_shift = None
        if index % 2 == 0:
            right_shift = QPointF(shift_pos.x(), 0)
            left_shift = QPointF(0, shift_pos.y())
        else:
            left_shift = QPointF(shift_pos.x(), 0)
            right_shift = QPointF(0, shift_pos.y())
        shape.move_vertex_by(right_index, right_shift)
        shape.move_vertex_by(left_index, left_shift)

    def bounded_move_shape(self, shape, pos):
        if self.out_of_pixmap(pos):
            return False  # No need to move
        o1 = pos + self.offsets[0]
        if self.out_of_pixmap(o1):
            pos -= QPointF(min(0, o1.x()), min(0, o1.y()))
        o2 = pos + self.offsets[1]
        if self.out_of_pixmap(o2):
            pos += QPointF(min(0, self.pixmap.width() - o2.x()),
                           min(0, self.pixmap.height() - o2.y()))
        # The next line tracks the new position of the cursor
        # relative to the shape, but also results in making it
        # a bit "shaky" when nearing the border and allows it to
        # go outside of the shape's area for some reason. XXX
        # self.calculateOffsets(self.selectedShape, pos)
        dp = pos - self.prev_point
        if dp:
            shape.move_by(dp)
            self.prev_point = pos
            return True
        return False

    def un_highlight(self, shape=None):
        if shape == None or shape == self.h_shape:
            if self.h_shape:
                self.h_shape.highlight_clear()
            self.h_vertex = self.h_shape = None
            
    def de_select_shape(self):
        if self.selected_shape:
            self.selected_shape.selected = False
            self.selected_shape = None
            # self.set_hiding(False)
            # self.selectionChanged.emit(False)
            self.update()

    def delete_selected(self):
        if self.selected_shape:
            shape = self.selected_shape
            self.un_highlight(shape)
            self.shapes.remove(self.selected_shape)
            self.selected_shape = None
            self.update()
            return shape

    def select_shape_point(self, point):
        """Select the first shape created which contains this point."""
        self.de_select_shape()
        if self.selected_vertex():  # A vertex is marked for selection.
            index, shape = self.h_vertex, self.h_shape
            shape.highlight_vertex(index, shape.MOVE_VERTEX)
            self.select_shape(shape)
            return self.h_vertex
        for shape in reversed(self.shapes):
            if shape.frameId == self.curFramesId:
                if shape.contains_point(point):
                    self.select_shape(shape)
                    self.calculate_offsets(shape, point)
                    return self.selected_shape
        return None
    
    def selected_vertex(self):
        return self.h_vertex is not None

    def calculate_offsets(self, shape, point):
        rect = shape.bounding_rect()
        x1 = rect.x() - point.x()
        y1 = rect.y() - point.y()
        x2 = (rect.x() + rect.width()) - point.x()
        y2 = (rect.y() + rect.height()) - point.y()
        self.offsets = QPointF(x1, y1), QPointF(x2, y2)

    def set_last_label(self, text, line_color=None, fill_color=None):
        assert text
        self.shapes[-1].label = text
        if line_color:
            self.shapes[-1].line_color = line_color

        if fill_color:
            self.shapes[-1].fill_color = fill_color

        return self.shapes[-1]
    
    def set_shape_label(self, shape, text, id, line_color=None, fill_color=None):
        shape.label = text
        shape.id = id
        if line_color:
            shape.line_color = line_color

        if fill_color:
            shape.fill_color = fill_color

        return shape

    def paintEvent(self, event):
        if not self.pixmap:
            return super(canvas, self).paintEvent(event)
        p = self._painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offset_to_center())

        p.drawPixmap(QPointF(0, 0), self.pixmap)

        Shape.scale = self.scale
        # Shape.label_font_size = self.label_font_size

        # 画矩形
        for shape in self.shapes:
            # if (shape.selected or not self._hide_background) and self.isVisible(shape):
            #     shape.fill = shape.selected or shape == self.h_shape
            #     shape.paint(p)
            if shape.frameId == self.curFramesId:
                shape.fill = shape.selected or shape == self.h_shape # 是否填充
                shape._highlight_point = shape == self.h_shape
                shape.paint(p)


        # 拖拽时显示矩形
        if self.current is not None and len(self.line) == 2:
            left_top = self.line[0]
            right_bottom = self.line[1]
            rect_width = right_bottom.x() - left_top.x()
            rect_height = right_bottom.y() - left_top.y()
            p.setPen(self.drawing_rect_color)
            brush = QBrush(Qt.Dense7Pattern)
            p.setBrush(brush)
            p.drawRect(int(left_top.x()), int(left_top.y()), int(rect_width), int(rect_height))

        # 十字参考线
        if self.drawing() and not self.prev_point.isNull() and not self.out_of_pixmap(self.prev_point):
            p.setPen(QColor(41, 121, 255))
            p.drawLine(int(self.prev_point.x()), 0, int(self.prev_point.x()), int(self.pixmap.height()))
            p.drawLine(0, int(self.prev_point.y()), int(self.pixmap.width()), int(self.prev_point.y()))

        p.end()
    
    # TODO: 边界
    def mouseMoveEvent(self, ev):
        """Update line with last point and current coordinates."""
        pos = self.transform_pos(ev.pos())

        # Update coordinates in status bar if image is opened
        if self.numFrames:
            self.window.label_coordinates.setText(
                'X: %d; Y: %d' % (pos.x(), pos.y()))
    
        if self.drawing(): # create mode
            self.override_cursor(CURSOR_DRAW)

            if self.current:
                # Display annotation width and height while drawing
                current_width = abs(self.current[0].x() - pos.x())
                current_height = abs(self.current[0].y() - pos.y())
                self.window.label_coordinates.setText(
                        'Width: %d, Height: %d / X: %d; Y: %d' % (current_width, current_height, pos.x(), pos.y()))

                color = self.drawing_line_color
                if self.out_of_pixmap(pos):
                    # Don't allow the user to draw outside the pixmap.
                    # Clip the coordinates to 0 or max,
                    # if they are outside the range [0, max]
                    size = self.pixmap.size()
                    clipped_x = min(max(0, pos.x()), size.width())
                    clipped_y = min(max(0, pos.y()), size.height())
                    pos = QPointF(clipped_x, clipped_y)
                
                self.line[1] = pos
                self.line.line_color = color
                self.prev_point = QPointF()
                self.current.highlight_clear()
            else:
                self.prev_point = pos
            self.repaint()
            return
        
        # Polygon/Vertex moving.
        if Qt.LeftButton & ev.buttons():
            if self.selected_vertex():
                self.bounded_move_vertex(pos)
                # self.shapeMoved.emit()
                self.repaint()

                # Display annotation width and height while moving vertex
                point1 = self.h_shape[1]
                point3 = self.h_shape[3]
                current_width = abs(point1.x() - point3.x())
                current_height = abs(point1.y() - point3.y())
                self.window.label_coordinates.setText(
                        'Width: %d, Height: %d / X: %d; Y: %d' % (current_width, current_height, pos.x(), pos.y()))

            elif self.selected_shape and self.prev_point:
                self.override_cursor(CURSOR_MOVE)
                self.bounded_move_shape(self.selected_shape, pos)
                self.repaint()

                # Display annotation width and height while moving shape
                point1 = self.selected_shape[1]
                point3 = self.selected_shape[3]
                current_width = abs(point1.x() - point3.x())
                current_height = abs(point1.y() - point3.y())
                self.window.label_coordinates.setText(
                        'Width: %d, Height: %d / X: %d; Y: %d' % (current_width, current_height, pos.x(), pos.y()))
            return

        # # pixmap moving
        # if Qt.RightButton & ev.buttons():
        #     pos = self.transform_pos(ev.pos(), right = True)
        #     self.override_cursor(CURSOR_MOVE)
        #     self.deltaPos = pos - self.prevRightPoint
        #     self.pointPos += self.deltaPos
        #     self.prevRightPoint = pos
        #     self.repaint()

        #     return

        # Just hovering over the canvas, 2 possibilities:
        # - Highlight shapes
        # - Highlight vertex
        # Update shape/vertex fill and tooltip value accordingly.
        self.setToolTip("Image")
        for shape in reversed([s for s in self.shapes]):
            # Look for a nearby vertex to highlight. If that fails,
            # check if we happen to be inside a shape.
            if shape.frameId == self.curFramesId:
                index = shape.nearest_vertex(pos, self.epsilon)
                if index is not None:
                    if self.selected_vertex():
                        self.h_shape.highlight_clear()
                    self.h_vertex, self.h_shape = index, shape
                    shape.highlight_vertex(index, shape.MOVE_VERTEX)
                    self.override_cursor(CURSOR_POINT)
                    self.setToolTip("Click & drag to move point")
                    self.setStatusTip(self.toolTip())
                    self.update()
                    break

                elif shape.contains_point(pos):
                    if self.selected_vertex():
                        self.h_shape.highlight_clear()
                    self.h_vertex, self.h_shape = None, shape
                    tooltip = str(shape.label) + str(' ') + str(shape.id) + ' (' + shape.auto + ')'
                    self.setToolTip(tooltip)
                    self.setStatusTip("Click & drag to move rect")
                    self.override_cursor(CURSOR_GRAB)
                    self.update()
                    # Display annotation width and height while hovering inside
                    point1 = self.h_shape[1]
                    point3 = self.h_shape[3]
                    current_width = abs(point1.x() - point3.x())
                    current_height = abs(point1.y() - point3.y())
                    self.window.label_coordinates.setText(
                            'Width: %d, Height: %d / X: %d; Y: %d' % (current_width, current_height, pos.x(), pos.y()))
                    break
        
        else:  # Nothing found, clear highlights, reset state.
            if self.h_shape:
                self.h_shape.highlight_clear()
                self.update()
            self.h_vertex, self.h_shape = None, None
            self.override_cursor(CURSOR_DEFAULT)

    def mousePressEvent(self, ev):
        pos = self.transform_pos(ev.pos())
        if ev.button() == Qt.LeftButton:
            if self.drawing():
                self.handle_drawing(pos)
            else:
                selection = self.select_shape_point(pos)
                self.prev_point = pos
                if selection is None:
                    # pan
                    QApplication.setOverrideCursor(QCursor(Qt.OpenHandCursor))
                    self.pan_initial_pos = pos
        elif ev.button() == Qt.RightButton:
            self.override_cursor(CURSOR_MOVE)
            self.prevRightPoint = pos

        self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            pos = self.transform_pos(ev.pos())
            if self.drawing():
                self.handle_drawing(pos)
                QApplication.restoreOverrideCursor()
            else:
                # pan
                QApplication.restoreOverrideCursor()

    def mouseDoubleClickEvent(self, ev):
        # 修改标签信息
        if self.selected_shape:
            self.label_dialog = LabelDialog(parent=self, list_item=self.window.labelHint)
            for shape in reversed([s for s in self.shapes]):
                if shape.selected and shape.frameId == self.curFramesId:
                    text, id = self.label_dialog.pop_up(id=shape.id, text=shape.label)
                    if text is not None:
                        generate_line_color, generate_fill_color = generate_color_by_text(text)
                        self.set_shape_label(shape, text, id, generate_line_color, generate_fill_color)
                        break
        self.repaint()
