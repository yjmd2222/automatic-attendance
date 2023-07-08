'''
abstraction because why not
'''

from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import win32con
import win32gui

# pylint: disable=wrong-import-position
from fake_attendance.arg_parse import args
from fake_attendance.helper import decorator_start_end
from fake_attendance.settings import VERBOSITY__INFO
# pylint: enable=wrong-import-position

# pylint: disable=too-few-public-methods
class BaseClass(ABC):
    'base class for abstraction'

    # pylint: disable=no-member
    @abstractmethod
    def __init__(self):
        'BaseClass.__init__(self) method that decorates self.run to print start and end of it'
        # to be used with super().__init__() in subclass
        self.run = decorator_start_end(self.print_name)(self.run)
    # pylint: enable=no-member

    # pylint: disable=method-hidden
    @abstractmethod
    def run(self):
        'run everything'
    # pylint: enable=method-hidden
# pylint: enable=too-few-public-methods

class UseSelenium(BaseClass):
    'base class for subclasses that use Selenium'

    @abstractmethod
    def __init__(self):
        '''
        UseSelenium.__init__(self) method that defines an empty Selenium self.driver attribute.\n
        Also inherits from BaseClass.__init__() method that decorates self.run to print start and\n
        end of it
        '''
        super().__init__()
        self.driver = None

    @abstractmethod
    def create_selenium_options(self):
        'declare options for Selenium driver.'
        options = Options()
        if args.verbosity is not None and args.verbosity == VERBOSITY__INFO:
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return options

    def initialize_selenium(self, options=None):
        'initialize Selenium and return driver'
        auto_driver = Service(ChromeDriverManager().install())

        return webdriver.Chrome(service=auto_driver, options=options)

    def maximize_window(self, hwnd):
        'maximize window'
        # force normal size from possible out-of-size maximized window
        win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)
        # maximize window
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

        return list(win32gui.GetWindowRect(hwnd))
