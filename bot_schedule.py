from apscheduler.schedulers.blocking import BlockingScheduler
from full_scrapeProgress import getLiveData
schedule = BlockingScheduler()

@schedule.scheduled_job('interval', seconds=30)
def timed_job():
    getLiveData()

schedule.start()    