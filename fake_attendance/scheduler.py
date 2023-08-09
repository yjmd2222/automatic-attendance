'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

from datetime import datetime, timedelta

from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger

from pynput import keyboard

from fake_attendance.abc import BaseClass
from fake_attendance.arg_parse import parsed_args
from fake_attendance.fake_check_in import FakeCheckIn
from fake_attendance.helper import (
    print_with_time,
    map_dict)
from fake_attendance.launch_zoom import LaunchZoom
from fake_attendance.quit_zoom import QuitZoom
from fake_attendance.settings import (
    ARGUMENT_MAP,
    ZOOM_ON_TIMES,
    ZOOM_QUIT_TIMES,
    SCHED_QUIT_TIMES,
    HOTKEYS_MAP)

# pylint: disable=too-many-instance-attributes
class MyScheduler(BaseClass):
    'A class that manages the scheduler'
    print_name = '스케줄러'

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
        self.all_time_sets = map_dict(
            self.job_ids,
            (self.get_timesets_from_terminal(),
             ZOOM_ON_TIMES,
             ZOOM_QUIT_TIMES,
             SCHED_QUIT_TIMES))
        self.all_job_funcs = map_dict(
            self.job_ids,
            (self.fake_check_in.run,
             self.launch_zoom.run,
             self.quit_zoom.run,
             self.quit))
        self.all_triggers = map_dict(
            self.job_ids,
            (self.build_trigger(self.all_time_sets[job_id]) for job_id in self.job_ids))
        self.next_times = {}
        self.until = None
        self.is_quit = False
        super().__init__()

    def build_trigger(self, time_sets):
        'build trigger with given time_sets'
        return OrTrigger(
            [CronTrigger(
                year   = time_set.year,
                month  = time_set.month,
                day    = time_set.day,
                hour   = time_set.hour,
                minute = time_set.minute,
                second = time_set.second)\
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

    def get_current_timesets(self, job_id):
        'get current trigger time sets'
        time_sets = self.all_time_sets[job_id]
        if self.until:
            time_sets = [time_set for time_set in time_sets if time_set > self.until]
        return time_sets

    def drop_runs_until(self, job_id, until):
        'reschedule so that job with matching job_id will not run until give datetime \'until\''
        # save variable
        self.until = until
        # new time_sets
        new_time_sets = self.get_current_timesets(job_id)
        # reschedule
        rescheduled_trigger = self.build_trigger(new_time_sets)
        self.sched.reschedule_job(job_id, trigger=rescheduled_trigger)

    def add_run(self, job_id, time_set):
        'extend trigger at given time. Adds job if no job found'
        new_time_sets = self.get_current_timesets(job_id) + [time_set]
        rescheduled_trigger = self.build_trigger(new_time_sets)
        # extend trigger
        try:
            self.sched.reschedule_job(job_id, trigger=rescheduled_trigger)
        # if can't extend trigger because not scheduled, add job
        except JobLookupError:
            self.sched.add_job(
                func = self.all_job_funcs[job_id],
                trigger = rescheduled_trigger,
                id = job_id)

    def get_timesets_from_terminal(self):
        'receive argument from command line for which time sets to add to schedule'
        time_sets = []

        def parse_time(raw_time_sets):
            'parse time sets from raw list'
            # pylint: disable=import-outside-toplevel
            from fake_attendance.helper import convert_to_datetime
            # pylint: enable=import-outside-toplevel
            parsed_time_sets = []
            is_success = None
            for raw in raw_time_sets:
                try:
                    # this line first because input may not even have a colon
                    time_set = convert_to_datetime(raw)
                    # if no ValueError then check if minutes two digits
                    if len(raw.split(":")[1]) != 2:
                        raise ValueError("분이 10의 자리 숫자가 아님")
                    parsed_time_sets.append(time_set)
                except ValueError as error:
                    print_with_time(f'시간 \'%H:%M\' 형식으로 입력해야 함. 이 부분 스킵: {error}')
            if parsed_time_sets:
                is_success = 'true'
            else:
                print_with_time('모든 입력값 시간 형식 잘 못 입력함')
                is_success = 'false'

            return parsed_time_sets, is_success

        # check argument passed. overrided in the order of predefined, text file, and time input
        if parsed_args:
            # this str will be checked whether to extrapolate or not
            is_success = 'false'
            # predefined time sets
            if parsed_args.predefined:
                # look up time sets map with argument
                try:
                    time_sets = ARGUMENT_MAP[parsed_args.predefined]
                    print_with_time(f'사전 정의 스케줄: {parsed_args.predefined}')
                    is_success = 'pass'
                except KeyError:
                    print_with_time(f'사전 정의 스케줄 옵션 잘 못 입력함. {list(ARGUMENT_MAP)} 중 입력해야 함')
                    is_success = 'false'
            # text file
            if is_success == 'false' and (parsed_args.textfile and '.txt' in parsed_args.textfile):
                with open (parsed_args.textfile, 'r', encoding='utf-8') as file:
                    raw_time_sets = [time_set.strip() for time_set in file.readlines()[1:]]
                    time_sets, is_success = parse_time(raw_time_sets)
            # check time input
            if is_success == 'false' and parsed_args.time:
                time_sets, is_success = parse_time(parsed_args.time)
            if parsed_args.extrapolate:
                if is_success == 'true':
                    # pylint: disable=import-outside-toplevel
                    from fake_attendance.helper import extrapolate_time_sets, unfoil_time_sets
                    # pylint: enable=import-outside-toplevel
                    time_sets = unfoil_time_sets(
                        [extrapolate_time_sets(time_set) for time_set in time_sets]
                    )
                else: # currently pass or false
                    print_with_time('기본 스케줄은 5분 offset 적용 안 함')
        # if time_sets empty
        if not time_sets:
            # regular day time sets
            print_with_time('기본 스케줄(regular) 사용')
            time_sets = ARGUMENT_MAP['regular']

        return time_sets

    def quit(self, message='스케줄러 종료 요청'):
        'sets flag self.is_quit to True'
        print_with_time(message)
        self.is_quit = True
        self.sched.remove_all_jobs()
        self.sched.remove_listener(self.print_next_time)

    def keyboard_command_listener(self):
        'setting up listener for keyboard commands'
        # dictionary for storing command: on_activate_wrapper
        on_activate_dict = {}
        def on_activate(job_id):
            'inner on_activate function that is fired on command'
            print_with_time(f'강제 {job_id} 커맨드 입력 확인')
            self.add_run(job_id, datetime.now() + timedelta(seconds=1))

        # adding the wrapper to dictionary
        for job_id in self.job_ids:
            # avoid cell-var-from-loop by using x in loop instead of last job_id
            on_activate_dict[HOTKEYS_MAP[job_id]] = lambda x=job_id: on_activate(x)
        listener = keyboard.GlobalHotKeys(on_activate_dict)
        listener.start()

    def wait_for_event(self):
        'runs APScheduler in background and waits for commands until quit command is passed'
        # wait for commands
        try:
            while True:
                # quit if no job left
                if all((not next_run for next_run in self.next_times.values())):
                    self.quit('남은 작업 없음')
                # quit
                if self.is_quit:
                    break
        # quit with ctrl + c
        except KeyboardInterrupt:
            print_with_time('Ctrl + C 입력 확인')
            self.quit()
        # shutdown scheduler
        self.sched.shutdown()

    def run(self):
        'run scheduler'
        self.add_jobs() # add all jobs
        self.sched.start() # start the scheduler
        self.print_next_time() # print time first job fires
        self.keyboard_command_listener() # listens to launch, check-in, quit, exit commands
        self.wait_for_event() # while loop that runs until quit
# pylint: enable=too-many-instance-attributes

if __name__ == '__main__':
    # pylint: disable=ungrouped-imports
    from fake_attendance.helper import fix_pyautogui
    fix_pyautogui()
    # pylint: enable=ungrouped-imports

    MyScheduler().run()
