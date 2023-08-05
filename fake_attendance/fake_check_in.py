'''
Script to automatically send link information in QR image on a Zoom meeting every five minutes
'''

import os
import sys

from sys import platform

from datetime import datetime, timedelta
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if platform == 'win32':
    import win32gui
else:
    import subprocess

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.abc import UseSelenium
from fake_attendance.info import KAKAO_ID, KAKAO_PASSWORD
from fake_attendance.helper import print_with_time, set_foreground
from fake_attendance.settings import (
    ZOOM_APPLICATION_NAME,
    ZOOM_CLASSROOM_NAME,
    SCREEN_QR_READER_BLANK,
    SCREEN_QR_READER_POPUP_LINK,
    SCREEN_QR_READER_SOURCE,
    LOGIN_WITH_KAKAO_BUTTON,
    ID_INPUT_BOX,
    PASSWORD_INPUT_BOX,
    LOGIN_BUTTON,
    IFRAME,
    AGREE,
    CHECK_IN,
    SUBMIT)
from fake_attendance.notify import PrepareSendEmail
# pylint: enable=wrong-import-position

# pylint: disable=too-many-instance-attributes
class FakeCheckIn(PrepareSendEmail, UseSelenium):
    'A class for checking QR image and sending email with link'
    print_name = 'QR 체크인'

    def __init__(self, sched_drop_runs_until=None):
        'initialize'
        self.sched_drop_runs_until = sched_drop_runs_until
        self.is_window = False
        self.hwnd = 0
        self.rect = [100,100,100,100]
        self.extension_source = SCREEN_QR_READER_SOURCE
        self.is_wait = False
        PrepareSendEmail.define_attributes(self)
        PrepareSendEmail.decorate_run(self)
        UseSelenium.__init__(self)

    def reset_attributes(self):
        'reset attributes for next run'
        self.is_window, self.hwnd = self.check_window()
        self.rect = self.maximize_window(self.hwnd) if self.is_window else [100,100,100,100]
        self.driver = None
        self.is_wait = False
        PrepareSendEmail.define_attributes(self)

    def resize_window_win32(self, rect, hwnd):
        'resize window to given rect on win32'
        win32gui.MoveWindow(hwnd, *rect, True)

    def resize_window_darwin(self, rect, app_name, window_name):
        'resize window to given rect on darwin'
        applescript_code = f'''
        tell application "System Events"
            tell application process "{app_name}"
                set zoom_conference to window 1 whose title is "{window_name}"
                tell zoom_conference
                    set position to {rect[:2]}
                    set size to {rect[2:]}
                    set rect to position & size
                end tell
            end tell
        end tell
        '''
        with open(os.devnull, 'wb') as devnull:
            subprocess.run(['osascript', '-e', applescript_code],
                            stdout=devnull,
                            check=True)

    def resize_window(self, rect):
        'resize window to given rect'
        if platform == 'win32':
            self.resize_window_win32(rect, self.hwnd)
        else:
            self.resize_window_darwin(rect, ZOOM_APPLICATION_NAME, ZOOM_CLASSROOM_NAME)

    # def check_window(self):
    #     'check and return window'
    #     if platform == 'win32':
    #         hwnd = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, None)
    #     else:
    #         ZOOM_APPLICATION_NAME = 'zoom.us'
    #         ZOOM_CLASSROOM_NAME = 'Zoom 회의'
    #         applescript_code = f'''
    #         tell application "{ZOOM_APPLICATION_NAME}"
    #             set target_title to "{ZOOM_CLASSROOM_NAME}"
    #             set window_list to every window
    #             repeat with a_window in window_list
    #                 set window_title to name of a_window
    #                 if window_title is equal to target_title then
    #                     set window_id to id of a_window
    #                     return window_id
    #                 end if
    #             end repeat
    #         end tell
    #         '''

    #         result = subprocess.run(['osascript', '-e', applescript_code],
    #                                 capture_output=True,
    #                                 text=True,
    #                                 check=True)
    #         hwnd = result.stdout.strip()

    #     return bool(hwnd), hwnd

    def check_link_loop(self):
        'Get link from QR'
        # maximize Chrome window
        self.driver.maximize_window()
        time.sleep(1)

        # calculate new window size
        ratios = [i/10 for i in range(3, 11)]
        rect_resized = self.rect.copy()
        result = None
        # only horizontally
        for ratio in ratios:
            rect_resized[2] = int(self.rect[2] * ratio)
            result = self.check_link(rect_resized)
            if result:
                break
        # both horizontally and vertically
        if not result:
            for ratio in ratios:
                rect_resized[2] = int(self.rect[2] * ratio)
                rect_resized[3] = int(self.rect[3] * ratio)
                result = self.check_link(rect_resized)
                if result:
                    break

        return result

    def check_link(self, rect_resized):
        'method to actually fire Screen QR Reader inside loop'
        # apply new window size
        self.resize_window(rect_resized)
        # bring it to foreground so that Screen QR Reader recognizes the first 'Zoom' match
        set_foreground(self.hwnd, ZOOM_APPLICATION_NAME, ZOOM_CLASSROOM_NAME)

        self.driver.get(SCREEN_QR_READER_POPUP_LINK) # Screen QR Reader
        time.sleep(2)

        # Selenium will automatically open the link in a new tab
        # if there is a QR image, so check tab count.
        window_handles = self.driver.window_handles

        # Screen QR Reader may open 'about:blank' when there is not a valid QR image.
        if len(window_handles) > 1: # if there are two tabs
            self.driver.switch_to.window(window_handles[-1]) # force Selenium to be on the new tab
            # check if the url is fake then return False
            if self.driver.current_url in (SCREEN_QR_READER_BLANK, SCREEN_QR_READER_POPUP_LINK):
                return False
            return True # return True if url is valid
        return False

    def create_selenium_options(self):
        'declare options for Selenium driver'
        options = UseSelenium.create_selenium_options(self)
        # Screen QR Reader source required
        options.add_extension(self.extension_source)
        # automatically select Zoom meeting
        options.add_argument('--auto-select-desktop-capture-source=Zoom')

        return options

    # pylint: disable=too-many-branches
    def selenium_action(self, is_continue, by_which, sleep, **kwargs):
        '''
        selenium action method\n
        Must specify kwargs\n
        'how' must be one of 'click', 'input', 'get_iframe', and 'submit'\n
        'element' is the element to be inspected\n
        'input_text' must be given if 'how' is 'input'
        '''
        # run if is_continue
        if not is_continue:
            return False
        # check three times
        for i in range(1, 3+1):
            try:
                # check if match pattern in src for iframes
                if kwargs['how'] == 'get_iframe':
                    is_valid_iframe = None
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((by_which, kwargs['element'])))
                    iframe_urls = [element.get_attribute('src') for element
                                   in self.driver.find_elements(by_which, kwargs['element'])]
                    for iframe_url in iframe_urls:
                        if iframe_url and 'codestates.typeform' in iframe_url:
                            is_valid_iframe = True
                            self.driver.get(iframe_url)
                            break
                    if not is_valid_iframe:
                        raise NoSuchElementException
                else:
                    element = self.driver.find_element(by_which, kwargs['element'])
                    if kwargs['how'] == 'click':
                        element.click()
                    elif kwargs['how'] == 'input':
                        element.send_keys(kwargs['input_text'])
                    elif kwargs['how'] == 'submit':
                        self.driver.execute_script('arguments[0].click();', element)
                    else:
                        assert kwargs['how'] in ['click', 'input', 'get_iframe', 'submit']
                print_with_time(f'{kwargs["element"]} 찾기 성공. {sleep}초 후 다음 단계로 진행')
                time.sleep(sleep)
                return True
            except NoSuchElementException:
                search_fail_message = f'{kwargs["element"]} 찾기 실패'
                if i == 3:
                    print_with_time(search_fail_message)
                    break
                print_with_time(f'{search_fail_message}. {sleep}초 후 재시도')
                time.sleep(sleep)
            except KeyError as error:
                print_with_time(f'kwarg의 키워드 알맞게 입력했는지 확인 필요. 조회 실패: {error}')
                break
            except AssertionError:
                print_with_time(f'how kwarg의 인자값 알맞게 입력했는지 확인 필요. 입력: {kwargs["how"]}')
                break

        print_with_time('출석 체크 실패. 현 상태에서 이메일 발송')
        return False
    # pylint: enable=too-many-branches

    def check_in(self):
        'do the check-in'
        # wait 10 seconds
        time.sleep(10)

        # bool flag
        is_continue = True

        # login type
        is_continue = self.selenium_action(is_continue, By.CLASS_NAME, 10,\
                        how='click', element=LOGIN_WITH_KAKAO_BUTTON)

        # insert Kakao id
        is_continue = self.selenium_action(is_continue, By.ID, 1,\
                        how='input', element=ID_INPUT_BOX, input_text=KAKAO_ID)

        # insert Kakao password
        is_continue = self.selenium_action(is_continue, By.ID, 1,\
                        how='input', element=PASSWORD_INPUT_BOX, input_text=KAKAO_PASSWORD)

        # log in
        is_continue = self.selenium_action(is_continue, By.CLASS_NAME, 10,\
                        how='click', element=LOGIN_BUTTON)

        # Should have successfully logged in. Now pass set link to pass to Notify
        self.result_dict['link']['content'] = self.driver.current_url if is_continue else '발견 실패'

        # get inner document link
        is_continue = self.selenium_action(is_continue, By.TAG_NAME, 10,\
                        how='get_iframe', element=IFRAME)

        # agree to check in
        is_continue = self.selenium_action(is_continue, By.XPATH, 3,\
                        how='click', element=AGREE)

        # select check-in
        is_continue = self.selenium_action(is_continue, By.XPATH, 3,\
                        how='click', element=CHECK_IN)

        # submit
        is_continue = self.selenium_action(is_continue, By.XPATH, 3,\
                        how='submit', element=SUBMIT)

        return is_continue

    # pylint: disable=attribute-defined-outside-init
    def run(self):
        'run whole check-in process'
        # get Zoom window
        self.is_window, self.hwnd = self.check_window()
        # if it is visible
        if self.is_window:
            # get max rect
            self.rect = self.maximize_window(self.hwnd)
            # init selenium
            self.driver = self.initialize_selenium()
        # if not
        else:
            # quit
            print_with_time('줌 실행중인지 확인 필요')
            self.reset_attributes()
            return

        # check QR code in Zoom
        is_qr = self.check_link_loop()
        # if there's no QR code
        if not is_qr:
            print_with_time('QR 코드 없음. 현 세션 완료')
            self.driver.quit()
            return

        # otherwise check in
        print_with_time('QR 코드 확인. 출석 체크 진행')
        check_in_result = self.check_in()

        # update result
        if check_in_result:
            self.result_dict['result']['content'] = '성공'
            self.is_wait = True
        else:
            self.result_dict['result']['content'] = '실패'
            self.is_wait = False

        # quit Selenium
        self.driver.quit()

        # make sure same job does not run within 30 minutes upon completion
        if self.is_wait:
            until = datetime.now() + timedelta(minutes=30)
            if self.sched_drop_runs_until:
                self.sched_drop_runs_until(self.print_name, until)
            print_with_time(f'출석 확인. {datetime.strftime(until, "%H:%M")}까지 출석 체크 실행 안 함')
            # checker bool to send email
            self.is_send = True
        return
    # pylint: enable=attribute-defined-outside-init
# pylint: enable=too-many-instance-attributes

if __name__ == '__main__':
    FakeCheckIn().run()
