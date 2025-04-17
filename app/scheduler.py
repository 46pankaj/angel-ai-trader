from apscheduler.schedulers.background import BackgroundScheduler
from ai.strategy_engine import run_strategy

def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_strategy, 'interval', minutes=5)
    scheduler.start()
