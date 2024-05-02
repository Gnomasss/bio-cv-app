import cv2
import numpy as np


def input(img=None):
    return img


def output(img=None):
    return img


def split(img=None):
    return [img.copy(), img.copy()]


def bitwise_and(imgs=None):
    return cv2.bitwise_and(imgs[0], imgs[1])


def bitwise_or(imgs=None):
    return cv2.bitwise_or(imgs[0], imgs[1])


def bitwise_xor(imgs=None):
    return cv2.bitwise_xor(imgs[0], imgs[1])


def bitwise_not(img=None):
    return cv2.bitwise_not(img)
