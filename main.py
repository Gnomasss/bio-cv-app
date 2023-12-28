import sys
from functools import partial

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication, QFileDialog, QMainWindow, QAction, \
    QVBoxLayout, QPushButton, QGridLayout, QLineEdit, QTextEdit, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QEvent, QObject, QPoint
import cv2
import numpy as np

import func2action


class MouseTracker(QObject):
    positionChanged = pyqtSignal(QPoint)
    buttonPressed = pyqtSignal(QPoint)
    buttonReleased = pyqtSignal(QPoint)

    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self):
        return self._widget

    def eventFilter(self, obj, event):
        if obj is self.widget and event.type() == QEvent.MouseMove:
            self.positionChanged.emit(event.pos())

        if obj is self.widget and event.type() == QEvent.MouseButtonPress:
            self.buttonPressed.emit(event.pos())

        if obj is self.widget and event.type() == QEvent.MouseButtonRelease:
            self.buttonReleased.emit(event.pos())

        return super().eventFilter(obj, event)


class MainWindow(QMainWindow):
    @staticmethod
    def resize_img(img, scale):
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)
        dim = (width, height)
        return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    def __init__(self):
        self.parent = super().__init__()
        self.image = None
        self.action_seq = list()

        self.img_scroll_area = QScrollArea(self)
        self.img_scroll_area.setWidgetResizable(True)
        self.img_label = QLabel(self)
        self.img_label.setScaledContents(True)
        self.img_scroll_area.setWidget(self.img_label)

        self.mouse_tracker = MouseTracker(self.img_label)
        self.mouse_tracker.buttonPressed.connect(self.mouse_press)
        self.mouse_tracker.buttonReleased.connect(self.mouse_released)
        self.mouse_tracker.positionChanged.connect(self.mouse_move)

        self.crop_area = None
        self.tmp_img = None
        self.arg_window = None
        self.arg_seq_window = None

        self.centralWidget = QWidget(self.parent)
        self.initUI()

    def initUI(self):
        self.setCentralWidget(self.centralWidget)
        grid = QGridLayout(self.centralWidget)

        vbox = QVBoxLayout(self.centralWidget)
        funcs_list = func2action.all_func()

        for method in funcs_list:
            button = QPushButton(method.name)
            button.clicked.connect(partial(self.get_filter_args, method=method))
            vbox.addWidget(button)

        hbox = QHBoxLayout(self.centralWidget)
        hbox.addLayout(vbox)
        hbox.addWidget(self.img_scroll_area)

        grid.addLayout(hbox, 0, 0, 1, 2)

        open_action = QAction(QIcon('open.png'), '&Open', self)
        open_action.setShortcut('Ctrl+W')
        open_action.setStatusTip('Open image')
        open_action.triggered.connect(self.get_img)

        save_action = QAction(QIcon("save.png"), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save image')
        save_action.triggered.connect(self.save_img)

        zoom_in_action = QAction(QIcon("zoom_in.png"), '&Zoom+', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.setStatusTip('Zoom in image')
        zoom_in_action.triggered.connect(self.zoom_in_img)

        zoom_out_action = QAction(QIcon("zoom_out.png"), '&Zoom-', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.setStatusTip('Zoom out image')
        zoom_out_action.triggered.connect(self.zoom_out_img)

        show_action_seq = QAction(QIcon("actions_seq.jpg"), '&Show', self)
        show_action_seq.setStatusTip('Show the action sequence')
        show_action_seq.triggered.connect(self.show_action_sequence)

        crop_image_action = QAction(QIcon("crop_image.png"), "&Crop", self)
        crop_image_action.setStatusTip("Crop the image")
        crop_image_action.triggered.connect(self.crop_image)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)

        zoom_in_tool = self.addToolBar('Zoom in')
        zoom_in_tool.addAction(zoom_in_action)

        zoom_out_tool = self.addToolBar('Zoom out')
        zoom_out_tool.addAction(zoom_out_action)
        crop_image_tool = self.addToolBar("Croop")
        crop_image_tool.addAction(crop_image_action)

        show_action_tool = self.addToolBar('Show action sequence')
        show_action_tool.addAction(show_action_seq)

        self.showMaximized()
        self.setWindowTitle('Img')
        self.show()

    def get_img(self):
        filename = QFileDialog.getOpenFileName()[0]
        self.image = cv2.imread(filename)
        self.set_photo(self.image)

    def set_photo(self, img):
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        self.img_label.setPixmap(QPixmap.fromImage(img))

    def zoom_in_img(self):
        self.image = self.resize_img(self.image, 1.1)
        self.set_photo(self.image)

    def zoom_out_img(self):
        self.image = self.resize_img(self.image, 0.9)
        self.set_photo(self.image)

    def save_img(self):
        filename = QFileDialog.getSaveFileName()[0]
        cv2.imwrite(filename, self.image)
        self.statusBar().showMessage("Image save")

    def get_filter_args(self, method):
        self.arg_window = FilterArgWindow(method, self)
        self.arg_window.show()

    def apply_filter(self, method, action_args):
        self.action_seq.append((method.name, action_args))
        self.image = method.func(self.image, **action_args)
        self.set_photo(self.image)

    def show_action_sequence(self):
        self.arg_seq_window = ActionSeqWindow(self.action_seq)
        self.arg_seq_window.show()

    @pyqtSlot(QPoint)
    def mouse_press(self, pos):
        if self.tmp_img is not None:
            self.crop_area = np.array([[pos.x(), pos.y()]])

    @pyqtSlot(QPoint)
    def mouse_move(self, pos):

        if self.crop_area is not None:
            img_size = np.array(self.image.shape[:2])[::-1]
            lable_size = np.array([self.img_label.size().width(), self.img_label.size().height()])
            if np.size(self.crop_area, axis=0) == 1:
                self.crop_area = np.append(self.crop_area, [[pos.y(), pos.x()]], axis=0)
            else:
                self.crop_area[1] = np.array([pos.x(), pos.y()])
            tmp_image_copy = self.tmp_img.copy()
            points = (self.crop_area / lable_size * img_size).astype(int)
            cv2.rectangle(tmp_image_copy, points[0], points[1], (255, 255, 255), 3)
            self.set_photo(tmp_image_copy)

    @pyqtSlot(QPoint)
    def mouse_released(self, pos):
        if self.crop_area is not None:
            self.crop_area[1] = [pos.x(), pos.y()]
            self.crop_image()

    def crop_image(self):
        if self.crop_area is None:
            mat = np.ones(self.image.shape, dtype='uint8') * 70
            self.tmp_img = cv2.subtract(self.image, mat)
            self.set_photo(self.tmp_img)
        elif len(self.crop_area) == 2:
            img_size = np.array(self.image.shape[:2])[::-1]
            lable_size = np.array([self.img_label.size().width(), self.img_label.size().height()])

            np.sort(self.crop_area, axis=1)

            self.crop_area = (self.crop_area / lable_size * img_size).astype(int)
            self.image = self.image[self.crop_area[0, 1]:self.crop_area[1, 1],
                        self.crop_area[0, 0]:self.crop_area[1, 0]].copy()
            self.tmp_img = None
            self.crop_area = None
            self.set_photo(self.image)


class FilterArgWindow(QMainWindow):
    def __init__(self, method, parent=None):
        super(FilterArgWindow, self).__init__(parent)
        self.parent = parent
        self.method = method
        self.centralWidget = QWidget(self)
        self.edits = None
        self.initGui()

    def initGui(self):
        self.setCentralWidget(self.centralWidget)
        grid = QGridLayout(self.centralWidget)
        grid.setSpacing(10)
        self.edits = dict()
        for i, arg in enumerate(self.method.args):
            label = QLabel(arg)
            edit = QLineEdit()
            self.edits[arg] = edit
            grid.addWidget(label, i, 0)
            grid.addWidget(edit, i, 1)

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply)
        grid.addWidget(apply_button, len(self.method.args), 0)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel)
        grid.addWidget(cancel_button, len(self.method.args), 1)

        self.resize(100, 100)
        self.setWindowTitle(f'Argument function {self.method.name}')

    def cancel(self):
        self.parent.action_args = None
        self.close()

    def apply(self):
        action_args = dict()
        for arg in self.edits:
            action_args[arg] = float(self.edits[arg].text())
        self.close()
        self.parent.apply_filter(self.method, action_args)


class ActionSeqWindow(QMainWindow):
    def __init__(self, action_seq):
        super().__init__()
        self.seq = action_seq
        self.textEdit = QTextEdit()
        self.initUI()

    def initUI(self):
        self.setCentralWidget(self.textEdit)
        self.textEdit.setPlainText("")

        for name, args in self.seq:
            self.textEdit.append(f"{name}\n")
            for arg in args:
                self.textEdit.append(f"{arg}: {args[arg]} ")
            self.textEdit.append('\n')

        self.resize(500, 500)
        self.setWindowTitle("Seq of arguments")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
