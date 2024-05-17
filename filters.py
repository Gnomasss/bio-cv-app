import cv2
import numpy as np
from scipy import ndimage
import suppotr_functions as sup


def gaussian_blur(img=None, kernel_size=3):
    kernel_size = int(kernel_size)

    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def gamma_correction(img=None, gamma=2.5):
    c = 255
    matrix = np.array([np.uint8(np.clip(c * ((i / 255.0) ** gamma), 0, 255)) for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(img, matrix)


def gray(img=None):

    if len(img.shape) >= 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        return img


def resize(img=None, width=None, height=None):
    if height is None:
        height = img.shape[0]
    if width is None:
        width = img.shape[1]
    width, height = int(width), int(height)
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)


def exact_crop(img=None, x=0, y=0, width=None, height=None):
    if height is None:
        height = img.shape[0]
    if width is None:
        width = img.shape[1]
    x, y, width, height = int(x), int(y), int(width), int(height)
    return img[y:y + height, x:x + width]


def rotate_img(img=None, angle=90):

    return ndimage.rotate(img, angle)


def sob(img=None):
    blur = cv2.GaussianBlur(img, (3, 3), 0)
    sobel_X = lambda image: np.uint8(np.abs(cv2.Sobel(image, cv2.CV_64F, 1, 0)))
    sobel_Y = lambda image: np.uint8(np.abs(cv2.Sobel(image, cv2.CV_64F, 0, 1)))

    sob = cv2.bitwise_or(sobel_X(blur), sobel_Y(blur))

    return sob


def laplasiian(img=None):
    new_img = cv2.GaussianBlur(img, (3, 3), 0)

    #new_img1 = standart(np.int64(img) - 3 * cv2.Laplacian(new_img, cv2.CV_64F))
    #new_img2 = standart(np.int64(new_img) - 1 * cv2.Laplacian(new_img, cv2.CV_64F))
    #new_img3 = standart(np.int64(img) - 1 * cv2.Laplacian(img, cv2.CV_64F))
    new_img4 = sup.standart(np.int64(new_img) - 1 * cv2.Laplacian(img, cv2.CV_64F))
    return sup.standart(np.int64(cv2.Laplacian(img, cv2.CV_64F)))
    #return cv.convertScaleAbs(cv2.Laplacian(img, cv2.CV_64F))


def equalization_hist(img=None):
    return cv2.equalizeHist(img)


def linear_hist_transform(img=None, k=1, b=0):
    matrix = np.array([np.uint8(np.clip(k * i + b, 0, 255)) for i in np.arange(0, 256)]).astype(
        "uint8")
    return cv2.LUT(img, matrix)


def piecewise_linear_3_transform(img=None, x1=0.5, y1=0.5, x2=0.5, y2=0.5):
    matrix = np.zeros((256, 1), dtype=np.uint8)
    for i in range(256):
        if i < x1 * 255:
            matrix[i] = i * (y1 / x1)
        elif i < x2 * 255:
            matrix[i] = (i - 255 * x1) * (y2 - y1) / (x2 - x1) + y1 * 255
        else:
            matrix[i] = (i - 255) * (y2 - 1) * (x2 - 1) + 255

        if matrix[i] < 0:
            matrix[i] = 0
        if matrix[i] > 255:
            matrix[i] = 255

    return cv2.LUT(img, matrix)


def DFT(img=None):

    dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude_spectrum = np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))

    cv2.normalize(magnitude_spectrum, magnitude_spectrum, 0, 255, cv2.NORM_MINMAX)
    magnitude_spectrum = magnitude_spectrum.astype(np.uint8)
    return magnitude_spectrum


def homomorf_filtering(img=None, d_0=80, gamma_l=0.25, gamma_h=2):
    ln_img = np.log(img)

    _, dft_shift = sup.DFT(ln_img)

    mask = sup.homomorf_mask(img, d_0, gamma_l, gamma_h)
    fshift = dft_shift * mask

    idft_img = sup.iDFT(fshift)

    new_img = np.exp(idft_img)
    cv2.normalize(new_img, new_img, 0, 255, cv2.NORM_MINMAX)
    new_img = new_img.astype(np.uint8)
    return new_img


def gauss_high_freq_filter(img=None, d_0=80):
    _, dft_shift = sup.DFT(img)
    mask = sup.gauss_high_freq_mask(img, d_0)
    fshift = dft_shift * mask

    idft_img = sup.iDFT(fshift)

    cv2.normalize(idft_img, idft_img, 0, 255, cv2.NORM_MINMAX)
    idft_img = idft_img.astype(np.uint8)
    return idft_img


def ideal_high_freq_filter(img=None, d_0=80):
    _, dft_shift = sup.DFT(img)
    mask = sup.ideal_high_freq_mask(img, d_0)
    fshift = dft_shift * mask

    idft_img = sup.iDFT(fshift)

    cv2.normalize(idft_img, idft_img, 0, 255, cv2.NORM_MINMAX)
    idft_img = idft_img.astype(np.uint8)
    return idft_img


if __name__ == '__main__':
    pass

