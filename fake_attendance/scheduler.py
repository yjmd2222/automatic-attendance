'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

import os
import sys

from datetime import datetime, timedelta
import time

from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.interval import IntervalTrigger

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
    SCHED_QUIT_HOUR,
    SCHED_QUIT_MINUTE,
    INTERRUPT_SEQUENCE)
# pylint: enable=wrong-import-position

# pylint: disable=too-many-instance-attributes
class MyScheduler(BaseClass):
    'A class that manages the scheduler'

    def __init__(self):
        'initialize'
        self.sched = BackgroundScheduler()
        self.fake_check_in = FakeCheckIn(self.reschedule)
        self.launch_zoom = LaunchZoom()
        self.quit_zoom = QuitZoom()
        self.time_sets = self.get_timesets() # [('%H','%M'),...]
        self.check_in_trigger = OrTrigger([
            IntervalTrigger(
                minutes = 5,
                start_date = time_set,
                end_date = time_set + timedelta(minutes=30))\
                    for time_set in self.time_sets])
        self.quit_scheduler_job_id = '스케줄러 종료'
        self.job_ids = [
            self.fake_check_in.print_name,
            self.launch_zoom.print_name,
            self.quit_zoom.print_name,
            self.quit_scheduler_job_id]
        self.is_quit = False
        self.print_name = '스케줄러'
        super().__init__()

    def add_jobs(self):
        '''
        add 1. grab zoom link on screen
            2. launch Zoom
            3. quit Zoom
            4. quit scheduler
            5. print next trigger time for next respective runs
        '''
        self.sched.add_job(self.fake_check_in.run, self.check_in_trigger, id=self.job_ids[0])
        self.sched.add_job(self.launch_zoom.run, 'cron',\
                           hour=ZOOM_ON_HOURS, id=self.job_ids[1])
        self.sched.add_job(self.quit_zoom.run, 'cron',\
                           hour=ZOOM_QUIT_HOURS, minute=ZOOM_QUIT_MINUTE, id=self.job_ids[2])
        self.sched.add_job(self.quit, 'cron',\
                           hour=SCHED_QUIT_HOUR, minute=SCHED_QUIT_MINUTE, id=self.job_ids[3])
        self.sched.add_listener(
            callback = self.print_next_time,
            mask = EVENT_JOB_EXECUTED)

    # pylint: disable=unused-argument
    def print_next_time(self, event=None):
        'print next trigger for next jobs'
        for job_id in self.job_ids:
            next_time = self.sched.get_job(job_id).next_run_time
            print_with_time(f'다음 {job_id} 작업 실행 시각: {next_time.strftime(("%H:%M"))}')
    # pylint: enable=unused-argument

    def reschedule(self, job_id, trigger):
        'reschedule so that job with matching job_id will not run until given datetime until'
        job = self.sched.get_job(job_id)
        job.reschedule(trigger)

    def get_timesets(self):
        'receive argument from command line for which time sets to add to schedule'
        time_sets = None
        def parse_time(raw_time_sets):
            'parse time sets from raw list'
            parsed_time_sets = []
            for raw in raw_time_sets:
                try:
                    # this line first because input may not even have a colon
                    time_set = datetime.strptime(raw, '%H:%M')
                    time_set = datetime.now().replace(
                        hour = time_set.hour,
                        minute = time_set.minute,
                        second = 0)
                    # if no ValueError then check if minutes two digits
                    if len(raw.split(":")[1]) != 2:
                        raise ValueError("분이 10의 자리 숫자가 아님")
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

    def quit(self):
        'quit scheduler'
        self.is_quit = True

    def wait_for_quit(self, interrupt_sequence):
        'break if sequence is pressed or end job'
        while True:
            if keyboard.is_pressed(interrupt_sequence):
                print_with_time('키보드로 중단 요청')
                self.quit()
                time.sleep(1)
            elif self.is_quit:
                print_with_time('스케줄러 종료 요청')
                self.sched.remove_all_jobs()
                self.sched.remove_listener(self.print_next_time)
                self.sched.shutdown(wait=False)
                break

    def run(self):
        'run scheduler'
        self.add_jobs() # add all jobs
        self.sched.start() # start the scheduler
        self.print_next_time() # print time first job fires
        self.wait_for_quit(INTERRUPT_SEQUENCE) # quit with keyboard or at self.quit job time
# pylint: enable=too-many-instance-attributes

if __name__ == '__main__':
    MyScheduler().run()
