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
from fake_attendance.abc import BaseClass
from fake_attendance.fake_check_in import FakeCheckIn
from fake_attendance.helper import print_with_time
from fake_attendance.launch_zoom import LaunchZoom
from fake_attendance.quit_zoom import QuitZoom
from fake_attendance.settings import (
    ARGUMENT_MAP,
    ZOOM_ON_HOURS,
    ZOOM_QUIT_HOURS,
    ZOOM_QUIT_MINUTE,
    INTERRUPT_SEQUENCE)
# pylint: enable=wrong-import-position

# pylint: disable=too-many-instance-attributes
class MyScheduler(BaseClass):
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
        self.job_ids = [
            self.fake_check_in.print_name,
            self.launch_zoom.print_name,
            self.quit_zoom.print_name]
        self.print_name = '스케줄러'
        super().__init__()

    def add_jobs(self):
        '''
        add 1. grab zoom link on screen
            2. launch Zoom
            3. print next trigger time for next QR check
        '''
        self.sched.add_job(self.fake_check_in.run, self.check_in_trigger, id=self.job_ids[0])
        self.sched.add_job(self.launch_zoom.run, 'cron',\
                           hour=ZOOM_ON_HOURS, id=self.job_ids[1])
        self.sched.add_job(self.quit_zoom.run, 'cron',\
                           hour=ZOOM_QUIT_HOURS, minute=ZOOM_QUIT_MINUTE, id=self.job_ids[2])
        self.sched.add_listener(
            callback = lambda event: self.print_next_time(),
            mask = EVENT_JOB_EXECUTED)

    def print_next_time(self):
        'print next trigger for next jobs'
        for job_id in self.job_ids:
            next_time = self.sched.get_job(job_id).next_run_time
            print_with_time(f'다음 {job_id} 스크립트 실행 시각: {next_time.strftime(("%H:%M"))}')

    def get_timesets(self):
        'receive argument from command line for which time sets to add to schedule'
        time_sets = None
        def parse_time(raw_time_sets):
            'parse time sets from raw list'
            parsed_time_sets = []
            for raw in raw_time_sets:
                try:
                    time_set = datetime.strptime(raw, '%H:%M')
                    if len(raw.split(":")[1]) != 2:
                        raise ValueError("분이 10의 자리 숫자가 아님")
                    time_set = {'hour': time_set.hour, 'minute': time_set.minute}
                    parsed_time_sets.append(time_set)
                except ValueError as error:
                    print_with_time(f'시간 형식 잘 못 입력함. 이 부분 스킵: {error}')
            if not parsed_time_sets:
                print_with_time('모든 입력값 시간 형식 잘 못 입력함. 기본 스케줄 사용')
                parsed_time_sets = ARGUMENT_MAP['regular']

            return parsed_time_sets

        # check argument passed
        if len(sys.argv) > 1:
            # argument as text file
            if '.txt' in sys.argv[1]:
                filename = sys.argv[1]
                with open (filename, 'r', encoding='utf-8') as file:
                    raw_time_sets = [time_set.strip() for time_set in file[1:]]
                    time_sets = parse_time(raw_time_sets)
            else:
                # look up time sets map with argument
                time_sets = ARGUMENT_MAP.get(sys.argv[1])
                # if no match, check if time input
                if not time_sets:
                    raw_time_sets = sys.argv[1:]
                    time_sets = parse_time(raw_time_sets)
        # if no argument
        else:
            # regular day time sets
            time_sets = ARGUMENT_MAP['regular']

        return time_sets

    def interrupt_from_keyboard(self, interrupt_sequence):
        'break if sequence is pressed'
        while True:
            if keyboard.is_pressed(interrupt_sequence):
                print_with_time('키보드로 중단 요청')
                break

    def run(self):
        'run scheduler'
        self.add_jobs() # add all jobs
        self.sched.start() # start the scheduler
        self.print_next_time() # print time first job fires
        self.interrupt_from_keyboard(INTERRUPT_SEQUENCE) # allow quit with keyboard
        self.sched.shutdown(wait=False) # shutdown scheduler if quit
# pylint: enable=too-many-instance-attributes

if __name__ == '__main__':
    MyScheduler().run()
