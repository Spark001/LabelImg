try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PyQt4.QtGui import QImage

import os.path
class LabelFileError(Exception):
    pass


class LabelFile(object):
	suffix = '.txt'

	def __init__(self, filename=None):
		self.choices = ()
		self.verified = False

	def saveLabel(self, filename, choices):
		with open(filename) as f:
			f.write(str(choices))

	def toggleVerify(self):
		self.verified = not self.verified


	@staticmethod
	def isLabelFile(filename):
		fileSuffix = os.path.splitext(filename)[1].lower()
		return fileSuffix == LabelFile.suffix