import sys

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox

class ModelComboBox(QWidget):
    def __init__(self, parent=None, items=[]):
        super(ModelComboBox, self).__init__(parent)

        layout = QHBoxLayout()
        self.cb = QComboBox()
        self.items = items
        self.cb.addItems(self.items)

        self.cb.currentIndexChanged.connect(parent.model_combo_selection_changed)

        layout.addWidget(self.cb)
        self.setLayout(layout)

        self.setMinimumWidth(250)