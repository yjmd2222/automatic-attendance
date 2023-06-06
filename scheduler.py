'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BlockingScheduler

from auto_check_qr import FakeCheckIn
from turn_on_camera import TurnOnCamera
from info import HOUR, MINUTE, MINUTES

class MyScheduler:
    'A class that manages the scheduler'

    def __init__(self):
        'initialize'
        self.sched = BlockingScheduler(standalone=True)
        self.fake_check_in = FakeCheckIn()
        self.turn_on_camera = TurnOnCamera()

    def shutdown(self, event):
        'testing interrupt'
        if self.sched.running and event:
            self.sched.shutdown(wait=False)

    def add_jobs(self):
        '''
        add 1. grabbing zoom link on screen
            2. turn on zoom camera
        '''
        self.sched.add_listener(self.shutdown, EVENT_JOB_EXECUTED)
        self.sched.add_job(self.fake_check_in.run, 'interval', minutes=MINUTES)
        self.sched.add_job(self.turn_on_camera.run, 'cron', hour=HOUR, minute=MINUTE)

    def run(self):
        'run scheduler'
        self.add_jobs()
        try:
            self.sched.start()
        except KeyboardInterrupt:
            self.sched.shutdown()
