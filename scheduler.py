import time
import schedule
import logging
import sys

from database import create_tables
from etl import run_etl 

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - SCHEDULER - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def start_scheduler():
    print("--- START SCHEDULERA ---", flush=True)
    create_tables()
    run_etl()

    schedule.every(10).minutes.do(run_etl)
    
    logging.info("Application scheduled. Use Ctrl+C to stop the application.")
    print("--- Waiting for next execution ---", flush=True)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.", flush=True)

if __name__ == "__main__":
    start_scheduler()