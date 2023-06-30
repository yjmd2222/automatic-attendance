'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

import os
import sys

from datetime import datetime

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
    ARGUMENT_MAP,
    ZOOM_ON_HOURS,
    ZOOM_QUIT_HOURS,
    ZOOM_QUIT_MINUTE)
# pylint: enable=wrong-import-position

class MyScheduler:
    'A class that manages the scheduler'

    def __init__(self):
        '''
        initialize
        time_sets = [{'hour': int, 'minute': int},...]
        '''
        self.sched = BackgroundScheduler()
        self.fake_check_in = FakeCheckIn()
        self.launch_zoom = LaunchZoom()
        self.quit_zoom = QuitZoom()
        self.time_sets = self.get_timesets()
        self.check_in_trigger = OrTrigger([
            CronTrigger(hour=TIME_SET['hour'], minute=TIME_SET['minute'])\
            for TIME_SET in self.time_sets
        ])

    def add_jobs(self):
        '''
        add 1. grab zoom link on screen
            2. launch Zoom
            3. print next trigger time for next QR check
        '''
        self.sched.add_job(self.fake_check_in.run, self.check_in_trigger, id='fake_check_in')
        self.sched.add_job(self.launch_zoom.run, 'cron',\
                           hour=ZOOM_ON_HOURS, id='lauch_zoom')
        self.sched.add_job(self.quit_zoom.run, 'cron',\
                           hour=ZOOM_QUIT_HOURS, minute=ZOOM_QUIT_MINUTE, id='quit_zoom')
        self.sched.add_listener(
            callback = lambda event: self.print_next_time(),
            mask = EVENT_JOB_EXECUTED)

    def print_next_time(self):
        'print next trigger for next QR check'
        next_time = self.sched.get_job('fake_check_in').next_run_time
        print_with_time('다음 출석 스크립트 실행 시각:', next_time.strftime(('%H:%M')))

    def get_timesets(self):
        'receive argument from command line for which time sets to add to schedule'
        time_sets = None
        # check argument passed
        if len(sys.argv) > 1:
            # argument as text file
            if '.txt' in sys.argv[1]:
                filename = sys.argv[1]
                with open (filename, 'r', encoding='utf-8') as file:
                    time_sets = [line.strip() for line in file[1:]]
                    time_sets = [datetime.strptime(i, '%H:%M') for i in time_sets]
                    time_sets = [{'hour': i.hour, 'minute': i.minute} for i in time_sets]
            else:
                # look up time sets map with argument
                time_sets = ARGUMENT_MAP.get(sys.argv[1])
                # if no match, check if time input
                if not time_sets:
                    time_sets = []
                    for i in sys.argv[1:]:
                        try:
                            time_set = datetime.strptime(i, '%H:%M')
                            time_set = {'hour': time_set.hour, 'minute': time_set.minute}
                            time_sets.append(time_set)
                        except ValueError as error:
                            print_with_time(f'시간 형식 잘 못 입력함: {error}')
                    else:
                        if not time_sets:
                            print_with_time('모든 입력값 시간 형식 잘 못 입력함. 기존 스케줄 사용')
                            time_sets = ARGUMENT_MAP['regular']
        # if no argument
        else:
            # regular day time sets
            time_sets = ARGUMENT_MAP['regular']

        return time_sets

    def run(self):
        'run scheduler'
        print_with_time('스케줄러 실행')
        self.add_jobs()
        self.sched.start()
        self.print_next_time()
        while True:
            if keyboard.is_pressed('ctrl+alt+c'):
                print_with_time('키보드로 중단 요청')
                break
        self.sched.shutdown(wait=False)

if __name__ == '__main__':
    MyScheduler().run()
