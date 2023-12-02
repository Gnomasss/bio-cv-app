import sys
from functools import partial

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication, QFileDialog, QMainWindow, QAction, qApp, \
    QVBoxLayout, QPushButton, QGridLayout, QLineEdit, QTextEdit
from PyQt5.QtGui import QPixmap, QImage, QIcon
import cv2

import func2action


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
        self.img_label = QLabel(self)
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
        hbox.addWidget(self.img_label)

        grid.addLayout(hbox, 0, 0, 1, 2)

        # self.setLayout(grid)

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

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)

        zoom_in_tool = self.addToolBar('Zoom in')
        zoom_in_tool.addAction(zoom_in_action)

        zoom_out_tool = self.addToolBar('Zoom out')
        zoom_out_tool.addAction(zoom_out_action)

        show_action_tool = self.addToolBar('Show action sequence')
        show_action_tool.addAction(show_action_seq)

        self.resize(550, 550)
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
