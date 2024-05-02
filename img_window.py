import sys

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication, QFileDialog, QMainWindow, QAction, \
    QVBoxLayout, QPushButton, QGridLayout, QLineEdit, QTextEdit, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QCursor
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QEvent, QObject, QPoint, QTimer, Qt
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
        self.mouse_pos = None

        self.tmp_rect_points = None
        self.rect = None

        self.rect_border = False
        self.rect_transform_border = None
        #self.rect_transform = False

        self.setWidgetResizable(True)
        self.img_label = QLabel(self)
        
        self.img_info = QLabel(self)
        self.img_info.setStyleSheet("background-color: rgba(224, 224, 224, 90);")
        self.img_info.setFont(QFont('Arial', 16))

        # self.img_label.setScaledContents(True)
        self.setWidget(self.img_label)
        self.img_pixmap = None

        self.setMouseTracking(True)

        self.mouse_tracker = MouseTracker(self.img_label)
        self.mouse_tracker.buttonPressed.connect(self.mouse_press)
        self.mouse_tracker.buttonReleased.connect(self.mouse_release)
        self.mouse_tracker.positionChanged.connect(self.mouse_move)

    def set_img(self, img):
        self.img = img
        self.update_img(self.img)

    def update_img(self, img):
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)

        self.img_pixmap = QPixmap.fromImage(img)
        self.img_label.setPixmap(self.img_pixmap)

    def convert_mouse_pos(self, pos):
        if self.img is not None:
            img_shift = (self.img_label.size().height() - self.img.shape[0]) // 2
            pos[1] -= img_shift
        return pos

    @pyqtSlot(QPoint)
    def mouse_press(self, pos):
        self.mouse_pos = self.convert_mouse_pos([pos.x(), pos.y()])
        self.draw_rectangle(1)
        self.remake_rect(1)

    @pyqtSlot(QPoint)
    def mouse_move(self, pos):
        self.mouse_pos = self.convert_mouse_pos([pos.x(), pos.y()])
        if self.img is not None and all((0 <= self.mouse_pos[i] < self.img.shape[1-i]) for i in range(2)):
            if len(self.img.shape) == 3:
                pixel_color = dict(zip(['B', 'G', 'R'], self.img[self.mouse_pos[1], self.mouse_pos[0], :]))
            elif len(self.img.shape) == 2:
                pixel_color = {"B": self.img[self.mouse_pos[1], self.mouse_pos[0]]}
            else:
                pixel_color = ""
            self.img_info.setText(f"{dict(zip(['X', 'Y'], self.mouse_pos))}\n"
                                  f"{pixel_color}")
        self.img_info.adjustSize()
        self.draw_rectangle(2)
        self.set_cursor()
        self.remake_rect(2)

    @pyqtSlot(QPoint)
    def mouse_release(self, pos):
        self.mouse_pos = self.convert_mouse_pos([pos.x(), pos.y()])
        self.draw_rectangle(3)
        self.remake_rect(3)
        #self.parent.crop_image() #подумать над этим

    def draw_rectangle(self, stage):
        if not self.rect_border and self.rect_transform_border is None:
            if stage == 1:
                if 0 <= self.mouse_pos[0] < self.img.shape[1] and 0 <= self.mouse_pos[1] < self.img.shape[0]:
                    self.tmp_rect_points = [self.mouse_pos]
            elif stage == 2:
                if self.tmp_rect_points is not None:
                    if len(self.tmp_rect_points) == 1:
                        self.tmp_rect_points.append(self.mouse_pos)
                    else:
                        self.tmp_rect_points[-1] = self.mouse_pos
                    self.draw_rectangle_by_points(self.tmp_rect_points)
            else:
                if len(self.tmp_rect_points) > 1:
                    self.tmp_rect_points[-1] = self.mouse_pos
                    self.rect = np.array(self.tmp_rect_points)
                    self.rect = np.sort(self.rect, axis=0)
                    self.draw_rectangle_by_points(self.tmp_rect_points)
                self.tmp_rect_points = None

    def draw_rectangle_by_points(self, points):
        img_copy = self.img.copy()
        cv2.rectangle(img_copy, points[0], points[1], (255, 255, 255), 2)
        self.update_img(img_copy)

    def set_cursor(self):
        if self.rect is not None:
            x, y = self.mouse_pos
            rect_x = self.rect[:, 0]
            rect_y = self.rect[:, 1]
            #print(mouse_pos, self.rect, rect_x)

            if abs(rect_x[0] - x) < 10 and abs(rect_y[0] - y) < 10:
                self.setCursor(Qt.ClosedHandCursor)
                self.rect_border = True

            elif abs(rect_x[1] - x) < 10 and abs(rect_y[1] - y) < 10:
                self.setCursor(Qt.SizeAllCursor)
                self.rect_border = True

            elif min(abs(rect_x - x)) < 8 and rect_y[0] <= y <= rect_y[1]:
                self.setCursor(Qt.SizeHorCursor)
                self.rect_border = True

            elif min(abs(rect_y - y)) < 8 and rect_x[0] <= x <= rect_x[1]:
                self.setCursor(Qt.SizeVerCursor)
                self.rect_border = True

            else:
                self.setCursor(Qt.ArrowCursor)
                self.rect_border = False
        else:
            self.setCursor(Qt.ArrowCursor)
            self.rect_border = False

    def remake_rect(self, stage):
        if self.rect_border or self.rect_transform_border is not None:
            if stage == 1:
                x, y = self.mouse_pos
                rect_x = self.rect[:, 0]
                rect_y = self.rect[:, 1]

                if abs(rect_x[0] - x) < 13 and abs(rect_y[0] - y) < 13:
                    self.rect_transform_border = (-1, -1)
                elif abs(rect_x[1] - x) < 13 and abs(rect_y[1] - y) < 13:
                    self.rect_transform_border = (-2, -2)
                elif abs(rect_x[0] - x) < 10:
                    self.rect_transform_border = (0, 0)
                elif abs(rect_y[0] - y) < 10:
                    self.rect_transform_border = (0, 1)
                elif abs(rect_x[1] - x) < 10:
                    self.rect_transform_border = (1, 0)
                elif abs(rect_y[1] - y) < 10:
                    self.rect_transform_border = (1, 1)

            elif stage == 2 and self.rect_transform_border is not None:
                if self.rect_transform_border == (-1, -1):
                    self.rect[1] = self.rect[1] + self.mouse_pos - self.rect[0]
                    self.rect[0] = self.mouse_pos
                elif self.rect_transform_border == (-2, -2):
                    self.rect[1] = self.mouse_pos
                else:
                    self.rect[self.rect_transform_border] = self.mouse_pos[self.rect_transform_border[1]]
                self.draw_rectangle_by_points(self.rect)

            elif stage == 3:
                self.rect = np.sort(self.rect, axis=0)
                self.rect_border = False
                self.rect_transform_border = None













if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageWindow()
    img = cv2.imread("akira.jpeg")
    ex.set_img(img)
    ex.show()
    sys.exit(app.exec_())

