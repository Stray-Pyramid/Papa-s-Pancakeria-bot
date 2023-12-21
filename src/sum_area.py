# Python 3.8.2
# Last updated 09/11/2020 (MM/DD/YYYY)
# By StrayPyramid

from PIL import ImageOps, ImageGrab
import numpy as np

from .constants.constants import Coor
from .datatypes.rect import Rect


def grab_area(rect):
    rect = Rect(rect)
    rect.translate(Coor.X_PAD, Coor.Y_PAD)

    im = ImageGrab.grab((rect.left(), rect.top(), rect.right(), rect.bottom()))
    return im


def sum_area(rect) -> int:
    # rect: Xpos, YPos, Width, Height
    im = ImageOps.grayscale(grab_area(rect))
    a = np.array(im.getcolors())
    a = a.sum()
    return a


def save_area(rect):
    im = grab_area(rect)
    area_sum = sum_area(rect)
    im.save("./"+str(area_sum)+".png", 'PNG')
