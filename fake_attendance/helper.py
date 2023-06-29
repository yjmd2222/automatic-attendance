'''
Helper methods
'''

import os

from datetime import datetime, timedelta

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

def get_time_sets(hour, minute, diff_minute=5):
    'return time sets diff_min and 2*diff_min minutes before and after given time'
    input_time = datetime.now().replace(hour=hour, minute=minute)
    time_list = [input_time + timedelta(minutes=diff_minute*i) for i in range(-2, 3)]
    return [{'hour': time_set.hour, 'minute': time_set.minute} for time_set in time_list]

def extrapolate_time_sets(time_sets_outer):
    'return unfoiled time sets'
    return [time_set for time_sets in time_sets_outer for time_set in time_sets]

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
