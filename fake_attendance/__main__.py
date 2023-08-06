'''
main file
'''

from fake_attendance.download_ext import DownloadExtensionSource
from fake_attendance.scheduler import MyScheduler

if __name__ == '__main__':
    # pylint: disable=duplicate-code
    # quick hack to fix error in pyautogui
    import pyscreeze
    import PIL

    __PIL_TUPLE_VERSION = tuple(int(x) for x in PIL.__version__.split("."))
    pyscreeze.PIL__version__ = __PIL_TUPLE_VERSION
    # end
    # pylint: enable=duplicate-code

    scheduler = MyScheduler()
    download = DownloadExtensionSource(scheduler)

    download.run()
    scheduler.run()
