'''
abstraction because why not
'''

import os

from sys import platform

import time

from abc import ABC, abstractmethod

import traceback

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchWindowException,
    WebDriverException)
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

from auto_attendance.arg_parse import parsed_args
from auto_attendance.helper import print_with_time
from auto_attendance.settings import (
    VERBOSITY__INFO,
    ZOOM_APPLICATION_NAME)
if platform == 'darwin':
    from auto_attendance.helper import get_screen_resolution

    import subprocess
else:
    from win32com.client import Dispatch
    import win32con
    import win32gui
    # pylint: disable=no-name-in-module
    from pywintypes import error as pywintypes_error
    # pylint: enable=no-name-in-module

class BaseClass(ABC):
    'base class for abstraction'

    @abstractmethod
    def __init__(self):
        '''
        BaseClass.__init__() that decorates self.run()\n
        to print start and end of it and to catch any errors that happen during runtime
        '''
        # to be used with super().__init__() in subclass
        self.run = self.decorator_start_end(self.run)
        self.run = self.decorator_system_exit(self.run)

    # pylint: disable=method-hidden
    @abstractmethod
    def run(self):
        'run everything'
    # pylint: enable=method-hidden

    # pylint: disable=no-member
    def decorator_start_end(self, func):
        'decorator for printing start and end of script'
        def wrapper(*args, **kwargs):
            'wrapper'
            print_with_time(f'{self.print_name} 스크립트 시작')
            func(*args, **kwargs)
            print_with_time(f'{self.print_name} 스크립트 종료')
        return wrapper
    # pylint: enable=no-member

    def decorator_system_exit(self, func):
        'decorator for catching SystemExit'
        def wrapper(*args, **kwargs):
            'wrapper'
            # pylint: disable=broad-exception-caught
            try:
                return func(*args, **kwargs)
            except SystemExit:
                print_with_time('현재 실행중인 스크립트 종료')
            except Exception as error:
                print_with_time(f'기타: {error.__module__} 모듈의 {type(error).__name__} exception 발생')
                traceback.print_exc()
            # pylint: enable=broad-exception-caught
            return None
        return wrapper

class UseSelenium(BaseClass):
    'base class for subclasses that use Selenium'

    @abstractmethod
    def __init__(self):
        '''
        UseSelenium.__init__() that defines an empty Selenium self.driver\n
        and self.verbosity attributes.\n
        Decorates self.run() to catch NoSuchWindowException and WebDriverException in Selenium\n
        Also inherits from BaseClass.__init__() that decorates self.run()\n
        to print start and end of it and to catch any errors that happen during runtime
        '''
        super().__init__()
        self.driver = None
        self.verbosity = parsed_args.verbosity

    def decorator_selenium_exception(self, func):
        'decorator for catching selenium\'s NoSuchWindowException'
        def wrapper(*args, **kwargs):
            'wrapper'
            try:
                func(*args, **kwargs)
            except (NoSuchWindowException, WebDriverException) as error:
                print_with_time('크롬 창 수동 종료 확인')
                # raise error to exit current script
                raise SystemExit from error
        return wrapper

    def decorator_system_exit(self, func):
        'decorator for catching SystemExit'
        def wrapper(*args, **kwargs):
            'wrapper'
            # pylint: disable=broad-exception-caught
            try:
                # wrap self.run() with self.decorator_selenium_exception() first
                return self.decorator_selenium_exception(func)(*args, **kwargs)
            except SystemExit:
                print_with_time('현재 실행중인 스크립트 종료')
                if self.driver:
                    self.driver.quit()
            except Exception as error:
                print_with_time(f'기타: {error.__module__} 모듈의 {type(error).__name__} exception 발생')
                traceback.print_exc()
                if self.driver:
                    self.driver.quit()
            # pylint: enable=broad-exception-caught
            return None
        return wrapper

    def create_selenium_options(self):
        '''
        declare options for Selenium driver\n
        adds an option to disable logging if -v 3 optional arg is given\n
        or return None
        '''
        options = Options()
        if self.verbosity is not None and self.verbosity == VERBOSITY__INFO:
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return options

    def initialize_selenium(self):
        'initialize Selenium and return driver'
        # auto_driver = Service(ChromeDriverManager().install())
        options = self.create_selenium_options()

        # return webdriver.Chrome(service=auto_driver, options=options)
        return webdriver.Chrome(options=options)

    def bring_chrome_to_front(self):
        'bring Selenium Chrome browser to front with a hack'
        self.driver.minimize_window()
        time.sleep(1)
        self.driver.maximize_window()
        time.sleep(0.5)

class ManipulateWindow:
    'base class for checking visibility of and manipulating windows'

    @staticmethod
    def _choose_error():
        'method for choosing error depending on OS'
        if platform == 'win32':
            error = pywintypes_error
        else:
            error = Exception
        return error

    @staticmethod
    def decorator_window_handling_exception(func):
        '''
        decorator for catching exception in window handling\n
        currently no errors found for darwin
        '''
        def wrapper(*args, **kwargs):
            'wrapper'
            error = ManipulateWindow._choose_error()
            for i in range(3+1):
                # pylint: disable=broad-exception-caught
                try:
                    return func(*args, **kwargs)
                except error as err:
                    print_with_time(f'{err.__module__} 모듈의 {type(err).__name__} exception 발생')
                    traceback.print_exc()
                    # message
                    handle_fail_message = '창을 조정할 수 없음'
                    # break after three tries
                    if i == 3:
                        print_with_time(handle_fail_message)
                        break
                    sleep = 5
                    print_with_time(f'{handle_fail_message}. {sleep}초 후 재시도')
                    time.sleep(sleep)
                # pylint: enable=broad-exception-caught
            # raise error after three tries
            raise SystemExit
        return wrapper

    def _set_foreground_win32(self, window_identifier):
        '''
        set window to foreground on win32
        send alt key to shell before setting foreground with win32gui to workaround
        error: (0, 'SetForegroundWindow', 'No error message is available')
        '''
        Dispatch('WScript.Shell').SendKeys('%')
        win32gui.SetForegroundWindow(window_identifier)

    def _set_foreground_darwin(self, window_identifier):
        'set window to foreground on darwin'
        window_title, app_name = window_identifier
        applescript_code = f'''
        tell application "System Events"
            tell application process "{app_name}"
                set frontmost to true
                set window_to_foreground to window 1 whose title is "{window_title}"
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

    @decorator_window_handling_exception
    def set_foreground(self, window_identifier:int|str):
        '''
        set window to foreground\n
        hwnd is window id on win32 and window title on darwin
        '''
        if platform == 'win32':
            self._set_foreground_win32(window_identifier)
        else:
            self._set_foreground_darwin(window_identifier)

    def print_all_windows(self, title='Zoom', is_print=False):
        '''
        wrapper for printing hwnds and respective class names with Zoom in title\n
        currently debugging only on win32
        '''
        if platform == 'win32':
            def win_enum_handler(hwnd, items):
                '''print hwnds and respective class names with 'Zoom' in title'''
                full_title = win32gui.GetWindowText(hwnd)
                if title in full_title:
                    items.append(
                        str(hwnd).ljust(10) + win32gui.GetClassName(hwnd).ljust(30) + full_title)

            items = []
            win32gui.EnumWindows(win_enum_handler, items)

            if is_print:
                for i in items:
                    print(i)

            if len(items):
                to_return = True, int(items[0].split()[0])
            else:
                to_return = False, 0
        else:
            to_return = False, 0
        return to_return

    def _check_window_win32(self, window_name, with_class):
        'check and return window on win32'
        # check with class
        if with_class:
            hwnd = win32gui.FindWindow(window_name, None)
            is_window = bool(win32gui.IsWindowVisible(hwnd))
        # check with title
        else:
            def win_enum_handler(hwnd, items):
                '''print hwnds and respective class names with 'window_identifier' in title'''
                full_title = win32gui.GetWindowText(hwnd)
                if window_name in full_title:
                    items.append(
                        [str(hwnd).ljust(10) + win32gui.GetClassName(hwnd).ljust(30) + full_title, hwnd])
            items = []
            win32gui.EnumWindows(win_enum_handler, items)
            if len(items):
                is_window = True
                hwnd = int(items[-1])
            else:
                is_window = False
                hwnd = 0

        return is_window, hwnd

    def _check_window_darwin(self, window_name):
        'check and return window on darwin'
        window_title, app_title = window_name
        applescript_code = f'''
        tell application "System Events"
            if exists application process "{app_title}" then
                tell application process "{app_title}"
                    if exists (window 1 whose title is "{window_title}") then
                        return 1
                    else
                        return 0
                    end if
                end tell
            else
                return 0
            end if
        end tell
        '''

        result = subprocess.run(['osascript', '-e', applescript_code],
                                capture_output=True,
                                text=True,
                                check=True)
        is_window = bool(int(result.stdout.strip()))

        return is_window, window_title

    @decorator_window_handling_exception
    def check_window(self, window_name, with_class=True):
        '''
        check window presence\n
        returns is_window, hwnd on win32\n
        and returns is_window, window_title on darwin.\n
        currently only works with Zoom conference window\n
        because Zoom does not properly support AppleScript
        '''
        if platform == 'win32':
            is_window, hwnd = self._check_window_win32(window_name, with_class)
        else:
            is_window, hwnd = self._check_window_darwin(window_name)
        return is_window, hwnd

    def _maximize_window_win32(self, window_identifier):
        '''
        maximize window on win32
        '''
        # force normal size from possible out-of-size maximized window
        win32gui.ShowWindow(window_identifier, win32con.SW_NORMAL)
        # maximize window
        win32gui.ShowWindow(window_identifier, win32con.SW_MAXIMIZE)

        rect = list(win32gui.GetWindowRect(window_identifier))

        return rect

    def _maximize_window_darwin(self, window_identifier):
        '''
        maximize window on darwin
        '''
        window_title, app_title = window_identifier
        pos_x, pos_y = get_screen_resolution()
        applescript_code = f'''
        tell application "System Events"
            tell application process "{app_title}"
                tell (window 1 whose title is "{window_title}")
                    set position to (0, 0)
                    set size to {pos_x, pos_y}
                    set rect to position & size
                end tell
                set frontmost to true
                return rect
            end tell
        end tell
        '''

        result = subprocess.run(['osascript', '-e', applescript_code],
                                capture_output=True,
                                text=True,
                                check=True)
        rect = result.stdout.strip().split(', ')
        rect = [int(num) for num in rect]

        return rect

    @decorator_window_handling_exception
    def maximize_window(self, window_identifier:int|str):
        '''
        maximize window and returns rect\n
        hwnd is window_title on darwin
        '''
        if platform == 'win32':
            rect =  self._maximize_window_win32(window_identifier)
        else:
            rect  = self._maximize_window_darwin(window_identifier)
        return rect

    # def maximize_window_darwin(self, hwnd, app_name=None):
    #     'maximize window on Darwin'
    #     applescript_code = f'''
    #     use framework "AppKit"
    #     use framework "Foundation"
    #     use scripting additions

    #     tell application "{app_name}"
    #         set currentWindow to window id {hwnd}
    #         set bounds of currentWindow to my getDisplayBounds()
    #         activate
    #     end tell

    #     on getDisplayBounds()
    #         set theScreen to current application's NSScreen's mainScreen()
    #         set ((aF, bF), (cF, dF)) to theScreen's frame()
    #         set ((aV, bV), (cV, dV)) to theScreen's visibleFrame()
    #         return (aV as integer, (dF - bV - dV) as integer, \
    #             (aV + cV) as integer, (dF - bV) as integer)
    #     end getDisplayBounds
    #     '''

    #     result = subprocess.run(['osascript', '-e', applescript_code])
    #     rect = result.stdout.strip()

    #     return rect
