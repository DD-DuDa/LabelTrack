import PyQt5
from PyQt5 import QtGui, QtCore

class TodoList(PyQt5.QWidget):
    def __init__(self):
        PyQt5.QWidget.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.initUI()
        self.show()

    def initUI(self):
        self.todoList = self.makeTodoList()
        self.undoStack = QtGui.QUndoStack(self)
        undoView = QtGui.QUndoView(self.undoStack)
        buttonLayout = self.buttonSetup()
        mainLayout = QtGui.QHBoxLayout(self)
        mainLayout.addWidget(undoView)
        mainLayout.addWidget(self.todoList)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.makeConnections()

    def buttonSetup(self):
        #Make buttons 
        self.deleteButton = QtGui.QPushButton("Delete")
        self.undoButton = QtGui.QPushButton("Undo")
        self.redoButton = QtGui.QPushButton("Redo")
        self.quitButton = QtGui.QPushButton("Quit")
        #Lay them out
        buttonLayout = QtGui.QVBoxLayout()
        buttonLayout.addWidget(self.deleteButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.undoButton)
        buttonLayout.addWidget(self.redoButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.quitButton)
        return buttonLayout

    def makeConnections(self):
        self.deleteButton.clicked.connect(self.deleteItem)
        self.quitButton.clicked.connect(self.close)
        self.undoButton.clicked.connect(self.undoStack.undo)
        self.redoButton.clicked.connect(self.undoStack.redo)

    def deleteItem(self):
        rowSelected=self.todoList.currentRow()
        rowItem = self.todoList.item(rowSelected)
        if rowItem is None:
            return
        command = CommandDelete(self.todoList, rowItem, rowSelected,
                                "Delete item '{0}'".format(rowItem.text()))
        self.undoStack.push(command)

    def makeTodoList(self):
        todoList = QtGui.QListWidget()
        allTasks = ('Fix door', 'Make dinner', 'Read', 
                    'Program in PySide', 'Be nice to everyone')
        for task in allTasks:
            todoItem=QtGui.QListWidgetItem(task)
            todoList.addItem(todoItem)
            todoItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        return todoList


class CommandDelete(QtGui.QUndoCommand):
    def __init__(self, listWidget, item, row, description):
        super(CommandDelete, self).__init__(description)
        self.listWidget = listWidget
        self.string = item.text()
        self.row = row

    def redo(self):
        self.listWidget.takeItem(self.row)

    def undo(self):
        addItem = QtGui.QListWidgetItem(self.string)
        addItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.listWidget.insertItem(self.row, addItem)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    myList=TodoList()
    sys.exit(app.exec_())