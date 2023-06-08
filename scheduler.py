'''
Scheduler that runs FakeCheckIn and TurnOnCamera
'''

from apscheduler.schedulers.background import BlockingScheduler

from auto_check_qr import FakeCheckIn
from archive.turn_on_camera import TurnOnCamera
from launch_zoom import LaunchZoom
from settings import (MINUTES, ZOOM_ON_HOUR, ZOOM_ON_MINUTE)

class MyScheduler:
    'A class that manages the scheduler'

    def __init__(self):
        'initialize'
        self.sched = BlockingScheduler(standalone=True)
        self.fake_check_in = FakeCheckIn()
        self.turn_on_camera = TurnOnCamera()
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

if __name__ == '__main__':
    MyScheduler().run()
