try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

import  string
from functools import partial

class SingleChoice(QWidget):

	toggle = pyqtSignal()
	
	def __init__(self, candidateNum,parent=None):
		super(SingleChoice, self).__init__(parent)
		self.candidateNum = candidateNum
		self.choice = None
		self.dirty = False
		self.buttonGroup = []

		layout = QVBoxLayout()

		## change fixed buttonNum to adaptive
		for i in xrange(self.candidateNum):
			btn = QRadioButton(chr(65+i))
			btn.toggled.connect(partial(self.state, btn))
			layout.addWidget(btn)
			self.buttonGroup.append(btn)

		# self.btna = QRadioButton('a')
		# self.btna.toggled.connect(lambda: self.state(self.btna))
		# layout.addWidget(self.btna)
		#
		# self.btnb = QRadioButton('b')
		# self.btnb.toggled.connect(lambda: self.state(self.btnb))
		# layout.addWidget(self.btnb)
		#
		# self.btnc = QRadioButton('c')
		# self.btnc.toggled.connect(lambda: self.state(self.btnc))
		# layout.addWidget(self.btnc)

		self.btnd = QRadioButton(r'None')
		self.btnd.setVisible(False)
		layout.addWidget(self.btnd)

		self.setLayout(layout)
		# self.show()

	def state(self, btn):
		self.toggle.emit()
		self.dirty = True
		if btn.isChecked():
			self.choice = btn.text()
			print 'choose the label: {}'.format(self.choice)

	def resetstate(self):
		# self.clearFocus()
		# if self.btna.isChecked(): self.btna.setChecked(False)
		# if self.btnb.isChecked(): self.btnb.setChecked(False)
		# if self.btnc.isChecked(): self.btnc.setChecked(False)
		self.btnd.setChecked(True)
		self.dirty = False
		self.choice = None

	def setstate(self, i):
		assert isinstance(i, int)
		assert i>=0 and i<self.candidateNum
		btn = self.buttonGroup[i]
		btn.setChecked(True)