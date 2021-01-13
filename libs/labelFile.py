# Copyright (c) 2016 Tzutalin
# Create by TzuTaLin <tzu.ta.lin@gmail.com>

try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PyQt4.QtGui import QImage

from base64 import b64encode, b64decode
from pascal_voc_io import PascalVocWriter
import os.path
import sys
import math


class LabelFileError(Exception):
    pass


class LabelFile(object):
    # It might be changed as window creates. By default, using XML ext
    # suffix = '.lif'
    suffix = '.xml'

    def __init__(self, filename=None):
        self.shapes = ()
        self.imagePath = None
        self.imageData = None
        self.verified = False

    def savePascalVocFormat(self, filename, shapes, imagePath, imageData,
                            lineColor=None, fillColor=None, databaseSrc=None):
        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        image = QImage()
        image.load(imagePath)
        imageShape = [image.height(), image.width(),
                      1 if image.isGrayscale() else 3]
        writer = PascalVocWriter(imgFolderName, imgFileNameWithoutExt,
                                 imageShape, localImgPath=imagePath)
        writer.verified = self.verified

        w, h = image.width(), image.height()
        for shape in shapes:
            print(shape['type'])
            points = shape['points']
            self.constrainPoints(points, w, h)
            label = shape['label']
            if shape['type'] == 'Rect':
                bndbox = LabelFile.convertPoints2BndBox(points)
                writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label, 'Rect')
            elif shape['type'] == 'Point':
                point = points[0]
                writer.addPoint(point[0], point[1], label, 'Point')
            elif shape['type'] == 'Polygon':
                polygon = LabelFile.convertPoints2Polygon(points)
                writer.addPolygon(polygon[0], polygon[1], polygon[2], polygon[3], polygon[4], polygon[5],
                                  polygon[6], polygon[7], label, 'Polygon')
            elif shape['type'] == 'RBox':
                rbox = LabelFile.convertPoints2RBox(shape)
                writer.addRBox(rbox[0], rbox[1], rbox[2], rbox[3], rbox[4], label, 'RBox')

        writer.save(targetFile=filename)
        return

    def constrainPoints(self, points, w, h):
        for i in range(len(points)):
            points[i] = (max(0, min(points[i][0], w-1)), max(0, min(points[i][1], h-1)))

    def toggleVerify(self):
        self.verified = not self.verified

    @staticmethod
    def isLabelFile(filename):
        fileSuffix = os.path.splitext(filename)[1].lower()
        return fileSuffix == LabelFile.suffix

    @staticmethod
    def convertPoints2BndBox(points):
        xmin = float('inf')
        ymin = float('inf')
        xmax = float('-inf')
        ymax = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            xmin = min(x, xmin)
            ymin = min(y, ymin)
            xmax = max(x, xmax)
            ymax = max(y, ymax)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        # if xmin < 1:
        #     xmin = 1
        #
        # if ymin < 1:
        #     ymin = 1

        return (int(xmin), int(ymin), int(xmax), int(ymax))

    @staticmethod
    def convertPoints2Polygon(points):
        x1 = points[0][0]
        y1 = points[0][1]
        x2 = points[1][0]
        y2 = points[1][1]
        x3 = points[2][0]
        y3 = points[2][1]
        x4 = points[3][0]
        y4 = points[3][1]
        return (int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), int(x4), int(y4))

    @staticmethod
    def convertPoints2RBox(shape):
        points = shape['points']
        center = shape['center']
        angle = shape['angle']

        cx = center.x()
        cy = center.y()

        w = math.sqrt((points[0][0]-points[1][0]) ** 2 +
            (points[0][1]-points[1][1]) ** 2)

        h = math.sqrt((points[2][0]-points[1][0]) ** 2 +
            (points[2][1]-points[1][1]) ** 2)

        angle = angle % 360

        return (round(cx,4), round(cy,4), round(w,4), round(h,4), round(angle,6))




