from PyQt5.QtWidgets import (QWidget, QLabel, QMainWindow, QSizePolicy,
                             QPushButton, QGridLayout, QLineEdit, QTextEdit, QScrollArea)
from PyQt5.QtGui import QFont, QImage, QPixmap, QPalette
import cv2
import func2action

FONT_SIZE = 16


class FilterArgWindow(QMainWindow):
    def __init__(self, method, parent=None):
        super(FilterArgWindow, self).__init__(parent)
        self.parent = parent
        self.method = method
        self.centralWidget = QWidget(self)
        self.edits = None
        self.initGui()

    def initGui(self):
        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.setFont(font)

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
        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.setFont(font)

        self.setCentralWidget(self.textEdit)
        self.textEdit.setPlainText("")

        for name, args in self.seq:
            self.textEdit.append(f"{name}\n")
            for arg in args:
                self.textEdit.append(f"{arg}: {args[arg]} ")
            self.textEdit.append('\n')

        self.resize(500, 500)
        self.setWindowTitle("Seq of arguments")


class InfoMessageWindow(QMainWindow):

    def __init__(self, version, github_url):
        super().__init__()
        self.version = version
        self.github_url = github_url
        self.textEdit = QTextEdit()
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.setFont(font)

        self.setCentralWidget(self.textEdit)
        self.textEdit.setPlainText("")

        self.textEdit.append(f"Version: {self.version}\n")
        self.textEdit.append(f"GitHub: {self.github_url}")

        self.resize(500, 200)
        self.setWindowTitle("Information")


class ImgInfoWindow(QMainWindow):

    def __init__(self, img):
        super().__init__()
        self.img = img

        self.specs = func2action.all_spec()

        self.textEdit = QTextEdit()
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.setFont(font)

        self.setCentralWidget(self.textEdit)
        self.textEdit.setPlainText("")

        for spec in self.specs:
            self.textEdit.append(f"{spec.name}: {spec.func(self.img)}\n")

        self.resize(500, 200)
        self.setWindowTitle("Image information")


class ImgsSeqInfoWindow(QMainWindow):

    def __init__(self, imgs_list, img_index):
        super().__init__()

        self.imgs_list = imgs_list
        self.index = img_index

        self.textEdit = QTextEdit()
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.setFont(font)

        self.setCentralWidget(self.textEdit)
        self.textEdit.setPlainText("")

        self.textEdit.append(f"Seq len: {len(self.imgs_list)}\n")
        self.textEdit.append(f"Current index: {self.index}\n")

        self.resize(500, 200)
        self.setWindowTitle("Image information")


'''class ErrorMessageWindow(QMainWindow):

    def __init__(self, message):
        super().__init__()
        self.message = message

        self.textEdit = QTextEdit()
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.setFont(font)

        self.setCentralWidget(self.textEdit)
        self.textEdit.setPlainText("")

        self.textEdit.append(self.message)

        self.resize(500, 200)
        self.setWindowTitle("Error")'''


class TestImageWindow(QMainWindow):

    def __init__(self, img):
        super().__init__()
        self.img = img
        self.img_pixmap = None

        self.img_label = QLabel()
        self.scrollArea = QScrollArea()

        self.scrollArea.setWidget(self.img_label)
        self.scrollArea.setWidgetResizable(True)

        self.setCentralWidget(self.scrollArea)

        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(FONT_SIZE)
        self.setFont(font)

        self.set_img()
        self.setWindowTitle("Test Image")

    def set_img(self):
        frame = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        self.img_pixmap = QPixmap.fromImage(img)
        self.img_label.setPixmap(self.img_pixmap)
