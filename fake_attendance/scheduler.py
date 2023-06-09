'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

import os
import sys

from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.fake_check_in import FakeCheckIn
from fake_attendance.launch_zoom import LaunchZoom
from fake_attendance.settings import (
    CHECK_IN_TIMES,
    ZOOM_ON_HOUR,
    ZOOM_ON_MINUTE)
# pylint: enable=wrong-import-position

class MyScheduler:
    'A class that manages the scheduler'

    def __init__(self):
        'initialize'
        self.sched = BlockingScheduler(standalone=True)
        self.fake_check_in = FakeCheckIn()
        self.launch_zoom = LaunchZoom()
        self.check_in_trigger = OrTrigger([
            CronTrigger(hour=TIME_SET['hour'], minute=TIME_SET['minute'])\
            for TIME_SET in CHECK_IN_TIMES
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
        self.sched.add_job(self.fake_check_in.run, self.check_in_trigger)
        self.sched.add_job(self.launch_zoom.run, 'cron',\
                           hour=ZOOM_ON_HOUR, minute=ZOOM_ON_MINUTE)
        self.sched.add_listener(
            callback = lambda event: self.print_next_time(),
            mask = EVENT_JOB_EXECUTED)

    def print_next_time(self):
        'print next trigger for next QR check'
        next_time = self.sched.get_jobs()[0].next_run_time
        print('다음 출석 스크립트 실행 시각:', next_time.strftime(('%H:%M')))

    def run(self):
        'run scheduler'
        self.add_jobs()
        try:
            self.sched.start()
        except KeyboardInterrupt:
            print('interrupt')

if __name__ == '__main__':
    MyScheduler().run()
