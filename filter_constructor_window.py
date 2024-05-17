import sys
from functools import partial
from pathlib import Path

import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsEllipseItem, QGraphicsRectItem,
                             QGraphicsProxyWidget, QGridLayout, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QPushButton, QWidget, QAction, QFileDialog, QToolButton, QToolBar, QMessageBox)
from PyQt5.QtGui import QPainter, QIcon, QColor, QFont
from PyQt5.QtCore import QSize, Qt
from PyQt5 import QtCore, QtWidgets

import func2action
import special_filters_for_scene
from filter_box_scene import NodeItem, GraphicsScene, Edge
from derivative_windows import TestImageWindow, ImgInfoWindow

FONT_SIZE = 16


class ConstructorWindow(QMainWindow):
    def __init__(self, basic_action_seq):
        self.parent = super().__init__()

        self.font = QFont()
        self.font.setPointSize(FONT_SIZE)
        self.basic_action_seq = basic_action_seq

        self.imgs = []
        self.img_names = []
        self.res_imgs = []

        self.test_img_windows = []
        self.test_img = None

        self.delete_flag = False

        self.my_scene = None
        self.view = None

        self.funcs_list = None
        self.input_nodes = set()
        self.output_nodes = set()
        self.filters_box = None

        self.centralWidget = QWidget(self.parent)
        self.initUI()

    def initUI(self):

        self.setFont(self.font)
        #filters = func2action.all_func()
        self.setCentralWidget(self.centralWidget)

        self.filters_box = QVBoxLayout()
        self.add_filters()

        self.my_scene = GraphicsScene()
        self.view = QGraphicsView(self.centralWidget)
        self.view.setScene(self.my_scene)
        self.view.setBackgroundBrush(QColor(170, 170, 170, 255))
        self.view.resize(1000, 600)
        #self.view.setMinimumSize(200, 200)
        self.view.setRenderHints(QPainter.Antialiasing)

        self.hbox = QHBoxLayout(self.centralWidget)

        self.hbox.addLayout(self.filters_box)
        self.hbox.addWidget(self.view)
        #self.view.setFocus()
        #self.showMaximized()
        self.resize(600, 600)

        icons_folder = Path("icons")

        test_action = QAction(QIcon(str(icons_folder / 'info_message.png')), "&Test", self)
        test_action.setStatusTip("Test")
        test_action.triggered.connect(self.test)

        get_imgs_action = QAction(QIcon(str(icons_folder / "open.png")), "&Open", self)
        get_imgs_action.setStatusTip("Open")
        get_imgs_action.triggered.connect(self.get_imgs)

        get_test_img_action = QAction(QIcon(str(icons_folder / "open.png")), "&Open test image", self)
        get_test_img_action.setStatusTip("Open test image")
        get_test_img_action.triggered.connect(self.get_test_img)

        save_imgs_action = QAction(QIcon(str(icons_folder / "save.png")), "&Save", self)
        save_imgs_action.setStatusTip("Save")
        save_imgs_action.triggered.connect(self.get_save_path)

        start_alg_action = QAction(QIcon(str(icons_folder / "start.jpg")), "&Start", self)
        start_alg_action.setStatusTip("Start")
        start_alg_action.triggered.connect(self.start_processing)

        save_script_action = QAction(QIcon(str(icons_folder / "save.png")), "&Save script", self)
        save_script_action.setStatusTip("Save script")
        save_script_action.triggered.connect(self.save_script)

        delete_node_action = QToolButton(self)
        delete_node_action.setIcon(QIcon(str(icons_folder / "delete_node.png")))
        delete_node_action.setCheckable(True)
        delete_node_action.setStatusTip("Delete")
        delete_node_action.toggled.connect(self.delete_node)


        self.statusBar()

        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(get_imgs_action)
        fileMenu.addAction(save_imgs_action)
        fileMenu.addAction(get_test_img_action)
        fileMenu.addAction(save_script_action)

        self.add_2_tool_bar(test_action, "test_action")
        self.add_2_tool_bar(start_alg_action, "Start image processing")

        self.formatbar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.formatbar)
        self.formatbar.addWidget(delete_node_action)

        self.init_basic_nodes()

        self.show()

    def init_basic_nodes(self):
        nodes = [self.newNode(func2action.Func("input", special_filters_for_scene.input, None), 0, 1)]
        for i, (method, args) in enumerate(self.basic_action_seq):
            nodes.append(self.newNode(method, 1, 1))
            nodes[-1].setX(250 * (i + 1))
            for arg in args:
                nodes[-1].filterBox.filterWidget.edits[arg].setText(str(args[arg]))
        nodes.append(self.newNode(func2action.Func("output", special_filters_for_scene.output, None), 1, 0))
        nodes[-1].setX(250 * (len(self.basic_action_seq) + 1))
        for i in range(1, len(nodes)):
            point1 = nodes[i - 1].out_points[0]
            point2 = nodes[i].inp_points[0]
            edge = Edge(point1, point2.scenePos())
            edge.setEnd(point2)
            self.my_scene.edges.append(edge)
            self.my_scene.addItem(edge)
            point1.addEdge(edge)
            point2.addEdge(edge)
        self.input_nodes.add(nodes[0])
        self.output_nodes.add(nodes[-1])

    def get_imgs(self):
        self.imgs = []
        self.res_imgs = []
        filenames = QFileDialog.getOpenFileNames()[0]
        if filenames != "":
            for filename in filenames:
                img = cv2.imread(filename)
                self.imgs.append(img)
                self.img_names.append(Path(filename).name)

    def get_test_img(self):
        self.test_img_windows.clear()
        filename = QFileDialog.getOpenFileName()[0]
        if filename != "":
            self.test_img = cv2.imread(filename)

    def update_delete_flag(self):
        self.delete_flag = not self.delete_flag
        self.my_scene.update_delete_flag(self.delete_flag)

    def delete_node(self):
        self.update_delete_flag()
        if self.delete_flag:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            #print(self.my_scene.deleted_items)
            self.input_nodes = self.input_nodes - self.my_scene.deleted_items
            self.output_nodes = self.output_nodes - self.my_scene.deleted_items
            self.my_scene.deleted_items.clear()

    def get_save_path(self):
        save_path = QFileDialog.getSaveFileName()[0]
        self.save_imgs(Path(save_path).parents[0])

    def add_2_tool_bar(self, action, descr):
        tool = self.addToolBar(descr)
        tool.addAction(action)

    def newNode(self, filter, n_in, n_out):
        x = 0
        y = 0
        w = max(215, len(filter.name) * 11)
        h = 40 * (len(filter.args) + 2) + 5
        if len(filter.args) == 0:
            w = max(115, len(filter.name) * 12)
            #w = 90
            h = 85

        node = NodeItem(x, y, w, h, n_in, n_out, filter)
        if n_out == 1 and n_in == 0:
            self.input_nodes.add(node)
        if n_out == 0 and n_in == 1:
            self.output_nodes.add(node)
        self.my_scene.addItem(node)
        node.filterBox.filterWidget.setFont(self.font)
        node.view_button.clicked.connect(partial(self.test_processing, node=node))
        return node

    def add_filters(self):
        self.funcs_list = func2action.all_func() + func2action.all_spec_func(special_filters_for_scene)

        for method in self.funcs_list:
            button = QPushButton(method.name)
            n_in, n_out = self.io_points(method.name)
            button.clicked.connect(partial(self.newNode, filter=method, n_in=n_in, n_out=n_out))
            button.setStatusTip(method.description)
            self.filters_box.addWidget(button)

    @staticmethod
    def io_points(func_name):
        if func_name == 'split':
            return 1, 2
        if func_name == 'input':
            return 0, 1
        if func_name == 'output':
            return 1, 0
        if 'bitwise' == func_name[:7] and ('not' not in func_name):
            return 2, 1
        return 1, 1

    @staticmethod
    def box2filter_with_args(node):
        filter_args = dict()
        for arg in node.filterBox.filterWidget.edits:
            filter_args[arg] = float(node.filterBox.filterWidget.edits[arg].text())
        return partial(node.filter.func, **filter_args)

    def create_graph(self):
        graph = dict()
        for edge in self.my_scene.edges:
            for i in range(len(edge.controlPoints())):
                point = edge.controlPoints()[i]
                anotherPoint = edge.controlPoints()[(i + 1) % 2]
                if not point.input_flag:
                    if point.parent not in graph:
                        graph[point.parent] = [anotherPoint.parent]
                    else:
                        graph[point.parent].append(anotherPoint.parent)
                    break
        return graph

    def apply_img(self, orig_img, graph, out_node):
        #graph = self.create_graph()
        queue_nodes = list(self.input_nodes)
        node_with_imgs = dict()
        for node in self.input_nodes:
            node_with_imgs[node] = [orig_img.copy()]

        while queue_nodes:
            node = queue_nodes.pop(0)
            imgs = node_with_imgs[node]

            if node.n_in != len(imgs) and node.n_in != 0:
                queue_nodes.append(node)
                continue
            output = self.box2filter_with_args(node)(imgs if node.n_in > 1 else imgs[0])
            new_imgs = output if node.n_out > 1 else [output]
            if node.n_out == 0:
                continue
            if out_node and node is out_node:
                return new_imgs

            # assert len(new_imgs) == len(graph[node]), "incorrect graph"

            for i in range(len(graph[node])):
                if graph[node][i] not in node_with_imgs:
                    node_with_imgs[graph[node][i]] = [new_imgs[i]]
                else:
                    node_with_imgs[graph[node][i]].append(new_imgs[i])
                if len(node_with_imgs[graph[node][i]]) == graph[node][i].n_in:
                    queue_nodes.append(graph[node][i])
        res = []
        for out in self.output_nodes:
            res.append(node_with_imgs[out][0])
        return res

    def start_processing(self):
        graph = self.create_graph()
        for img in self.imgs:
            res_imgs = self.apply_img(img, graph, None)
            self.res_imgs.append(res_imgs)
            '''for i in range(len(res_imgs)):
                suf_ind = filename.find('.')
                cv2.imwrite(f"{filename[:suf_ind]}_{i}{filename[suf_ind:]}", res_imgs[i])'''

    def save_imgs(self, path):
        for img_name, res_img in zip(self.img_names, self.res_imgs):
            for i in range(len(res_img)):
                suf_ind = img_name.find('.')
                cv2.imwrite(str(path / f"{img_name[:suf_ind]}_{i}{img_name[suf_ind:]}"), res_img[i])

    def test(self):
        if self.test_img is not None:
            # self.test_img_windows.clear()
            graph = self.create_graph()
            res = self.apply_img(self.test_img, graph, None)
            for i, img in enumerate(res):
                cv2.imwrite(f"test_img_{i}.jpeg", img)
        else:
            error_message = QMessageBox()
            error_message.setText("Error")
            error_message.setInformativeText("Please select a test image")
            error_message.exec_()

    '''def test(self):
        graph = self.create_graph()
        orig_img = cv2.imread("akira.jpeg")
        res_imgs = self.apply_img(orig_img, graph, None)
        for i in range(len(res_imgs)):
            cv2.imwrite(f"akira_{i}.jpeg", res_imgs[i])'''

    def test_processing(self, node):
        if self.test_img is not None:
            #self.test_img_windows.clear()
            graph = self.create_graph()
            res = self.apply_img(self.test_img, graph, node)

            for img in res:
                self.test_img_windows.append(TestImageWindow(img))
                #img_window.setParent(self)
                self.test_img_windows[-1].show()
        else:
            error_message = QMessageBox()
            error_message.setText("Error")
            error_message.setInformativeText("Please select a test image")
            error_message.exec_()

    def open_script(self):
        #open_script_path = QFileDialog.getSaveFileName()[0]
        open_script_path = "/home/pashnya/Documents/test/test.txt"
        if open_script_path:
            #self.input_nodes.clear()
            #self.output_nodes.clear()
            graph = dict()
            filter_names = dict()
            filters = list()
            for filter in self.funcs_list:
                filter_names[filter.name] = filter
            with open(open_script_path) as f:
                n = int(f.readline())
                for _ in range(n):
                    inp = f.readline().split('#')
                    name = inp[0]
                    args = dict([(x.split(':')[0], float(x.split(':')[1])) for x in inp[1:-1] if ':' in x])
                    filters.append([filter_names[name], args])
                for i in range(n):
                    childs = f.readline().split()
                    childs[-1] = childs[-1][:-2]
                    graph[filters[i]] = [filters[int(child)] for child in childs]

            self.input_nodes.clear()
            self.output_nodes.clear()
            for filter in filters:
                if filter[0].name == "input":
                    self.input_nodes.append(self.newNode(filter[0], 0, 1))
                elif filter[0].name == "output":
                    self.input_nodes.append(self.newNode(filter[0], 1, 0))
                # не могу сейчас дописать отрисовку считанного графа
                # не буду пока ее никуда добавлять

    def save_script(self):
        graph = None
        try:
            graph = self.create_graph()
        except Exception:
            error_message = QMessageBox()
            error_message.setText("Error")
            error_message.setInformativeText("Please create correct script")
            error_message.exec_()
        if graph:
            save_script_path = QFileDialog.getSaveFileName()[0]
            #save_script_path = "/home/pashnya/Documents/test/test.txt"
            with open(save_script_path, 'w') as f:
                f.write(f"{len(graph) + len(self.output_nodes)}\n")
                node_index = dict()
                ind = 0
                for node in graph:
                    node_index[node] = ind
                    ind += 1
                    f.write(f"{node.filter.name}#")
                    for arg in node.filterBox.filterWidget.edits:
                        value = node.filterBox.filterWidget.edits[arg].text()
                        f.write(f"{arg}:{value}#")
                    f.write("\n")
                for output in self.output_nodes:
                    node_index[output] = ind
                    ind += 1
                    f.write(f"{output.filter.name}#\n")

                for node in node_index:
                    if node in graph:
                        for child in graph[node]:
                            f.write(f"{node_index[child]} ")
                    f.write("\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ConstructorWindow([])
    w.show()
    sys.exit(app.exec_())
