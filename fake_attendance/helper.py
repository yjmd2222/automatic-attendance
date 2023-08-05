'''
Helper methods
'''

import os

from sys import platform

from datetime import datetime, timedelta
import time

import pyautogui
if platform == 'win32':
    from win32com.client import Dispatch
    import win32gui
else:
    import subprocess

def get_file_path(filename, sub=None):
    'return full file path'
    if sub:
        return os.path.join(os.getcwd(), sub, filename)
    return os.path.join(os.getcwd(), filename)

def get_last_match(image):
    'For checking distinct elements. Nothing found if (0,0,0,0) returned'
    dimensions = [(0,0,0,0)]
    threshhold = 8

    all_locations = list(pyautogui.locateAllOnScreen(image, confidence=0.7))
    for idx, dim in enumerate(all_locations):
        if abs(all_locations[idx][0] - dimensions[-1][0]) +\
            abs(all_locations[idx][1] - dimensions[-1][1]) > threshhold:
            dimensions.append(dim)
    positions = [(dimension[0]+dimension[2]/2, dimension[1]+dimension[3]/2)
                 for dimension in dimensions]

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

def bring_chrome_to_front(driver):
    'bring Selenium Chrome browser to front with a hack'
    driver.minimize_window()
    time.sleep(1)
    driver.maximize_window()
    time.sleep(0.5)

def send_alt_key_and_set_foreground(hwnd):
    '''
    send alt key to shell before setting foreground with win32gui to workaround
    error: (0, 'SetForegroundWindow', 'No error message is available')
    '''
    Dispatch('WScript.Shell').SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)

def set_foreground_darwin(app_name, window_name):
    'set window to foreground on darwin'
    applescript_code = f'''
    tell application "System Events"
        tell application process "{app_name}"
            set frontmost to true
            set window_to_foreground to window 1 whose title is "{window_name}"
            tell window_to_foreground
                perform action "AXRaise" of window_to_foreground
            end tell
        end tell
    end tell
    '''
    with open(os.devnull, 'wb') as devnull:
        subprocess.run(['osascript', '-e', applescript_code],
                        stdout=devnull,
                        check=True)

def set_foreground(hwnd=None, app_name=None, window_name=None):
    '''
    set window to foreground\n
    hwnd is used on win32 and others on darwin
    '''
    if platform == 'win32':
        send_alt_key_and_set_foreground(hwnd)
    else:
        set_foreground_darwin(app_name, window_name)

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

def get_screen_resolution():
    'get screen resolution'
    pos_x, pos_y = pyautogui.size()
    return pos_x, pos_y

def check_appearance():
    """
    Checks DARK/LIGHT mode of macOS\n
    if DARK: True, elif LIGHT: False
    """
    cmd = 'defaults read -g AppleInterfaceStyle'
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    return bool(popen.communicate()[0])
