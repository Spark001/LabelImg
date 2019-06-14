#!/usr/bin/env python
# -*- coding: utf8 -*-

import codecs
import os.path
import re
import sys
import subprocess

from functools import partial
from collections import defaultdict

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    # needed for py3+qt4
    # ref: http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
    # ref:
    # http://stackoverflow.com/questions/21217399/pyqt4-qtcore-qvariant-object-instead-of-a-string
    if sys.version_info.major >= 3:
        import sip

        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

import resources
from lib  import struct, newAction, newIcon, addActions, fmtShortcut
from canvas import Canvas
from toolBar import ToolBar
from zoomWidget import ZoomWidget
from labelFileBest import LabelFile, LabelFileError
from singleChoiceWidget import SingleChoice

__appname__ = 'Choose the Best'

def u(x):
    '''py2/py3 unicode helper'''
    if sys.version_info < (3, 0, 0):
        if type(x) == str:
            return x.decode('utf-8')
        # if type(x) == QString:
        #     return unicode(x)
        return x
    else:
        return x  # py3

class Window(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar

class MainWindow(QMainWindow, Window):
	FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

	chooseWhichOne = pyqtSignal()

	def __init__(self):
		super(MainWindow, self).__init__()
		self.setWindowTitle(__appname__)
		self.defaultSaveDir = None
		self.autoSaving = True
		self.dirty = False
		self.size = QSize(1200,900)
		self.resize(self.size)

		candidateNum = 3

		# For loading all image under a directory
		self.mImgList = []
		self.dirname = None
		self.labelHist = []
		self.lastOpenDir = None

	## Layout
		self.fileListWidget = QListWidget()
		self.fileListWidget.itemDoubleClicked.connect(self.fileitemDoubleClicked)
		filelistLayout = QHBoxLayout()
		filelistLayout.setContentsMargins(0, 0, 0, 0)
		filelistLayout.addWidget(self.fileListWidget)

		# self.fileDoneWidget = QListWidget()
		# filelistLayout.addWidget(self.fileDoneWidget)

		fileListContainer = QWidget()
		fileListContainer.setLayout(filelistLayout)
		self.filedock = QDockWidget(u'File List', self)
		self.filedock.setObjectName(u'Files')
		self.filedock.setWidget(fileListContainer)
		self.addDockWidget(Qt.BottomDockWidgetArea, self.filedock)

		''' add label widget to choose label'''
		self.labelWidget = SingleChoice(candidateNum)
		self.labeldock = QDockWidget(u'Label', self)
		self.labeldock.setWidget(self.labelWidget)
		self.addDockWidget(Qt.RightDockWidgetArea, self.labeldock)
		self.labelWidget.toggle.connect(self.setDirty)


		self.zoomWidget = ZoomWidget()
		''' add canvas to show image '''
		self.canvas = Canvas(parent=self)
		self.canvas.zoomRequest.connect(self.zoomRequest)
		''' add scroll bar'''
		scroll = QScrollArea()
		scroll.setWidget(self.canvas)
		scroll.setWidgetResizable(True)
		self.scrollBars = {
			Qt.Vertical: scroll.verticalScrollBar(),
			Qt.Horizontal: scroll.horizontalScrollBar()
		}
		self.canvas.scrollRequest.connect(self.scrollRequest)
		self.setCentralWidget(scroll)
	## Actions
		action = partial(newAction, self)
		quit = action('&Quit', self.close,
					  'Ctrl+Q', 'quit', u'Quit application')

		# open = action('&Open', self.openFile,
		# 			  'Ctrl+O', 'open', u'Open image or label file')

		opendir = action('&Open Dir', self.openDir,
						 'Ctrl+u', 'open', u'Open Dir')

		changeSavedir = action('&Change Save Dir', self.changeSavedir,
							   'Ctrl+r', 'open', u'Change default saved Annotation dir')

		# openAnnotation = action('&Open Annotation', self.openAnnotation,
		# 						'Ctrl+q', 'openAnnotation', u'Open Annotation')

		openNextImg = action('&Next Image', self.openNextImg,
							 'd', 'next', u'Open Next')

		openPrevImg = action('&Prev Image', self.openPrevImg,
							 'a', 'prev', u'Open Prev')

		save = action('&Save', self.saveFile,
					  's', 'save', u'Save labels to file', enabled=False)

		# choose = action('&Choo')
		# close = action('&Close', self.closeFile,
		# 			   'Ctrl+W', 'close', u'Close current file')

		zoom = QWidgetAction(self)
		zoom.setDefaultWidget(self.zoomWidget)
		self.zoomWidget.setWhatsThis(
				u"Zoom in or out of the image. Also accessible with"
				" %s and %s from the canvas." % (fmtShortcut("Ctrl+[-+]"),
												 fmtShortcut("Ctrl+Wheel")))
		self.zoomWidget.setEnabled(False)

		zoomIn = action('Zoom &In', partial(self.addZoom, 10),
						'Ctrl++', 'zoom-in', u'Increase zoom level', enabled=False)
		zoomOut = action('&Zoom Out', partial(self.addZoom, -10),
						 'Ctrl+-', 'zoom-out', u'Decrease zoom level', enabled=False)
		zoomOrg = action('&Original size', partial(self.setZoom, 100),
						 'Ctrl+=', 'zoom', u'Zoom to original size', enabled=False)
		fitWindow = action('&Fit Window', self.setFitWindow,
						   'Ctrl+F', 'fit-window', u'Zoom follows window size',
						   checkable=True, enabled=False)
		fitWidth = action('Fit &Width', self.setFitWidth,
						  'Ctrl+Shift+F', 'fit-width', u'Zoom follows window width',
						  checkable=True, enabled=False)
		# Group zoom controls into a list for easier toggling.
		zoomActions = (self.zoomWidget, zoomIn, zoomOut,
					   zoomOrg, fitWindow, fitWidth)
		self.zoomMode = self.MANUAL_ZOOM
		self.scalers = {
			self.FIT_WINDOW: self.scaleFitWindow,
			self.FIT_WIDTH: self.scaleFitWidth,
			# Set to one to scale to 100% when loading files.
			self.MANUAL_ZOOM: lambda: 1,
		}

	## Store actions for further handling.

		self.actions = \
			struct(save=save, open=open,
				  zoom=zoom, zoomIn=zoomIn, zoomOut=zoomOut, zoomOrg=zoomOrg,
				  fitWindow=fitWindow, fitWidth=fitWidth,
				  zoomActions=zoomActions,
				  fileMenuActions=(
					  open, opendir, save, quit),
				  beginner=())

		self.tools = self.toolbar('Tools')
		self.actions.beginner = (
			opendir, changeSavedir,
			openNextImg, openPrevImg, save,
			None,
			zoomIn, zoom, zoomOut, fitWindow, fitWidth
		)

		self.statusBar().showMessage('%s started.' % __appname__)
		self.statusBar().show()

		# Application state.
		self.image = QImage()
		self.filePath = None
		self.recentFiles = []
		self.maxRecent = 7

		self.queueEvent(partial(self.loadFile, self.filePath))

		# Callbacks:
		self.zoomWidget.valueChanged.connect(self.paintCanvas)

		self.populateModeActions()

	def populateModeActions(self):
		tool = self.actions.beginner
		self.tools.clear()
		addActions(self.tools, tool)
		# self.canvas.menus[0].clear()
		# addActions(self.canvas.menus[0], menu)
		# self.menus.edit.clear()
		# actions = (self.actions.create,) if self.beginner() \
		# 	else (self.actions.createMode, self.actions.editMode)

	def toggleActions(self, value=True):
		"""Enable/Disable widgets which depend on an opened image."""
		for z in self.actions.zoomActions:
			z.setEnabled(value)

	def scanAllImages(self, folderPath):
		extensions = ['.jpeg', '.jpg', '.png', '.bmp']
		images = []

		for root, dirs, files in os.walk(folderPath):
			for file in files:
				if file.lower().endswith(tuple(extensions)):
					relatviePath = os.path.join(root, file)
					path = u(os.path.abspath(relatviePath))
					images.append(path)
		images.sort(key=lambda x: x.lower())
		return images

	def paintCanvas(self):
		assert not self.image.isNull(), "cannot paint null image"
		self.canvas.scale = 0.01 * self.zoomWidget.value()
		self.canvas.adjustSize()
		self.canvas.update()

	def queueEvent(self, function):
		QTimer.singleShot(0, function)

	def openFile(self, _value=False):
		if not self.mayContinue():
			return
		path = os.path.dirname(str(self.filePath)) \
			if self.filePath else '.'
		formats = ['*.%s' % str(fmt).lower()
				   for fmt in QImageReader.supportedImageFormats()]
		filters = "Image & Label files (%s)" % \
				  ' '.join(formats + ['*%s' % LabelFile.suffix])
		filename = QFileDialog.getOpenFileName(self,
											   '%s - Choose Image or Label file' % __appname__, path, filters)
		if filename:
			self.loadFile(filename)

	def setDirty(self):
		self.dirty = True
		self.actions.save.setEnabled(True)

	def setClean(self):
		self.dirty = False
		self.actions.save.setEnabled(False)

	def mayContinue(self):
		return not (self.dirty and not self.discardChangesDialog())

	def discardChangesDialog(self):
		yes, no = QMessageBox.Yes, QMessageBox.No
		msg = u'You have unsaved changes, proceed anyway?'
		return yes == QMessageBox.warning(self, u'Attention', msg, yes | no)

	def openDir(self, _value=False):
		if not self.mayContinue():
			return

		path = os.path.dirname(self.filePath) \
			if self.filePath else '.'

		# if self.lastOpenDir is not None and len(self.lastOpenDir) > 1:
		#     path = self.lastOpenDir
		dirpath = u(QFileDialog.getExistingDirectory(self,
													 '%s - Open Directory' % __appname__, path, QFileDialog.ShowDirsOnly
													 | QFileDialog.DontResolveSymlinks))
		dirpath = str(dirpath)
		self.defaultSaveDir = dirpath

		if dirpath is not None and len(dirpath) > 1:
			self.lastOpenDir = dirpath

		self.dirname = dirpath
		self.filePath = None
		self.fileListWidget.clear()
		self.mImgList = self.scanAllImages(dirpath)
		self.openNextImg()
		for imgPath in self.mImgList:
			item = QListWidgetItem(imgPath)
			# item.setBackgroundColor(QColor('green'))
			self.fileListWidget.addItem(item)
		self.checkDone()

	def checkDone(self):
		if self.defaultSaveDir is not None:
			for imgfile in self.mImgList:
				self.toggleDone(imgfile)

	def toggleDone(self, filePath):
		imgFileName = os.path.basename(filePath)
		savedFileName = os.path.splitext(imgFileName)[0] + LabelFile.suffix
		savedPath = os.path.join(str(self.defaultSaveDir), savedFileName)
		if os.path.exists(savedPath):
			index = self.mImgList.index(filePath)
			fileWidgetItem = self.fileListWidget.item(index)
			fileWidgetItem.setBackgroundColor(QColor(Qt.green))

	def changeDoneState(self):
		pass

	def changeSavedir(self, _value=False):
		if self.defaultSaveDir is not None:
			path = str(self.defaultSaveDir)
		else:
			path = '.'

		dirpath = str(QFileDialog.getExistingDirectory(self,
													   '%s - Save to the directory' % __appname__, path,
													   QFileDialog.ShowDirsOnly
													   | QFileDialog.DontResolveSymlinks))

		if dirpath is not None and len(dirpath) > 1:
			self.defaultSaveDir = dirpath

		self.statusBar().showMessage('%s . Annotation will be saved to %s' %
									 ('Change saved folder', self.defaultSaveDir))
		self.statusBar().show()

		if self.filePath is not None:
			self.loadFile(self.filePath)

	def openPrevImg(self, _value=False):
		if not self.mayContinue():
			return

		if len(self.mImgList) <= 0:
			return

		if self.filePath is None:
			return

		currIndex = self.mImgList.index(self.filePath)
		if currIndex - 1 >= 0:
			filename = self.mImgList[currIndex - 1]
			if filename:
				self.loadFile(filename)

	def openNextImg(self, _value=False):
		# Proceding next image without dialog if having any label
		if self.autoSaving is True and self.defaultSaveDir is not None:
			if self.dirty is True:
				self.saveFile()

		if not self.mayContinue():
			return

		if len(self.mImgList) <= 0:
			return

		filename = None
		if self.filePath is None:
			filename = self.mImgList[0]
		else:
			currIndex = self.mImgList.index(self.filePath)
			if currIndex + 1 < len(self.mImgList):
				filename = self.mImgList[currIndex + 1]

		if filename:
			self.loadFile(filename)

	def _saveFile(self, annotationFilePath):
		if annotationFilePath and self.saveLabels(annotationFilePath):
			self.setClean()
			self.statusBar().showMessage('Saved to  %s' % annotationFilePath)
			self.statusBar().show()

	def saveLabels(self, annotationFilePath):
		annotationFilePath = u(annotationFilePath)
		if self.labelFile is None:
			self.labelFile = LabelFile()
			self.labelFile.verified = self.canvas.verified

		labels = self.labelWidget.choice
		# Can add differrent annotation formats here
		try:
			with open(annotationFilePath, 'w') as f:
				f.write(labels)
			# print 'save labels in {} done!'.format(annotationFilePath)
			self.toggleDone(self.filePath)
			return True
		except LabelFileError as e:
			self.errorMessage(u'Error saving label data',
							  u'<b>%s</b>' % e)
			return False

	def resetState(self):
		self.filePath = None
		self.imageData = None
		self.labelFile = None
		self.labelWidget.resetstate()
		return

	def loadFile(self, filePath=None):
		"""Load the specified file, or the last opened file if None."""
		self.resetState()
		self.canvas.setEnabled(False)
		if filePath is None:
			filePath = ''

		unicodeFilePath = u(filePath)
		# print unicodeFilePath
		# Tzutalin 20160906 : Add file list and dock to move faster
		# Highlight the file item
		if unicodeFilePath and self.fileListWidget.count() > 0:
			index = self.mImgList.index(unicodeFilePath)
			fileWidgetItem = self.fileListWidget.item(index)
			fileWidgetItem.setSelected(True)

		if unicodeFilePath and os.path.exists(unicodeFilePath):
			# Load image:
			# read data first and store for saving into label file.
			self.imageData = read(unicodeFilePath, None)
			self.labelFile = None
			image = QImage.fromData(self.imageData)
			if image.isNull():
				self.errorMessage(u'Error opening file',
								  u"<p>Make sure <i>%s</i> is a valid image file." % unicodeFilePath)
				self.status("Error reading %s" % unicodeFilePath)
				return False
			self.status("Loaded %s" % os.path.basename(unicodeFilePath))
			self.image = image
			self.filePath = unicodeFilePath
			self.canvas.loadPixmap(QPixmap.fromImage(image))

			if self.defaultSaveDir is not None:
				imgFilename = os.path.basename(filePath)
				labelFilename = os.path.splitext(imgFilename)[0] + \
								LabelFile.suffix
				labelPath = os.path.join(self.defaultSaveDir, labelFilename)

				if labelPath and os.path.exists(labelPath):
					self.loadLabels(labelPath)

			self.setClean()
			self.canvas.setEnabled(True)
			self.adjustScale(initial=True)
			self.addRecentFile(self.filePath)
			self.canvas.setFocus()
			self.paintCanvas()
			self.toggleActions(True)
			return True
		return False

	def loadLabels(self, labelPath):
		## label is defined in one english character
		with open(labelPath, 'r') as f:
			labels = f.readline()
		labels = [l for l in labels.strip().split()]
		assert len(labels) == 1
		index = ord(labels[0])-65
		self.labelWidget.setstate(index)
		self.setClean()

	def status(self, message, delay=5000):
		self.statusBar().showMessage(message, delay)

	def saveFile(self, _value=False):
		if self.defaultSaveDir is not None and len(str(self.defaultSaveDir)):
			# print('handle the image:' + self.filePath)
			imgFileName = os.path.basename(self.filePath)
			savedFileName = os.path.splitext(
					imgFileName)[0] + LabelFile.suffix
			savedPath = os.path.join(
					str(self.defaultSaveDir), savedFileName)
			# print 'savepath is {}'.format(savedPath)
			self._saveFile(savedPath)
		else:
			self._saveFile(self.filePath if self.labelFile
						   else self.saveFileDialog())
		self.setClean()

	def addRecentFile(self, filePath):
		if filePath in self.recentFiles:
			self.recentFiles.remove(filePath)
		elif len(self.recentFiles) >= self.maxRecent:
			self.recentFiles.pop()
		self.recentFiles.insert(0, filePath)

	def currentPath(self):
		return os.path.dirname(self.filePath) if self.filePath else '.'

	def scrollRequest(self, delta, orientation):
		units = - delta / (8 * 15)
		bar = self.scrollBars[orientation]
		bar.setValue(bar.value() + bar.singleStep() * units)

	def setZoom(self, value):
		self.actions.fitWidth.setChecked(False)
		self.actions.fitWindow.setChecked(False)
		self.zoomMode = self.MANUAL_ZOOM
		self.zoomWidget.setValue(value)

	def addZoom(self, increment=10):
		self.setZoom(self.zoomWidget.value() + increment)

	def zoomRequest(self, delta):
		units = delta / (8 * 15)
		scale = 10
		self.addZoom(scale * units)

	def setFitWindow(self, value=True):
		if value:
			self.actions.fitWidth.setChecked(False)
		self.zoomMode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
		self.adjustScale()

	def setFitWidth(self, value=True):
		if value:
			self.actions.fitWindow.setChecked(False)
		self.zoomMode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
		self.adjustScale()

	def scaleFitWindow(self):
		"""Figure out the size of the pixmap in order to fit the main widget."""
		e = 2.0  # So that no scrollbars are generated.
		w1 = self.centralWidget().width() - e
		h1 = self.centralWidget().height() - e
		a1 = w1 / h1
		# Calculate a new scale value based on the pixmap's aspect ratio.
		w2 = self.canvas.pixmap.width() - 0.0
		h2 = self.canvas.pixmap.height() - 0.0
		a2 = w2 / h2
		return w1 / w2 if a2 >= a1 else h1 / h2

	def scaleFitWidth(self):
		# The epsilon does not seem to work too well here.
		w = self.centralWidget().width() - 2.0
		return w / self.canvas.pixmap.width()

	def adjustScale(self, initial=False):
		value = self.scalers[self.FIT_WINDOW if initial else self.zoomMode]()
		self.zoomWidget.setValue(int(100 * value))

	def fileitemDoubleClicked(self, item=None):
		if not self.mayContinue():
			return
		currIndex = self.mImgList.index(u(item.text()))
		if currIndex < len(self.mImgList):
			filename = self.mImgList[currIndex]
			if filename:
				self.loadFile(filename)

def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default

def get_main_app(argv=[]):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    app = QApplication(argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(newIcon("app"))
    win = MainWindow()
    win.show()
    return app, win

def main(argv):
    '''construct main app and run it'''
    app, _win = get_main_app(argv)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main(sys.argv))