'''
Run scheduler with fake_check_in and launch_zoom as its jobs.
Pass in argument to fire at specific time
'''

import sys

from datetime import datetime
import json

from fake_attendance.scheduler import MyScheduler

time_sets = None
# argument passed
if len(sys.argv) > 1:
    # argument as text file
    if sys.argv[1][-4:] == '.txt':
        filename = sys.argv[1]
        with open (filename, 'r', encoding='utf-8') as file:
            time_sets = [line.strip() for line in file][1:]
            time_sets = [datetime.strptime(i, '%H:%M') for i in time_sets]
            time_sets = [{'hour': i.hour, 'minute': i.minute} for i in time_sets]
    # argument as list of time
    else:
        time_sets = json.loads(sys.argv[1])

scheduler = MyScheduler(time_sets) if time_sets else MyScheduler()
scheduler.run()
