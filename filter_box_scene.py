from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem,
                             QGraphicsProxyWidget, QGridLayout, QLabel, QLineEdit, QVBoxLayout, QPushButton)
from PyQt5.QtGui import QPainterPath
from PyQt5.QtCore import QRectF
from PyQt5 import QtCore, QtWidgets


class Edge(QtWidgets.QGraphicsLineItem):
    def __init__(self, start, p2):
        super().__init__()
        self.start = start
        self.end = None
        self._line = QtCore.QLineF(start.scenePos(), p2)
        self.setLine(self._line)

    def controlPoints(self):
        return [self.start, self.end]

    def controlParents(self):
        return [self.start.parent, self.end.parent]

    def equal(self, edge):
        return edge.controlPoints() == self.controlPoints() or edge.controlPoints() == self.controlPoints()[::-1]

    def setP2(self, p2):
        self._line.setP2(p2)
        self.setLine(self._line)

    def setStart(self, start):
        self.start = start
        self.updateEdge(start)

    def setEnd(self, end):
        self.end = end
        self.updateEdge(end)

    def updateEdge(self, source):
        if source == self.start:
            self._line.setP1(source.scenePos())
        else:
            self._line.setP2(source.scenePos())
        self.setLine(self._line)


class MountPointItem(QGraphicsEllipseItem):

    def __init__(self, x, y, r, parent, input_flag):
        super().__init__(-r//2, -r//2, r, r, parent)
        self.x = x
        self.y = y
        self.r = r
        self.parent = parent
        self.edges = []
        self.input_flag = input_flag
        #self.united = []

        self.setFlags(self.ItemSendsScenePositionChanges)
        self.acceptTouchEvents()

    def addEdge(self, edgeItem):
        for existing in self.edges:
            if edgeItem.equal(existing):
                return False
        self.edges.append(edgeItem)
        #self.united.append(edgeItem.controlPoints()[0] if edgeItem.controlPoints()[0] != self else edgeItem.controlPoints()[1])

        return True

    def removeEdge(self, edgeItem):
        #print(self.edges)
        for existing in self.edges:
            if edgeItem.equal(existing):
                self.scene().removeItem(existing)
                self.edges.remove(existing)
                return True
        return False

    def itemChange(self, change, value):
        for edge in self.edges:
            edge.updateEdge(self)
        return super().itemChange(change, value)


class FilterBoxWidget(QtWidgets.QWidget):

    def __init__(self, func_name, func_args, w, h):
        super(FilterBoxWidget, self).__init__()

        self.w, self.h = w, h

        self.view_button = None
        self.name = func_name
        self.args = func_args
        self.edits = dict()
        self.initUI()

    def initUI(self):

        vbox = QVBoxLayout(self)
        name_label = QLabel(self.name)
        grid = QGridLayout(self)
        grid.setSpacing(10)
        for i, arg in enumerate(self.args):
            label = QLabel(arg)
            edit = QLineEdit()
            self.edits[arg] = edit
            grid.addWidget(label, i, 0)
            grid.addWidget(edit, i, 1)
        self.view_button = QPushButton("View")
        vbox.addWidget(name_label)
        vbox.addLayout(grid)
        vbox.addWidget(self.view_button)
        self.setMaximumSize(self.w, self.h)


class FilterBoxItem(QGraphicsRectItem):

    def __init__(self, x, y, w, h, func_name, func_args):
        super().__init__()
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.proxy = QGraphicsProxyWidget()
        self.filterWidget = FilterBoxWidget(func_name, func_args, w, h)
        self.proxy.setWidget(self.filterWidget)
        self.proxy.setParentItem(self)


class NodeItem(QGraphicsItem):

    def __init__(self, x, y, w, h, n_in, n_out, filter):
        super().__init__()
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.r = 10
        self.n_in = n_in
        self.n_out = n_out
        self.filter = filter

        self.filterBox = FilterBoxItem(x, y, w, h, filter.name, filter.args)
        self.filterBox.setParentItem(self)

        self.view_button = self.filterBox.filterWidget.view_button

        self.inp_points = []
        self.out_points = []

        self.in_step = (h - n_in * 2 * self.r) // (n_in + 1)
        for i in range(n_in):
            self.inp_points.append(MountPointItem(x - self.r - 1, y + self.in_step * (i + 1) + self.r + i * 2 * self.r,
                                                  self.r, self, True))
            self.inp_points[-1].setX(x - self.r - 1)
            self.inp_points[-1].setY(y + self.in_step * (i + 1) + self.r + i * 2 * self.r)
            self.inp_points[-1].setParentItem(self)

        self.out_step = (h - n_out * 2 * self.r) // (n_out + 1)
        for i in range(n_out):
            self.out_points.append(MountPointItem(x + w + self.r + 1, y + self.out_step * (i + 1) + self.r + i * 2 * self.r,
                                                  self.r, self, False))
            self.out_points[-1].setX(x + w + self.r + 1)
            self.out_points[-1].setY(y + self.out_step * (i + 1) + self.r + i * 2 * self.r)
            self.out_points[-1].setParentItem(self)

        self.setFlags(QGraphicsItem.ItemIsMovable)
        self.setAcceptTouchEvents(True)

    def boundingRect(self):
        bound_rect = QRectF(-2 * (self.r + 1), 0, self.w + 4 * (self.r + 1), self.h)
        return bound_rect

    def update_delete_flag(self, flag):
        self.delete_flag = flag

    '''def addUnited(self, my_point, other_point):
        if my_point in self.inp_points:
            self.out_nodes.append(other_point.parent)
        if my_point in self.out_points:
            self.inp_nodes.append(other_point.parent)'''

    def paint(self, painter, option, widget=...):
        # иначе warning-ами сыпет, но работает
        self.filterBox.paint(painter, option, widget)
        #painter.drawRect(self.boundingRect())
        '''for point in self.inp_points:
            point.paint(painter, option, widget)
        for point in self.out_points:
            point.paint(painter, option, widget)'''


class GraphicsScene(QGraphicsScene):
    startItem = newConnection = None
    edges = []
    delete_flag = False
    deleted_items = set()

    def removeEdge(self, new_edge):
        for edge in self.edges:
            if new_edge.equal(edge):
                self.edges.remove(edge)

    def controlPointAt(self, pos):
        mask = QPainterPath()
        mask.setFillRule(QtCore.Qt.WindingFill)
        for item in self.items(pos):
            if self.delete_flag and isinstance(item, NodeItem):
                return item
            if mask.contains(pos):
                return
            if isinstance(item, MountPointItem):
                return item

            if not isinstance(item, Edge):
                mask.addPath(item.shape().translated(item.scenePos()))

    def mousePressEvent(self, event):
        #print(self.delete_flag)
        if event.button() == QtCore.Qt.LeftButton:
            item = self.controlPointAt(event.scenePos())
            if item and not self.delete_flag:
                self.startItem = item
                self.newConnection = Edge(item, event.scenePos())
                self.addItem(self.newConnection)
                return
            if item:
                new_edges = []
                for edge in self.edges:
                    if item in edge.controlParents():
                        if not edge.start.removeEdge(edge):
                            edge.end.removeEdge(edge)
                    else:
                        new_edges.append(edge)
                self.edges = new_edges
                self.deleted_items.add(item)
                self.removeItem(item)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if item and (not self.delete_flag) and item != self.startItem:
                p2 = item.scenePos()
            else:
                p2 = event.scenePos()
            self.newConnection.setP2(p2)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if item and (not self.delete_flag) and item != self.startItem:
                self.newConnection.setEnd(item)
                if self.startItem.addEdge(self.newConnection):
                    item.addEdge(self.newConnection)
                    self.edges.append(self.newConnection)
                else:
                    self.startItem.removeEdge(self.newConnection)
                    item.removeEdge(self.newConnection)
                    self.removeItem(self.newConnection)
                    self.removeEdge(self.newConnection)
            else:
                self.removeItem(self.newConnection)
        self.startItem = self.newConnection = None
        super().mouseReleaseEvent(event)

    def update_delete_flag(self, flag):
        self.delete_flag = flag
        #print(self.edges)

