'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

import os
import sys

from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger

import keyboard

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.fake_check_in import FakeCheckIn
from fake_attendance.helper import print_with_time
from fake_attendance.launch_zoom import LaunchZoom
from fake_attendance.quit_zoom import QuitZoom
from fake_attendance.settings import (
    CHECK_IN_TIMES,
    ZOOM_ON_HOUR,
    ZOOM_QUIT_HOUR)
# pylint: enable=wrong-import-position

class MyScheduler:
    'A class that manages the scheduler'

    def __init__(self, time_sets=CHECK_IN_TIMES):
        '''
        initialize
        time_sets = [{'hour': int, 'minute': int},...]
        '''
        self.sched = BackgroundScheduler()
        self.fake_check_in = FakeCheckIn()
        self.launch_zoom = LaunchZoom()
        self.quit_zoom = QuitZoom()
        self.check_in_trigger = OrTrigger([
            CronTrigger(hour=TIME_SET['hour'], minute=TIME_SET['minute'])\
            for TIME_SET in time_sets
        ])

    def shutdown(self, event):
        'testing interrupt'
        if self.sched.running and event:
            self.sched.shutdown(wait=False)

    def add_jobs(self):
        '''
        add 1. grab zoom link on screen
            2. launch Zoom
            3. print next trigger time for next QR check
        '''
        self.sched.add_job(self.fake_check_in.run, self.check_in_trigger, id='fake_check_in')
        self.sched.add_job(self.launch_zoom.run, 'cron',\
                           hour=ZOOM_ON_HOUR, id='lauch_zoom')
        self.sched.add_job(self.quit_zoom.run, 'cron',\
                           hour=ZOOM_QUIT_HOUR, id='quit_zoom')
        self.sched.add_listener(
            callback = lambda event: self.print_next_time(),
            mask = EVENT_JOB_EXECUTED)

    def print_next_time(self):
        'print next trigger for next QR check'
        next_time = self.sched.get_job('fake_check_in').next_run_time
        print_with_time('다음 출석 스크립트 실행 시각:', next_time.strftime(('%H:%M')))

    def run(self):
        'run scheduler'
        print_with_time('스케줄러 실행')
        self.add_jobs()
        self.sched.start()
        try:
            keyboard.wait('ctrl+c')
        except KeyboardInterrupt:
            print_with_time('키보드로 중단 요청')
        self.sched.shutdown()


if __name__ == '__main__':
    MyScheduler().run()
