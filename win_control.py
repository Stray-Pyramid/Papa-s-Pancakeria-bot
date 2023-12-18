import pyautogui
import time

from rect import *
from constants import *

def pressKey(key: str) -> None:
    pyautogui.press(keys=key, interval=0.05)

def holdKey(key: str) -> None:
    pyautogui.keyDown(key)
    time.sleep(.05)
    
def releaseKey(key: str) -> None:
    pyautogui.keyUp(key)
    time.sleep(.05)
    
def writeString(string):
    pyautogui.typewrite(string, interval=0.1)
            
def mousePos(cord):
    pyautogui.moveTo(cord[0] + Coor.X_PAD, cord[1] + Coor.Y_PAD)
    
def leftClick():
    pyautogui.leftClick()

def leftDown():
    pyautogui.mouseDown(button="left")
    time.sleep(.1)

def leftUp(delay = 0.1):
    pyautogui.mouseUp(button='left')
    time.sleep(delay)

def clickPos(cord, delay=0):
    pyautogui.leftClick(cord[0] + Coor.X_PAD, cord[1] + Coor.Y_PAD, duration=delay)