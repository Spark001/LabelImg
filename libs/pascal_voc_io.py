#!/usr/bin/env python
# -*- coding: utf8 -*-
import _init_path
import sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs
import math

XML_EXT = '.xml'
ENCODING = 'utf-8'

class PascalVocWriter:

    def __init__(self, foldername, filename, imgSize, databaseSrc='Unknown', localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.localImgPath = localImgPath

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True)

    def genXML(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or \
                self.foldername is None or \
                self.imgSize is None:
            return None

        top = Element('annotation')
        folder = SubElement(top, 'folder')
        folder.text = self.foldername

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        localImgPath = SubElement(top, 'path')
        localImgPath.text = self.localImgPath

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.databaseSrc

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.imgSize[1])
        height.text = str(self.imgSize[0])
        if len(self.imgSize) == 3:
            depth.text = str(self.imgSize[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def addBndBox(self, xmin, ymin, xmax, ymax, name, type):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        bndbox['type'] = type
        self.boxlist.append(bndbox)

    def addPoint(self, x, y, name, type):
        point = {'x': int(x), 'y': int(y)}
        # point = {'x': x, 'y': y}
        point['name'] = name
        point['type'] = type
        self.boxlist.append(point)

    def addPolygon(self, x1, y1, x2, y2, x3, y3, x4, y4, name, type):
        polygon = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'x3': x3, 'y3': y3, 'x4': x4, 'y4': y4}
        polygon['name'] = name
        polygon['type'] = type
        self.boxlist.append(polygon)

    def addRBox(self, cx, cy, w, h, angle, name, type):
        rbox = {'cx': cx, 'cy': cy, 'w': w, 'h': h, 'angle': angle}
        rbox['name'] = name
        rbox['type'] = type
        self.boxlist.append(rbox)

    def appendObjects(self, top):
        for each_object in self.boxlist:
            object_item = SubElement(top, 'object')
            name = SubElement(object_item, 'name')
            try:
                name.text = unicode(each_object['name'])
            except NameError:
                # Py3: NameError: name 'unicode' is not defined
                name.text = each_object['name']
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = "0"
            if each_object['type'] == 'Rect':
                bndbox = SubElement(object_item, 'bndbox')
                xmin = SubElement(bndbox, 'xmin')
                xmin.text = str(each_object['xmin'])
                ymin = SubElement(bndbox, 'ymin')
                ymin.text = str(each_object['ymin'])
                xmax = SubElement(bndbox, 'xmax')
                xmax.text = str(each_object['xmax'])
                ymax = SubElement(bndbox, 'ymax')
                ymax.text = str(each_object['ymax'])
            elif each_object['type'] == 'Point':
                point = SubElement(object_item, 'point')
                xmin = SubElement(point, 'x')
                xmin.text = str(each_object['x'])
                ymin = SubElement(point, 'y')
                ymin.text = str(each_object['y'])
            elif each_object['type'] == 'Polygon':
                polygon = SubElement(object_item, 'polygon')
                x1 = SubElement(polygon, 'x1')
                x1.text = str(each_object['x1'])
                y1 = SubElement(polygon, 'y1')
                y1.text = str(each_object['y1'])
                x2 = SubElement(polygon, 'x2')
                x2.text = str(each_object['x2'])
                y2 = SubElement(polygon, 'y2')
                y2.text = str(each_object['y2'])
                x3 = SubElement(polygon, 'x3')
                x3.text = str(each_object['x3'])
                y3 = SubElement(polygon, 'y3')
                y3.text = str(each_object['y3'])
                x4 = SubElement(polygon, 'x4')
                x4.text = str(each_object['x4'])
                y4 = SubElement(polygon, 'y4')
                y4.text = str(each_object['y4'])
            elif each_object['type'] == 'RBox':
                rbox = SubElement(object_item, 'rbox')
                cx = SubElement(rbox, 'cx')
                cx.text = str(each_object['cx'])
                cy = SubElement(rbox, 'cy')
                cy.text = str(each_object['cy'])
                w = SubElement(rbox, 'w')
                w.text = str(each_object['w'])
                h = SubElement(rbox, 'h')
                h.text = str(each_object['h'])
                angle = SubElement(rbox, 'angle')
                angle.text = str(each_object['angle'])

    def save(self, targetFile=None):
        root = self.genXML()
        self.appendObjects(root)
        out_file = None
        if targetFile is None:
            out_file = codecs.open(
                self.filename + XML_EXT, 'w', encoding=ENCODING)
        else:
            out_file = codecs.open(targetFile, 'w', encoding=ENCODING)

        prettifyResult = self.prettify(root)
        out_file.write(prettifyResult.decode(ENCODING))
        out_file.close()


class PascalVocReader:

    def __init__(self, filepath):
        # shapes type:
        # [label, shapetype,  [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color]
        self.shapes = []
        self.filepath = filepath
        self.parseXML()

    def getShapes(self):
        return self.shapes

    def addBndBox(self, label, bndbox):
        xmin = float(bndbox.find('xmin').text)
        ymin = float(bndbox.find('ymin').text)
        xmax = float(bndbox.find('xmax').text)
        ymax = float(bndbox.find('ymax').text)
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        self.shapes.append((label, 'Rect', points, None, None, None))

    def addPoint(self, label, point):  #save as bndbox
        xmin = float(point.find('x').text)
        ymin = float(point.find('y').text)
        # xmin = float(point.find('x').text)
        # ymin = float(point.find('y').text)
        xmax = xmin
        ymax = ymin
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        self.shapes.append((label, 'Point', points, None, None, None))

    def addPolygon(self, label, polygon):
        x1 = float(polygon.find('x1').text)
        y1 = float(polygon.find('y1').text)
        x2 = float(polygon.find('x2').text)
        y2 = float(polygon.find('y2').text)
        x3 = float(polygon.find('x3').text)
        y3 = float(polygon.find('y3').text)
        x4 = float(polygon.find('x4').text)
        y4 = float(polygon.find('y4').text)
        points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        self.shapes.append((label, 'Polygon', points, None, None, None))

    def addRBox(self, label, rbox):
        cx = float(rbox.find('cx').text)
        cy = float(rbox.find('cy').text)
        w = float(rbox.find('w').text)
        h = float(rbox.find('h').text)
        angle = float(rbox.find('angle').text)

        direction = angle / 180 * math.pi

        p1x, p1y = self.rotatePoint(cx, cy, cx - w/2, cy - h/2, direction)
        p2x, p2y = self.rotatePoint(cx, cy, cx + w/2, cy - h/2, direction)
        p3x, p3y = self.rotatePoint(cx, cy, cx + w/2, cy + h/2, direction)
        p4x, p4y = self.rotatePoint(cx, cy, cx - w/2, cy + h/2, direction)

        points = [(p1x, p1y), (p2x, p2y), (p3x, p3y), (p4x, p4y)]

        self.shapes.append((label, 'RBox', points, None, None, angle))

    def rotatePoint(self, xc, yc, xp, yp, theta):
        xoff = xp-xc
        yoff = yp-yc
        cosTheta = math.cos(theta)
        sinTheta = math.sin(theta)
        pResx = cosTheta * xoff + sinTheta * yoff
        pResy = - sinTheta * xoff + cosTheta * yoff
        # pRes = (xc + pResx, yc + pResy)
        return xc+pResx, yc+pResy

    def parseXML(self):
        assert self.filepath.endswith('.xml'), "Unsupport file format"
        parser = etree.XMLParser(encoding=ENCODING)
        xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()
        filename = xmltree.find('filename').text

        for object_iter in xmltree.findall('object'):
            if object_iter.find('bndbox') is not None:
                bndbox = object_iter.find('bndbox')
                label = object_iter.find('name').text
                self.addBndBox(label, bndbox)
            elif object_iter.find('point') is not None:
                point = object_iter.find('point')
                label = object_iter.find('name').text
                self.addPoint(label, point)
            elif object_iter.find('keypoint') is not None:
                point = object_iter.find('keypoint')
                label = object_iter.find('name').text
                self.addPoint(label, point)
            elif object_iter.find('polygon') is not None:
                polygon = object_iter.find('polygon')
                label = object_iter.find('name').text
                self.addPolygon(label, polygon)
            elif object_iter.find('rbox') is not None:
                rbox = object_iter.find('rbox')
                label = object_iter.find('name').text
                self.addRBox(label, rbox)
        return True


# tempParseReader = PascalVocReader('../tests/xml/00049.xml')
# print(tempParseReader)
# print tempParseReader.getShapes()
"""
# Test
tmp = PascalVocWriter('temp','test', (10,20,3))
tmp.addBndBox(10,10,20,30,'chair')
tmp.addBndBox(1,1,600,600,'car')
tmp.save()
"""


# root = ElementTree.parse('../tests/xml/00049.xml')
# size = root.find('size')
# print(size.find('width'))
# size.remove(size.find('width'))
# print(size.find('width'))