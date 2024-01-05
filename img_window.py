import sys

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication, QFileDialog, QMainWindow, QAction, \
    QVBoxLayout, QPushButton, QGridLayout, QLineEdit, QTextEdit, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QEvent, QObject, QPoint, QTimer
import numpy as np
import cv2


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


class ImageWindow(QScrollArea):

    def __init__(self, parent=None):
        QScrollArea.__init__(self, parent=parent)

        self.parent = parent

        self.img = None

        self.points = None
        self.draw = False

        self.setWidgetResizable(True)
        self.img_label = QLabel(self)
        # self.img_label.setScaledContents(True)
        self.setWidget(self.img_label)
        self.img_pixmap = None

        self.setMouseTracking(True)

        self.mouse_tracker = MouseTracker(self.img_label)
        self.mouse_tracker.buttonPressed.connect(self.mouse_press)
        self.mouse_tracker.buttonReleased.connect(self.mouse_release)
        self.mouse_tracker.positionChanged.connect(self.mouse_move)

    def set_img(self, img):
        if not self.draw:
            self.img = img
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)

        self.img_pixmap = QPixmap.fromImage(img)
        self.img_label.setPixmap(self.img_pixmap)

    def convert_mouse_pos(self, pos):
        if self.img is not None:
            img_shift = (self.img_label.size().height() - self.img.shape[0]) // 2
            pos[1] -= img_shift
        return pos

    def draw_mode_on(self):
        self.draw = True

    def draw_mode_off(self):
        self.draw = False
        self.points = None

    @pyqtSlot(QPoint)
    def mouse_press(self, pos):
        mouse_pos = self.convert_mouse_pos([pos.x(), pos.y()])
        self.points = [mouse_pos]

    @pyqtSlot(QPoint)
    def mouse_move(self, pos):
        mouse_pos = self.convert_mouse_pos([pos.x(), pos.y()])
        if self.draw and self.points is not None:
            if len(self.points) == 1:
                self.points.append(mouse_pos)
            else:
                self.points[-1] = mouse_pos
            img_copy = self.img.copy()
            cv2.rectangle(img_copy, self.points[0], self.points[1], (255, 255, 255), 3)
            self.set_img(img_copy)

    @pyqtSlot(QPoint)
    def mouse_release(self, pos):
        mouse_pos = self.convert_mouse_pos([pos.x(), pos.y()])
        self.points[-1] = mouse_pos
        self.parent.crop_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageWindow()
    img = cv2.imread("akira.jpeg")
    ex.set_img(img)
    ex.show()
    sys.exit(app.exec_())

