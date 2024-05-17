import numpy as np
import cv2


def standart(image=None):
    image2 = image.copy()
    image2[image2 < 0.0] = 0.0
    image2[image2 > 255.0] = 255.0
    image2 = image2.astype(np.uint8)

    return image2


def DFT(img):

    dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude_spectrum = np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))

    cv2.normalize(magnitude_spectrum, magnitude_spectrum, 0, 1, cv2.NORM_MINMAX)
    return magnitude_spectrum, dft_shift


def iDFT(fshift):

    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    cv2.normalize(img_back, img_back, 0, 1, cv2.NORM_MINMAX)
    return img_back


def gauss_high_freq_mask(img, d_0):
    n, m = img.shape
    d = np.fromfunction(lambda i, j, k: euclid_norm(i-n/2, j-m/2), (n, m, 2), dtype=np.float32)
    h = 1 - np.exp(-(d/d_0)**2)
    return h


def ideal_high_freq_mask(img, d_0):
    n, m = img.shape
    d = np.fromfunction(lambda i, j, k:  euclid_norm(i-n/2, j-m/2), (n, m, 2))
    d = (d > d_0).astype(int)
    return d


def homomorf_mask(img, d_0, gamma_l, gamma_h):
    gauss_h = gauss_high_freq_mask(img, d_0)
    h = (gamma_h - gamma_l) * gauss_h + gamma_l
    return h


def euclid_norm(x, y):
    return (x**2 + y**2)**0.5
