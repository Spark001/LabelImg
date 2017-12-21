#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 14:54
# @Author  : Scott Shen
# @Site    : 
# @File    : splitLabelDialog.py
# @Software: PyCharm Community Edition
try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from lib import newIcon
from functools import partial

engTochi = {
    "person_type":"人物类型",
    "person_num":"人物数量",
    "person_location":"人物位置",
    "person_action":"人物动作",
    "person_point":"人物指向"
}

BB = QDialogButtonBox


class SplitLabelDialog(QDialog):

    def __init__(self, parent=None, predefined=None):
        # print 'split'
        super(SplitLabelDialog, self).__init__(parent)
        self.tips = ([''] * len(predefined)) if predefined!=None else None
        self.length = len(predefined)
        self.lbl = QLabel()
        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        self.buttonBox.setEnabled(False)
        self.printf()
        self.layout = QFormLayout()
        index = 0
        for key,item in predefined.items():
            gb = QGroupBox(engTochi[key])
            lot = QHBoxLayout()
            if not isinstance(item, list):
                item = [item]
            for idx,i in enumerate(item):
                checkbox = QRadioButton(i)
                lot.addWidget(checkbox)
                # connect every radiobutton with the label's string
                # and buttonbox's status
                checkbox.toggled.connect(partial(self.getString,i, index))
            gb.setLayout(lot)
            self.layout.addWidget(gb)
            index += 1
        self.layout.addWidget(self.lbl)
        self.layout.addWidget(bb)
        self.setLayout(self.layout)

    # TODO @Scott Shen
    # pre load the choosed information from self.tips
    def pre_load(self):
        pass

    # use last text as predefine
    def popUp(self, text):
        # textsplit = text.split('-')
        # if len(textsplit) == len(self.tips):
        #     self.tips = textsplit
        # self.pre_load()
        return self.lbl.text() if self.exec_() else None
        pass
    
    def validate(self):
        self.accept()

    def getString(self, key, ind):
        self.tips[ind] = key
        self.printf()
        pass

    def printf(self):
        isReady = True
        string = ''
        for _ in range(self.length):
            if self.tips[_] == '':
                self.tips[_] = '?'
                isReady = False
            string += str(self.tips[_])+'-'
        string = string[:-1]
        self.buttonBox.setEnabled(isReady)
        self.lbl.setText(string)