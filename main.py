from twitter_service import run_main_loop
from apscheduler.schedulers.background import BlockingScheduler

sched = BlockingScheduler()
sched.add_job(run_main_loop, 'interval', seconds=60)

sched.start()
