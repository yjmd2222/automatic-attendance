'''
abstraction because why not
'''

from sys import platform

import time

from abc import ABC, abstractmethod

import traceback

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchWindowException,
    TimeoutException,
    WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from auto_attendance.arg_parse import parsed_args
from auto_attendance.helper import print_with_time
from auto_attendance.settings import VERBOSITY__INFO
if platform == 'darwin':
    from auto_attendance.helper import (
        get_screen_resolution,
        execute_applescript)
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
                print_with_time(f'기타: {type(error).__name__} exception 발생')
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
            except TimeoutException as error:
                print_with_time('로딩 너무 오래 걸림')
                # raise error to exit current script
                raise SystemExit from error
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
                print_with_time(f'기타: {type(error).__name__} exception 발생')
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
        auto_driver = Service(ChromeDriverManager().install())
        options = self.create_selenium_options()
        driver = webdriver.Chrome(service=auto_driver, options=options)
        driver.set_page_load_timeout(10)

        return driver

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

    def _set_foreground_win32(self, hwnd):
        '''
        set window to foreground on win32
        send alt key to shell before setting foreground with win32gui to workaround
        error: (0, 'SetForegroundWindow', 'No error message is available')
        '''
        Dispatch('WScript.Shell').SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)

    def _set_foreground_darwin(self, window_name, app_name):
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
        execute_applescript(applescript_code, False)

    @decorator_window_handling_exception
    def set_foreground(self, identifier:int|str, app_name):
        '''
        set window to foreground\n
        identifier is hwnd on win32\n
        and window_name on darwin\n
        app_name is unused on win32
        '''
        if platform == 'win32':
            self._set_foreground_win32(identifier)
        else:
            self._set_foreground_darwin(identifier, app_name)

    def _get_all_windows_win32(self, window_name)->list:
        '''
        get all window names matching window_name in format below\n
        [hwnd window_class window_name, hwnd]
        '''
        def win_enum_handler(hwnd, items):
            '''print hwnds and respective class names with 'identifier' in name'''
            full_title = win32gui.GetWindowText(hwnd)
            if window_name in full_title:
                items.append(
                    [str(hwnd).ljust(10) + win32gui.GetClassName(hwnd).ljust(30) + full_title,
                     hwnd])
        items = []
        win32gui.EnumWindows(win_enum_handler, items)
        return items

    def print_all_windows(self, name='Zoom', is_print=False):
        '''
        wrapper for printing hwnds and respective class names with Zoom in title\n
        currently debugging only on win32
        '''
        if platform == 'win32':
            items = self._get_all_windows_win32(name)
            if is_print:
                for item in items:
                    # [hwnd window_class window_name, hwnd]
                    print(item)

    def _check_window_win32(self, window_name, with_class):
        'check and return window on win32'
        # check with class
        if with_class:
            hwnd = win32gui.FindWindow(window_name, None)
            is_window = bool(win32gui.IsWindowVisible(hwnd))
        # check with title
        else:
            items = self._get_all_windows_win32(window_name)
            if items:
                is_window = True
                hwnd = int(items[0][-1])
            else:
                is_window = False
                hwnd = 0

        return is_window, hwnd

    def _check_window_darwin(self, window_name, app_name):
        'check and return window on darwin'
        applescript_code = f'''
        tell application "System Events"
            if exists application process "{app_name}" then
                tell application process "{app_name}"
                    if exists (window 1 whose title is "{window_name}") then
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

        result = execute_applescript(applescript_code, True)
        is_window = bool(int(result.stdout.strip()))

        return is_window, window_name

    @decorator_window_handling_exception
    def check_window(self, window_name, app_name, with_class=True):
        '''
        check window presence\n
        returns is_window, hwnd on win32\n
        and returns is_window, window_name on darwin\n
        app_name is unused on win32\n\n
        win32 API's ClassName is used if with_class == True\n
        and WindowName is used otherwise\n\n
        currently only works with Zoom conference window for Zoom\n
        because Zoom does not properly support AppleScript
        '''
        if platform == 'win32':
            is_window, identifier = self._check_window_win32(window_name, with_class)
        else:
            is_window, identifier = self._check_window_darwin(window_name, app_name)
        return is_window, identifier

    def _maximize_window_win32(self, hwnd):
        '''
        maximize window on win32
        '''
        # force normal size from possible out-of-size maximized window
        win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)
        # maximize window
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

        rect = list(win32gui.GetWindowRect(hwnd))

        return rect

    def _maximize_window_darwin(self, window_name, app_name):
        '''
        maximize window on darwin
        '''
        pos_x, pos_y = get_screen_resolution()
        applescript_code = f'''
        tell application "System Events"
            tell application process "{app_name}"
                tell (window 1 whose title is "{window_name}")
                    set position to (0, 0)
                    set size to {pos_x, pos_y}
                    set rect to position & size
                end tell
                set frontmost to true
                return rect
            end tell
        end tell
        '''

        result = execute_applescript(applescript_code, True)
        rect = result.stdout.strip().split(', ')
        rect = [int(num) for num in rect]

        return rect

    @decorator_window_handling_exception
    def maximize_window(self, identifier:int|str, app_name):
        '''
        maximize window and returns rect\n
        identifier is hwnd on win32\n
        and window_name on darwin\n
        app_name is unused on win32
        '''
        if platform == 'win32':
            rect =  self._maximize_window_win32(identifier)
        else:
            rect  = self._maximize_window_darwin(identifier, app_name)
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
