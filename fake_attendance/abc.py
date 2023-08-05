'''
abstraction because why not
'''

from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

import win32con
import win32gui

from fake_attendance.arg_parse import parsed_args
from fake_attendance.helper import print_with_time
from fake_attendance.settings import VERBOSITY__INFO

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

    def check_window(self, window_class=None, window_title=None):
        'check and return window'
        hwnd = win32gui.FindWindow(window_class, window_title)
        is_window = win32gui.IsWindowVisible(hwnd)

        return bool(is_window), hwnd

    def maximize_window(self, hwnd):
        'maximize window'
        # force normal size from possible out-of-size maximized window
        win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)
        # maximize window
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

        return list(win32gui.GetWindowRect(hwnd))
