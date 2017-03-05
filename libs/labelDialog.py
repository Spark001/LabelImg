try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from lib import newIcon, labelValidator, newAction, addActions
from functools import partial

BB = QDialogButtonBox


class LabelDialog(QDialog):

    def __init__(self, text="Enter object label", parent=None, listItem=None):
        super(LabelDialog, self).__init__(parent)
        self.edit = QLineEdit()
        self.edit.setText(text)
        self.edit.setValidator(labelValidator())
        self.edit.editingFinished.connect(self.postProcess)
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)
        self.listItem = listItem[:]

        if listItem is not None and len(listItem) > 0:
            self.listWidget = QListWidget(self)
            for item in listItem:
                #qDebug(item)
                self.listWidget.addItem(item)
            self.listWidget.itemDoubleClicked.connect(self.listItemClick)
            layout.addWidget(self.listWidget)

            # add a shortcut to choose the first label
            action = partial(newAction, self)
            choose1 = action('@Choose label', self.choose,
                             ' ', None, u'Choose label')
            addActions(self.listWidget, (choose1,))

        self.setLayout(layout)

    def validate(self):
        try:
            if self.edit.text().trimmed():
                self.accept()
        except AttributeError:
            # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
            if self.edit.text().strip():
                self.accept()

    def postProcess(self):
        try:
            self.edit.setText(self.edit.text().trimmed())
        except AttributeError:
            # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
            self.edit.setText(self.edit.text())

    def popUp(self, text='', move=True):
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))
        self.edit.setFocus(Qt.PopupFocusReason)
        if move:
            self.move(QCursor.pos())
        return self.edit.text() if self.exec_() else None

    def listItemClick(self, tQListWidgetItem):
        try:
            text = tQListWidgetItem.text().trimmed()
        except AttributeError:
            # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
            text = tQListWidgetItem.text().strip()
        self.edit.setText(text)
        self.validate()

    def ch1(self):
        if self.listItem is not None and len(self.listItem) > 0:
            try:
                text = self.listItem[0].trimmed()
            except AttributeError:
                # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
                text = self.listItem[0].strip()
            self.edit.setText(text)
            self.validate()

    def choose(self):
        if self.listItem is not None and len(self.listItem) > 0:
            try:
                text = self.listWidget.currentItem().text().trimmed()
            except AttributeError:
                # PyQt5: AttributeError: 'str' object has no attribute 'trimmed'
                text = self.listWidget.currentItem().text().strip()
            self.edit.setText(text)
            self.validate()
