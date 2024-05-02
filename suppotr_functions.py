import numpy as np
import cv2


def standart(image=None):
    image2 = image.copy()
    image2[image2 < 0.0] = 0.0
    image2[image2 > 255.0] = 255.0
    image2 = image2.astype(np.uint8)

    return image2
