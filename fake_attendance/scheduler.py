'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

from datetime import datetime, timedelta

from apscheduler.schedulers.background import BlockingScheduler

from fake_attendance.fake_check_in import FakeCheckIn
from fake_attendance.launch_zoom import LaunchZoom
from fake_attendance.settings import (MINUTES, ZOOM_ON_HOUR, ZOOM_ON_MINUTE)

class MyScheduler:
    'A class that manages the scheduler'

    def __init__(self):
        'initialize'
        self.sched = BlockingScheduler(standalone=True)
        self.fake_check_in = FakeCheckIn()
        self.launch_zoom = LaunchZoom()

    def shutdown(self, event):
        'testing interrupt'
        if self.sched.running and event:
            self.sched.shutdown(wait=False)

    def add_jobs(self):
        '''
        add 1. grabbing zoom link on screen
            2. turn on zoom camera
        '''
        self.sched.add_job(self.fake_check_in.run, 'interval', minutes=MINUTES)
        self.sched.add_job(self.launch_zoom.run, 'cron',\
                           hour=ZOOM_ON_HOUR, minute=ZOOM_ON_MINUTE)

    def run(self):
        'run scheduler'
        self.add_jobs()
        try:
            self.sched.start()
        except KeyboardInterrupt:
            print('interrupt')
