import numpy as np
import cv2


def shape(img):
    return img.shape[:2]


def mean_brightness(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

