from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from GUI.model_combox import ModelComboBox
from GUI.utils import new_icon, label_validator, trimmed

BB = QDialogButtonBox

class ModelDialog(QDialog):
    def __init__(self, parent=None, model=[]):
        super(ModelDialog, self).__init__(parent)
        
        # 模型名称
        self.modelName = QLabel("Model: ", self)
        
        
        self.model = model
        self.currentModel = self.model[0]
        self.modelComboBox = ModelComboBox(self, items = self.model)

        hLayoutModelName = QHBoxLayout()
        hLayoutModelName.addWidget(self.modelName)
        hLayoutModelName.addWidget(self.modelComboBox)

        layout = QVBoxLayout()
        layout.addLayout(hLayoutModelName)
        self.button_box = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(new_icon('done'))
        bb.button(BB.Cancel).setIcon(new_icon('undo'))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

        self.setLayout(layout)

        
    def model_combo_selection_changed(self, index):
        self.currentModel = self.model[index]

    def validate(self):
        self.accept()

    def pop_up(self, move=True):
        if move:
            cursor_pos = QCursor.pos()
            parent_bottom_right = self.parentWidget().geometry()
            max_x = parent_bottom_right.x() + parent_bottom_right.width() - self.sizeHint().width()
            max_y = parent_bottom_right.y() + parent_bottom_right.height() - self.sizeHint().height()
            max_global = self.parentWidget().mapToGlobal(QPoint(max_x, max_y))
            if cursor_pos.x() > max_global.x():
                cursor_pos.setX(max_global.x())
            if cursor_pos.y() > max_global.y():
                cursor_pos.setY(max_global.y())
            self.move(cursor_pos)
        return True if self.exec_() else False

    