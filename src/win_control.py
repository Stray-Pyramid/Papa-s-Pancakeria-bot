import pyautogui
import time, math

from .datatypes.rect import *
from .constants.constants import *

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
            
def mousePos(cord, duration=0):
    pyautogui.moveTo(cord[0] + Coor.X_PAD, cord[1] + Coor.Y_PAD, duration, _pause = False)
    
def leftClick():
    pyautogui.leftClick()

def leftDown(delay = 0.1):
    pyautogui.mouseDown(button="left", _pause = False)
    time.sleep(delay)

def leftUp(delay = 0.1):
    pyautogui.mouseUp(button='left', _pause = False)
    time.sleep(delay)

def clickPos(cord, interval=0.1):
    pyautogui.leftClick(cord[0] + Coor.X_PAD, cord[1] + Coor.Y_PAD, interval=interval)
    
def calculate_distances(path):
    distances = []

    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        distances.append(distance)

    return distances
    
def move_cursor_along_path(path, speed, offset=(0,0)):
    distances = calculate_distances(path)

    for i in range(len(path) - 1):
        distance = distances[i]
        move_time = distance / speed
        #print(f"Moving to X:{offset[0] + path[i][0]}, Y:{offset[1] + path[i][1]}, Distance: {distance}, Move time: {move_time}")
        mousePos((offset[0] + path[i][0], offset[1] + path[i][1]))
        time.sleep(move_time)

    # Move the cursor to the last point after completion
    mousePos((offset[0] + path[-1][0], offset[1] + path[-1][1]))