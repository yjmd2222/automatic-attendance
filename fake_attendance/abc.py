'''
abstraction because why not
'''

from sys import platform

from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

if platform == 'win32':
    import win32con
    import win32gui
elif platform == 'darwin':
    import subprocess

# pylint: disable=wrong-import-position
from fake_attendance.arg_parse import parsed_args
from fake_attendance.helper import print_with_time
if platform == 'win32':
    from fake_attendance.settings import ZOOM_CLASSROOM_CLASS
elif platform == 'darwin':
    from fake_attendance.helper import get_screen_resolution
    from fake_attendance.settings import (
        ZOOM_APPLICATION_NAME,
        ZOOM_CLASSROOM_NAME)
from fake_attendance.settings import VERBOSITY__INFO
# pylint: enable=wrong-import-position

class BaseClass(ABC):
    'base class for abstraction'

    @abstractmethod
    def __init__(self):
        'BaseClass.__init__() that decorates self.run() to print start and end of it'
        # to be used with super().__init__() in subclass
        self.run = self.decorator_start_end(self.run)

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

class UseSelenium(BaseClass):
    'base class for subclasses that use Selenium'

    @abstractmethod
    def __init__(self):
        '''
        UseSelenium.__init__() that defines an empty Selenium self.driver\n
        and self.verbosity attributes.\n
        Also inherits from BaseClass.__init__() that decorates self.run to print start and\n
        end of it
        '''
        super().__init__()
        self.driver = None
        self.verbosity = parsed_args.verbosity

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

    def check_window_win32(self, window_class_name):
        'check and return window on win32'
        hwnd = win32gui.FindWindow(window_class_name, None)
        is_window = bool(win32gui.IsWindowVisible(hwnd))

        return is_window, hwnd

    def check_window_darwin(self, app_name, window_name):
        'check window and return True on darwin'
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

        result = subprocess.run(['osascript', '-e', applescript_code], capture_output=True, text=True, check=True)
        is_window = bool(int(result.stdout.strip()))

        return is_window, None

    def check_window(self):
        '''
        check Zoom conference window presence\n
        returns is_window, hwnd on win32\n
        and returns is_window, None on darwin
        '''
        if platform == 'win32':
            is_window, hwnd = self.check_window_win32(ZOOM_CLASSROOM_CLASS)
        elif platform == 'darwin':
            is_window, hwnd = self.check_window_darwin(ZOOM_APPLICATION_NAME, ZOOM_CLASSROOM_NAME)
        return is_window, hwnd

    def maximize_window_win32(self, hwnd):
        '''
        maximize window on win32
        '''
        # force normal size from possible out-of-size maximized window
        win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)
        # maximize window
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

        rect = list(win32gui.GetWindowRect(hwnd))

        return rect

    def maximize_window_darwin(self, app_name, window_name):
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

        result = subprocess.run(['osascript', '-e', applescript_code],
                                capture_output=True,
                                text=True,
                                check=True)
        rect = result.stdout.strip().split(', ')
        rect = [int(num) for num in rect]

        return rect
    
    def maximize_window(self, hwnd:int|None):
        '''
        maximize window and returns rect\n
        hwnd is just a placeholder on darwin
        '''
        if platform == 'win32':
            return self.maximize_window_win32(hwnd)
        elif platform == 'darwin':
            return self.maximize_window_darwin(ZOOM_APPLICATION_NAME, ZOOM_CLASSROOM_NAME)

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
