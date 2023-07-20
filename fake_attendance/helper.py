'''
Helper methods
'''

import os

from datetime import datetime, timedelta
import time

import pyautogui
from win32com.client import Dispatch
import win32gui

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

def convert_to_datetime(time_, format_='%H:%M'):
    'convert given time to datetime.datetime for today\'s date'
    time_ = datetime.strptime(time_, format_)
    time_ = datetime.now().replace(
        hour = time_.hour,
        minute = time_.minute,
        second = 0)
    return time_

def extrapolate_time_sets(time_:str|datetime, diff_minute=5, extend_num=2, format_='%H:%M'):
    '''
    return time sets diff_min and 2*diff_min minutes before and after given time\n
    converts 'time_' to datetime.datetime if type str
    '''
    if isinstance(time_, str):
        time_ = convert_to_datetime(time_, format_)
    return [time_ + timedelta(minutes=diff_minute*i) for i in range(-extend_num, extend_num+1)]

def unfoil_time_sets(time_sets_outer):
    'return unfoiled time sets'
    return [time_set for time_sets in time_sets_outer for time_set in time_sets]

def print_with_time(*args, **kwargs):
    '''
    uses built-in print function with time in %H:%M:%S format in start of message\n
    arguments for 'print()' can be specified in **kwargs fashion
    '''
    now = datetime.strftime(datetime.now(), '%H:%M:%S')
    print(now, *args, **kwargs)

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

def print_sequence(sequence):
    'return which sequence was pressed as message'
    print_with_time(f'강제 {sequence} 커맨드 입력 확인')
