import time
import math
import pyautogui

from .constants.constants import Coor


def press_key(key: str) -> None:
    pyautogui.press(keys=key, interval=0.05)


def hold_key(key: str) -> None:
    pyautogui.keyDown(key)
    time.sleep(.05)


def release_key(key: str) -> None:
    pyautogui.keyUp(key)
    time.sleep(.05)


def write_string(string):
    pyautogui.typewrite(string, interval=0.1)


def mouse_pos(cord, duration=0, delay=0.1):
    pyautogui.moveTo(cord[0] + Coor.X_PAD, cord[1] +
                     Coor.Y_PAD, duration, _pause=False)
    time.sleep(delay)


def left_click():
    pyautogui.leftClick()


def left_down(delay=0.1):
    pyautogui.mouseDown(button="left", _pause=False)
    time.sleep(delay)


def left_up(delay=0.1):
    pyautogui.mouseUp(button='left', _pause=False)
    time.sleep(delay)


def click_pos(cord, interval=0.1):
    pyautogui.leftClick(cord[0] + Coor.X_PAD, cord[1] +
                        Coor.Y_PAD, interval=interval, _pause=False)


def calculate_distances(path):
    distances = []

    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        distances.append(distance)

    return distances


def move_cursor_along_path(path, speed, offset=(0, 0)):
    distances = calculate_distances(path)

    for i in range(len(path) - 1):
        distance = distances[i]
        move_time = distance / speed
        # print(f"Moving to X:{offset[0] + path[i][0]}, Y:{offset[1] + path[i][1]}, Distance: {distance}, Move time: {move_time}")
        mouse_pos((offset[0] + path[i][0], offset[1] + path[i][1]), delay=0)
        time.sleep(move_time)

    # Move the cursor to the last point after completion
    mouse_pos((offset[0] + path[-1][0], offset[1] + path[-1][1]), delay=0)
