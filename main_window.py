import sys
import os
from functools import partial
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication, QFileDialog, QMainWindow, QAction, \
    QVBoxLayout, QPushButton, QGridLayout, QLineEdit, QTextEdit, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QEvent, QObject, QPoint, QTimer
import numpy as np
import cv2

import func2action
from derivative_windows import *
from img_window import ImageWindow

FONT_SIZE = 16


class MainWindow(QMainWindow):

    @staticmethod
    def resize_img(img, scale):
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)
        dim = (width, height)
        return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    def __init__(self):

        self.parent = super().__init__()

        self.versin = 0.1
        self.github_url = "https://github.com/Gnomasss/bio-cv-app"

        self.img = None
        self.imgs_list = None
        self.img_index = None

        self.img_window = ImageWindow(self)

        self.action_seq = list()

        self.crop_area = None
        self.tmp_img = None
        self.arg_window = None
        self.arg_seq_window = None
        self.funcs_list = None
        self.filters_box = None
        self.info_window = None
        self.img_info_window = None
        self.imgs_seq_info_window = None

        self.centralWidget = QWidget(self.parent)
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.setFont(font)

        self.setCentralWidget(self.centralWidget)

        hbox = QHBoxLayout(self.centralWidget)

        self.filters_box = QVBoxLayout(self.centralWidget)

        self.add_filters()

        hbox.addLayout(self.filters_box)

        hbox.addWidget(self.img_window)

        icons_folder = Path("icons")

        # Make actions
        ################################

        open_action = QAction(QIcon(str(icons_folder / "open.png")), '&Open image', self)
        open_action.setShortcut('Ctrl+W')
        open_action.setStatusTip('Open image')
        open_action.triggered.connect(self.get_img)

        save_action = QAction(QIcon(str(icons_folder / "save.png")), '&Save image', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save image')
        save_action.triggered.connect(self.save_img)

        add_img_action = QAction(QIcon(str(icons_folder / "add_image.png")), '&Add image to list', self)
        add_img_action.setShortcut('Ctrl+O')
        add_img_action.setStatusTip('Add image to list')
        add_img_action.triggered.connect(self.add_new_image_2list)

        zoom_in_action = QAction(QIcon(str(icons_folder / "zoom_in.png")), '&Zoom in', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.setStatusTip('Zoom in image')
        zoom_in_action.triggered.connect(self.zoom_in_img)

        zoom_out_action = QAction(QIcon(str(icons_folder / "zoom_out.png")), '&Zoom out', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.setStatusTip('Zoom out image')
        zoom_out_action.triggered.connect(self.zoom_out_img)

        show_action_seq = QAction(QIcon(str(icons_folder / "actions_seq.png")), '&Show filters sequence', self)
        show_action_seq.setStatusTip('Show the filters sequence')
        show_action_seq.triggered.connect(self.show_action_sequence)

        add_filters_action = QAction(QIcon(str(icons_folder / "new_filters.png")), '&Add new filters from file', self)
        add_filters_action.setStatusTip('Add filters from file')
        add_filters_action.triggered.connect(self.get_new_filters)

        crop_image_action = QAction(QIcon(str(icons_folder / "crop_image.png")), "&Crop image", self)
        crop_image_action.setStatusTip("Crop the image")
        crop_image_action.triggered.connect(self.crop_image)

        open_info_message_action = QAction(QIcon(str(icons_folder / "info_message.png")), "&Info about app", self)
        open_info_message_action.setStatusTip("Open info about app")
        open_info_message_action.triggered.connect(self.open_info_message)

        open_img_info_message_action = QAction(QIcon(str(icons_folder / "img_info.png")), "&Info about image", self)
        open_img_info_message_action.setStatusTip("Open info about image")
        open_img_info_message_action.triggered.connect(self.open_img_info)

        next_img_action = QAction(QIcon(str(icons_folder / "next_img.png")), "&Next image in list", self)
        next_img_action.setStatusTip("Next image in list")
        next_img_action.triggered.connect(self.next_img)

        prev_img_action = QAction(QIcon(str(icons_folder / "prev_img.png")), "&Previous image in list", self)
        prev_img_action.setStatusTip("Previous image in list")
        prev_img_action.triggered.connect(self.prev_img)

        open_info_seq_imgs_action = QAction(QIcon(str(icons_folder / "img_list.png")), "&Info about images list", self)
        open_info_seq_imgs_action.setStatusTip("Open info about images list")
        open_info_seq_imgs_action.triggered.connect(self.open_info_img_seq)

        rotate_img_action = QAction(QIcon(str(icons_folder / "rotate.png")), "&Flip image", self)
        rotate_img_action.setStatusTip("Rotate image by 90 degrees")
        rotate_img_action.triggered.connect(self.flip_img)

        ###########################

        self.statusBar()

        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)

        filtersMenu = menubar.addMenu('&Filters')
        filtersMenu.addAction(add_filters_action)
        filtersMenu.addAction(show_action_seq)

        img_seqMenu = menubar.addMenu('&Images')
        img_seqMenu.addAction(open_img_info_message_action)
        img_seqMenu.addAction(add_img_action)
        img_seqMenu.addAction(next_img_action)
        img_seqMenu.addAction(prev_img_action)
        img_seqMenu.addAction(open_info_seq_imgs_action)

        infoMenu = menubar.addMenu('&Info')
        infoMenu.addAction(open_info_message_action)

        ##################

        self.add_2_tool_bar(zoom_in_action, "Zoom in")
        self.add_2_tool_bar(zoom_out_action, "Zoom out")
        self.add_2_tool_bar(crop_image_action, "Crop")
        self.add_2_tool_bar(rotate_img_action, "Rotate image")
        #self.add_2_tool_bar(show_action_seq, "Show action sequence")
        #self.add_2_tool_bar(add_filters_action, "Add new filters")
        #self.add_2_tool_bar(open_info_message_action, "Show infromation about ap")
        #self.add_2_tool_bar(open_img_info_message_action, "Show infromation about image")
        #self.add_2_tool_bar(next_img_action, "Next image in sequence")
        #self.add_2_tool_bar(prev_img_action, "Previous image in sequence")
        #self.add_2_tool_bar(open_info_seq_imgs_action, "Show info about img seq")

        #########################

        # self.showMaximized()
        self.setWindowTitle('Img')
        self.show()

    def add_2_tool_bar(self, action, descr):
        tool = self.addToolBar(descr)
        tool.addAction(action)

    def update_img_list(self):
        self.imgs_list[self.img_index] = self.img

    def get_img(self):
        filename = QFileDialog.getOpenFileName()[0]
        self.img = cv2.imread(filename)
        self.imgs_list = [self.img]
        self.img_index = 0
        self.img_window.set_img(self.img)

    def zoom_in_img(self):
        self.img = self.resize_img(self.img, 1.1)
        self.update_img_list()
        self.img_window.set_img(self.img)

    def zoom_out_img(self):
        self.img = self.resize_img(self.img, 0.9)
        self.update_img_list()
        self.img_window.set_img(self.img)

    def flip_img(self):
        self.img = cv2.rotate(self.img, cv2.ROTATE_90_CLOCKWISE)
        self.update_img_list()
        self.img_window.set_img(self.img)

    def save_img(self):
        filename = QFileDialog.getSaveFileName()[0]
        cv2.imwrite(filename, self.img)
        self.statusBar().showMessage("Image save")

    def add_new_image_2list(self):
        filename = QFileDialog.getOpenFileName()[0]
        self.img = cv2.imread(filename)
        self.imgs_list.append(self.img)
        self.img_index = len(self.imgs_list) - 1
        self.img_window.set_img(self.img)

    def crop_image(self):
        if self.img_window.points is None:
            mat = np.ones(self.img.shape, dtype='uint8') * 70
            self.tmp_img = cv2.subtract(self.img, mat)
            self.img_window.set_img(self.tmp_img)
            self.img_window.draw_mode_on()

        elif len(self.img_window.points) == 2:
            crop_area = np.array(self.img_window.points)
            np.sort(crop_area, axis=1)

            self.img = self.img[crop_area[0, 1]:crop_area[1, 1],
                       crop_area[0, 0]:crop_area[1, 0]].copy()
            self.update_img_list()

            self.tmp_img = None
            self.img_window.draw_mode_off()
            self.img_window.set_img(self.img)

    def get_new_filters(self):
        filters_file_path = QFileDialog.getOpenFileName()[0]
        new_funcs_list = func2action.all_func_from_file(filters_file_path)
        self.add_filters(new_funcs_list)

    def add_filters(self, new_funcs_list=None):
        if new_funcs_list is None:
            self.funcs_list = func2action.all_func()
        else:
            for i in reversed(range(self.filters_box.count())):
                self.filters_box.itemAt(i).widget().setParent(None)

            new_funcs_names = set([func.name for func in new_funcs_list])

            self.funcs_list = [method for method in self.funcs_list if method.name not in new_funcs_names]

            self.funcs_list += new_funcs_list

        for method in self.funcs_list:
            button = QPushButton(method.name)
            button.clicked.connect(partial(self.get_filter_args, method=method))
            button.setStatusTip(method.description)
            self.filters_box.addWidget(button)

    def open_info_message(self):
        self.info_window = InfoMessageWindow(self.versin, self.github_url)
        self.info_window.show()

    def open_img_info(self):
        self.img_info_window = ImgInfoWindow(self.img)
        self.img_info_window.show()

    def next_img(self):
        self.img_index += 1
        self.img = self.imgs_list[self.img_index % len(self.imgs_list)]
        self.img_index %= len(self.imgs_list)
        self.img_window.set_img(self.img)

    def prev_img(self):
        self.img_index -= 1
        self.img = self.imgs_list[self.img_index % len(self.imgs_list)]
        self.img_index %= len(self.imgs_list)
        self.img_window.set_img(self.img)

    def open_info_img_seq(self):
        self.imgs_seq_info_window = ImgsSeqInfoWindow(self.imgs_list, self.img_index)
        self.imgs_seq_info_window.show()

    def get_filter_args(self, method):
        self.arg_window = FilterArgWindow(method, self)
        self.arg_window.show()

    def apply_filter(self, method, action_args):
        self.action_seq.append((method.name, action_args))
        self.imgs_list = [method.func(img, **action_args) for img in self.imgs_list]
        self.img = self.imgs_list[self.img_index]
        self.img_window.set_img(self.img)

    def show_action_sequence(self):
        self.arg_seq_window = ActionSeqWindow(self.action_seq)
        self.arg_seq_window.show()



if __name__ == '__main__':
    try:
        os.chdir(sys._MEIPASS)
    except Exception:
        base_path = os.path.abspath(".")

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
