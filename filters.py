import cv2
import numpy as np
from scipy import ndimage


def blur(descr_flag=False, img=None, kernel_size=3):
    description = "Блюр"
    if descr_flag:
        return description

    kernel_size = int(kernel_size)

    return cv2.blur(img, (kernel_size, kernel_size))


def gamma_correction(descr_flag=False, img=None, gamma=2.5):
    description = "Гамма преобразование"
    if descr_flag:
        return description

    c = 255
    matrix = np.array([np.uint8(np.clip(c * ((i / 255.0) ** gamma), 0, 255)) for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(img, matrix)


def gray(descr_flag=False, img=None):
    description = "Перевод изображения в градации серого"
    if descr_flag:
        return description
    if len(img.shape) >= 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        return img


def resize(descr_flag=False, img=None, width=None, height=None):
    description = "Изменеие размеров изображения"
    if descr_flag:
        return description
    if height is None:
        height = img.shape[0]
    if width is None:
        width = img.shape[1]
    width, height = int(width), int(height)
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)


def exact_crop(descr_flag=False, img=None, x=0, y=0, width=None, height=None):
    description = "Точное вырезание участка изображения"
    if descr_flag:
        return description
    if height is None:
        height = img.shape[0]
    if width is None:
        width = img.shape[1]
    x, y, width, height = int(x), int(y), int(width), int(height)
    return img[y:y + height, x:x + width]


def rotate_img(descr_flag=False, img=None, angle=90):
    description = "Повернуть изображение на определенный угол в градусах"
    if descr_flag:
        return description

    return ndimage.rotate(img, angle)


def sob(descr_flag=False, img=None):
    description = None
    if descr_flag:
        return description

    blur = cv2.GaussianBlur(img, (3, 3), 0)
    sobel_X = lambda image: np.uint8(np.abs(cv2.Sobel(image, cv2.CV_64F, 1, 0)))
    sobel_Y = lambda image: np.uint8(np.abs(cv2.Sobel(image, cv2.CV_64F, 0, 1)))

    sob = cv2.bitwise_or(sobel_X(blur), sobel_Y(blur))

    return sob


def standart(descr_flag=False, image=None):
    description = "Вспомогательная функция"
    if descr_flag:
        return description

    image2 = image.copy()
    image2[image2 < 0.0] = 0.0
    image2[image2 > 255.0] = 255.0
    image2 = image2.astype(np.uint8)

    return image2


def laplasiian(descr_flag=False, img=None):
    description = None
    if descr_flag:
        return description

    new_img = cv2.GaussianBlur(img, (3, 3), 0)

    #new_img1 = standart(np.int64(img) - 3 * cv2.Laplacian(new_img, cv2.CV_64F))
    #new_img2 = standart(np.int64(new_img) - 1 * cv2.Laplacian(new_img, cv2.CV_64F))
    #new_img3 = standart(np.int64(img) - 1 * cv2.Laplacian(img, cv2.CV_64F))
    new_img4 = standart(False, np.int64(new_img) - 1 * cv2.Laplacian(img, cv2.CV_64F))
    return new_img4


if __name__ == '__main__':
    pass

