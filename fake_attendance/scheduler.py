'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

import os
import sys

from datetime import datetime
import time

from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger

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
    ZOOM_ON_TIMES,
    ZOOM_QUIT_TIMES,
    SCHED_QUIT_TIMES,
    INTERRUPT_SEQUENCE)
# pylint: enable=wrong-import-position

# pylint: disable=too-many-instance-attributes
class MyScheduler(BaseClass):
    'A class that manages the scheduler'
    def __init__(self):
        'initialize'
        self.sched = BackgroundScheduler()
        self.fake_check_in = FakeCheckIn(self.drop_runs_until)
        self.launch_zoom = LaunchZoom()
        self.quit_zoom = QuitZoom()
        self.quit_scheduler_job_id = '스케줄러 종료'
        self.job_ids = [
            self.fake_check_in.print_name,
            self.launch_zoom.print_name,
            self.quit_zoom.print_name,
            self.quit_scheduler_job_id]
        self.all_time_sets = self.map_dict(
            self.job_ids,
            (self.get_timesets_from_terminal(),
             ZOOM_ON_TIMES,
             ZOOM_QUIT_TIMES,
             SCHED_QUIT_TIMES))
        self.all_job_funcs = self.map_dict(
            self.job_ids,
            (self.fake_check_in.run,
             self.launch_zoom.run,
             self.quit_zoom.run,
             self.quit))
        self.all_triggers = self.map_dict(
            self.job_ids,
            (self.build_trigger(self.all_time_sets[job_id]) for job_id in self.job_ids))
        self.next_times = {}
        self.is_quit = False
        self.print_name = '스케줄러'
        super().__init__()

    def map_dict(self, keys, values):
        'build dict with given iterables'
        return {zipped[0]: zipped[1] for zipped in zip(keys, values)}

    def build_trigger(self, time_sets):
        'build trigger with given time_sets'
        return OrTrigger(
            [CronTrigger(
                year   = time_set.year,
                month  = time_set.month,
                day    = time_set.day,
                hour   = time_set.hour,
                minute = time_set.minute)\
                    for time_set in time_sets])

    def add_jobs(self):
        '''
        add 1. grab zoom link on screen
            2. launch Zoom
            3. quit Zoom
            4. quit scheduler
            5. print next trigger time for next respective runs
        '''
        # first four jobs
        for job_id in self.job_ids:
            self.sched.add_job(
                func = self.all_job_funcs[job_id],
                trigger = self.all_triggers[job_id],
                id = job_id)
        # last job/listener
        self.sched.add_listener(
            callback = self.print_next_time,
            mask = EVENT_JOB_EXECUTED)

    # pylint: disable=unused-argument
    def print_next_time(self, event=None):
        'print next trigger for next jobs'
        for job_id in self.job_ids:
            try:
                next_time = self.sched.get_job(job_id).next_run_time
                print_with_time(f'다음 {job_id} 작업 실행 시각: {next_time.strftime(("%H:%M"))}')
                self.next_times[job_id] = next_time
            except AttributeError:
                print_with_time(f'오늘 남은 {job_id} 작업 없음')
                self.next_times[job_id] = None
    # pylint: enable=unused-argument

    def drop_runs_until(self, job_id, until):
        'reschedule so that job with matching job_id will not run until give datetime \'until\''
        # which time sets
        time_sets = self.all_time_sets[job_id]
        # dropped the ones before 'until'
        new_time_sets = [time_set for time_set in time_sets if time_set > until]
        # variables to pass to self.reschedule
        rescheduled_trigger = None
        is_remove_job = False
        # if next run left
        if new_time_sets:
            # reschedule
            rescheduled_trigger = OrTrigger(self.build_trigger(new_time_sets))
        # else
        else:
            # remove the job
            is_remove_job = True
        self.reschedule(job_id, rescheduled_trigger, is_remove_job)

    def reschedule(self, job_id, rescheduled_trigger, is_remove_job):
        'method that is called at the end of drop_runs_until'
        # if no next run
        if is_remove_job:
            try:
                self.sched.remove_job(job_id)
            except JobLookupError:
                print_with_time(f'오늘 남은 {job_id} 작업 없음')
        # else
        else:
            print(rescheduled_trigger)
            self.sched.reschedule_job(job_id, trigger=rescheduled_trigger)

    def get_timesets_from_terminal(self):
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

    def quit(self, message='스케줄러 종료 시간'):
        'quit scheduler'
        time.sleep(1)
        print_with_time(message)
        self.is_quit = True
        time.sleep(1)

    def wait_for_quit(self, interrupt_sequence):
        'break if sequence is pressed or end job'
        while True:
            if keyboard.is_pressed(interrupt_sequence):
                self.quit('키보드로 중단 요청')
            elif all((not next_run for next_run in self.next_times.values())):
                self.quit('남은 작업 없음')
            if self.is_quit:
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
