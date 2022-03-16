#!/usr/bin/python
# -*- coding: utf-8 -*-


try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from lib import distance
import math

# QColor for (r, g, b, alpha)
DEFAULT_LINE_COLOR = QColor(0, 255, 0, 128)
DEFAULT_FILL_COLOR = QColor(255, 0, 0, 128)
DEFAULT_SELECT_LINE_COLOR = QColor(255, 255, 255)
DEFAULT_SELECT_FILL_COLOR = QColor(0, 128, 255, 155)
DEFAULT_VERTEX_FILL_COLOR = QColor(0, 255, 0, 255)
DEFAULT_HVERTEX_FILL_COLOR = QColor(255, 0, 0)
FISRT_VERTEX_FILL_COLOR = QColor(255, 0, 255, 255)
SECOND_VERTEX_FILL_COLOR = QColor(0, 0, 255, 255)

class Shape(object):
    P_SQUARE, P_ROUND = range(2)

    MOVE_VERTEX, NEAR_VERTEX = range(2)

    # The following class variables influence the drawing
    # of _all_ shape objects.
    line_color = DEFAULT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    select_line_color = DEFAULT_SELECT_LINE_COLOR
    select_fill_color = DEFAULT_SELECT_FILL_COLOR
    vertex_fill_color = DEFAULT_VERTEX_FILL_COLOR
    vertex_fill_check_color = DEFAULT_FILL_COLOR
    hvertex_fill_color = DEFAULT_HVERTEX_FILL_COLOR
    first_vertex_fill_color = FISRT_VERTEX_FILL_COLOR
    second_vertex_fill_color = SECOND_VERTEX_FILL_COLOR
    point_type = P_ROUND
    point_size = 8
    scale = 1.0

    def __init__(self, label=None, shapetype='Rect', line_color=None, angle=None, center=None, isRotated=False):
        self.label = label
        self.points = []
        self.fill = False
        self.selected = False

        self.angle = 0
        self.center = None
        self.isRotated = isRotated

        self._highlightIndex = None
        self._highlightMode = self.NEAR_VERTEX
        self._highlightSettings = {
            self.NEAR_VERTEX: (4, self.P_ROUND),
            self.MOVE_VERTEX: (1.5, self.P_SQUARE),
        }

        self._closed = False

        self._shapetype = shapetype

        if line_color is not None:
            # Override the class line_color attribute
            # with an object attribute. Currently this
            # is used for drawing the pending line a different color.
            self.line_color = line_color

    def rotate(self, angle):
        for i, p in enumerate(self.points):
            self.points[i] = self.rotatePoint(p, angle)
        self.angle += angle
        self.angle = self.angle % 360

    def rotatePoint(self, p, angle):
        theta = angle / 180 * math.pi
        order = p-self.center
        cosTheta = math.cos(theta)
        sinTheta = math.sin(theta)
        pResx = cosTheta * order.x() + sinTheta * order.y()
        pResy = - sinTheta * order.x() + cosTheta * order.y()
        pRes = QPointF(self.center.x() + pResx, self.center.y() + pResy)
        return pRes

    def close(self):
        if self._shapetype != 'Point' and len(self.points) == 4:
            self.center = QPointF((self.points[0].x()+self.points[2].x()) / 2, (self.points[0].y()+self.points[2].y()) / 2)
        # judge the direction changed
        self._closed = True

    def reachMaxPoints(self):
        if len(self.points) >= 4:
            return True
        return False

    def addPoint(self, point):
        if self.points and point == self.points[0]:
            self.close()
        else:
            self.points.append(point)

    def popPoint(self):
        if self.points:
            return self.points.pop()
        return None

    def isClosed(self):
        return self._closed

    def setOpen(self):
        self._closed = False

    def paint(self, painter):
        if self.points:
            color = self.select_line_color if self.selected else self.line_color
            pen = QPen(color)
            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            vrtx_path = QPainterPath()

            line_path.moveTo(self.points[0])
            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            #self.drawVertex(vrtx_path, 0)

            for i, p in enumerate(self.points):
                line_path.lineTo(p)
                self.drawVertex(vrtx_path, i)
            if self.isClosed():
                line_path.lineTo(self.points[0])

            painter.drawPath(line_path)
            painter.drawPath(vrtx_path)
            painter.fillPath(vrtx_path, self.vertex_fill_color)

            # add for color first and second point in polygon
            if self._shapetype in ['Polygon', 'RBox']:
                self.reFillVertex(painter)

            if self.fill:
                color = self.select_fill_color if self.selected else self.fill_color
                painter.fillPath(line_path, color)

            #self.drawRotation(painter)

    def paintCenter(self, painter):
        if self.center is not None:
            center_path = QPainterPath()
            d = self.point_size / self.scale
            center_path.addRect(self.center.x() - d / 2, self.center.y() - d / 2, d, d)
            painter.drawPath(center_path)
            if self.isRotated:
                painter.fillPath(center_path, self.vertex_fill_color)
            else:
                painter.fillPath(center_path, QColor(0, 0, 0))

    def paintDirection(self, painter):
        if self.center is not None:
            direct_path = QPainterPath()
            src = QPointF(self.center.x(), self.center.y())
            xlast = (self.points[1].x() + self.points[2].x()) / 2.
            ylast = (self.points[1].y() + self.points[2].y()) / 2.
            dst = QPointF(xlast, ylast)
            direct_path.moveTo(src)
            direct_path.lineTo(dst)
            pen = QPen()
            pen.setColor(QColor(255, 0, 0, 128))
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawPath(direct_path)

    def reFillVertex(self, painter):
        if self._shapetype == 'Polygon':
            vrtx_path = QPainterPath()
            self.drawVertex(vrtx_path, 0)
            painter.fillPath(vrtx_path, self.first_vertex_fill_color)
            vrtx_path = QPainterPath()
            self.drawVertex(vrtx_path, 1)
            painter.fillPath(vrtx_path, self.second_vertex_fill_color)
        elif self._shapetype == 'RBox':
            vrtx_path = QPainterPath()
            self.drawVertex(vrtx_path, 1)
            painter.fillPath(vrtx_path, self.first_vertex_fill_color)
            vrtx_path = QPainterPath()
            self.drawVertex(vrtx_path, 2)
            painter.fillPath(vrtx_path, self.second_vertex_fill_color)

    def drawVertex(self, path, i):
        d = self.point_size / self.scale
        shape = self.point_type
        point = self.points[i]
        if i == self._highlightIndex:
            size, shape = self._highlightSettings[self._highlightMode]
            d *= size
        if self._highlightIndex is not None:
            self.vertex_fill_color = self.hvertex_fill_color
        else:
            self.vertex_fill_color = self.line_color
        if shape == self.P_SQUARE:
            path.addRect(point.x() - d / 2, point.y() - d / 2, d, d)
        elif shape == self.P_ROUND:
            path.addEllipse(point, d / 2.0, d / 2.0)
        else:
            assert False, "unsupported vertex shape"

    def drawRotation(self, painter):
        if self.selected and self._shapetype != 'Point':
            line_path = QPainterPath()
            p1 = (self.points[0]+self.points[1])/2
            line_path.moveTo(p1)
            p2 = QPoint(p1.x(), p1.y()-15/self.scale)
            line_path.lineTo(p2)
            painter.drawPath(line_path)
            image = QPixmap('icons/rotation.png')
            im_w = image.width()
            im_h = image.height()
            # rotation button
            topLeft = QPoint(p2.x()-im_w/2/self.scale, p2.y()-im_h/self.scale)
            bottomRight = QPoint(p2.x()+im_w/2/self.scale, p2.y())
            rect = QRect(topLeft, bottomRight)

            painter.drawPixmap(rect, image)
            # change the mouse

    def nearestVertex(self, point, epsilon):
        for i, p in enumerate(self.points):
            if distance(p - point) <= epsilon:
                return i
        return None

    def containsPoint(self, point):
        return self.makePath().contains(point)

    def makePath(self):
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        return path

    def boundingRect(self):
        return self.makePath().boundingRect()

    def moveBy(self, offset):
        self.points = [p + offset for p in self.points]

    def moveVertexBy(self, i, offset):
        self.points[i] = self.points[i] + offset

    def highlightVertex(self, i, action):
        self._highlightIndex = i
        self._highlightMode = action

    def highlightClear(self):
        self._highlightIndex = None

    def copy(self):
        shape = Shape("%s" % self.label)
        shape.points = [p for p in self.points]
        shape.fill = self.fill
        shape.selected = self.selected
        shape._closed = self._closed
        shape._shapetype = self._shapetype
        # add for rotated shape
        shape.isRotated = self.isRotated
        shape.angle = self.angle
        shape.center = self.center
        if self.line_color != Shape.line_color:
            shape.line_color = self.line_color
        if self.fill_color != Shape.fill_color:
            shape.fill_color = self.fill_color
        return shape

    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __setitem__(self, key, value):
        self.points[key] = value
