'''
Helper methods
'''

import os

from datetime import datetime
import time

import pyautogui
from win32com.client import Dispatch
import win32gui

def decorator_start_end(name):
    'outer decorator, argument should be name for script'
    def inner_decorator(func):
        'inner'
        def wrapper(*args, **kwargs):
            'wrapper'
            print_with_time(f'{name} 스크립트 시작')
            func(*args, **kwargs)
            print_with_time(f'{name} 스크립트 종료')
        return wrapper
    return inner_decorator

def get_file_path(filename, sub=None):
    'return full file path'
    if sub:
        return os.path.join(os.getcwd(), sub, filename)
    return os.path.join(os.getcwd(), filename)

def get_last_match(image):
    'For checking distinct elements. Nothing found if (0,0,0,0) returned'
    positions = [(0,0,0,0)]
    threshhold = 8

    all_locations = list(pyautogui.locateAllOnScreen(image, confidence=0.7))
    for idx, pos in enumerate(all_locations):
        if idx == len(all_locations) - 1:
            break
        if abs(all_locations[idx][0] - positions[-1][0]) +\
            abs(all_locations[idx][1] - positions[-1][1]) > threshhold:
            positions.append(pos)

    return positions[-1]

def get_datetime(raw_time_set):
    'return datetime object for given hour and minute'
    if raw_time_set[1] >= 0:
        time_set = datetime.now().replace(
            hour = raw_time_set[0],
            minute = raw_time_set[1],
            second = 0)
    else:
        time_set = datetime.now().replace(
            hour = raw_time_set[0] - 1,
            minute = raw_time_set[1] + 60,
            second = 0)
    return time_set

def print_with_time(*args):
    'print with time in %H:%M:%S format'
    now = datetime.strftime(datetime.now(), '%H:%M:%S')
    print(now, *args)

def send_alt_key_and_set_foreground(hwnd):
    '''
    send alt key to shell before setting foreground with win32gui to workaround
    error: (0, 'SetForegroundWindow', 'No error message is available')
    '''
    Dispatch('WScript.Shell').SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)

def print_all_windows(title='Zoom'):
    'wrapper'
    def win_enum_handler(hwnd, items):
        '''print hwnds and respective class names with 'Zoom' in title'''
        full_title = win32gui.GetWindowText(hwnd)
        if title in full_title:
            items.append(str(hwnd).ljust(10) + win32gui.GetClassName(hwnd).ljust(30) + full_title)

    items = []
    win32gui.EnumWindows(win_enum_handler, items)

    for i in items:
        print(i)

def bring_chrome_to_front(driver):
    'bring Selenium Chrome browser to front with a hack'
    driver.minimize_window()
    time.sleep(1)
    driver.maximize_window()
    time.sleep(0.5)

def decorator_get_name(func):
    'decorator for getting method name'
    def wrapper(*args, **kwargs):
        'wrapper'
        args = args[:-1] + (func.__name__,)
        func(*args, **kwargs)
    return wrapper
