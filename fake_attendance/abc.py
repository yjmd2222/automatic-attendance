'''
abstraction because why not
'''

from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import win32con
import win32gui

# pylint: disable=wrong-import-position
from fake_attendance.helper import decorator_start_end
# pylint: enable=wrong-import-position

# pylint: disable=too-few-public-methods
class BaseClass(ABC):
    'base class for abstraction'

    # pylint: disable=no-member
    @abstractmethod
    def __init__(self):
        'initialize'
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

    def __init__(self):
        'initialize'
        super().__init__()
        self.driver = None

    @abstractmethod
    def create_selenium_options(self):
        'declare options for Selenium driver.'

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
