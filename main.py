import threading
import signal
import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from notification_handler import main as notification_main
from db_utils import update_hydration_logs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure the logs folder exists
log_folder = "logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Configure logging with daily rotation
log_file = os.getenv("LOG_FILE", "logs/hydration_tracker.log")
log_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
log_handler.suffix = "%Y-%m-%d"
log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.DEBUG)

# Handle graceful shutdown
def signal_handler(sig, frame):
    logging.info("Gracefully shutting down...")
    stop_event.set()

if __name__ == "__main__":
    try:
        # Initialize a threading event for stopping the loop
        stop_event = threading.Event()
        signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C

        # Start the notification thread
        main_thread = threading.Thread(target=notification_main, args=(stop_event,))
        main_thread.start()

        # Start the hydration logs update thread
        update_hydration_thread = threading.Thread(target=update_hydration_logs, args=(stop_event,))
        update_hydration_thread.start()

        main_thread.join()
        update_hydration_thread.join()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)