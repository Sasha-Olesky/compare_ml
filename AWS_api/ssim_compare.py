
from PIL import Image
from ssim import SSIM
from ssim.utils import get_gaussian_kernel

gaussian_kernel_sigma = 1.5
gaussian_kernel_width = 11
gaussian_kernel_1d = get_gaussian_kernel(gaussian_kernel_width, gaussian_kernel_sigma)
size = (256, 256)

def get_ssim(strImg):
    ssim = Image.open(strImg)
    ssim = ssim.resize(size, Image.ANTIALIAS)
    return ssim

def compare_ssim(im1, im2):
    similar = SSIM(im1).cw_ssim_value(im2) * 100
    if similar > 90:
        return 'Same Image'
    else:
        return 'Different Image'

def ssim_compare(img1, img2):
    im1 = Image.open(img1)
    im1 = im1.resize(size, Image.ANTIALIAS)

    im2 = Image.open(img2)
    im2 = im2.resize(size, Image.ANTIALIAS)

    similar = SSIM(im1).cw_ssim_value(im2) * 100
    if similar > 90:
        return ('Same Image', similar)
    else:
        return ('Different Image', similar)
