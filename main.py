import threading
import signal
import logging
import sys
import os
import subprocess
from concurrent_log_handler import ConcurrentRotatingFileHandler
from handlers.notification_handler import main as notification_main
from utils.db_utils import update_hydration_logs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure the logs folder exists
log_folder = "logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Configure logging with rotation based on file size
log_file = os.getenv("LOG_FILE", "logs/hydration_tracker.log")
log_handler = ConcurrentRotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=7)  # 10 MB per log file
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

        # Open another terminal and run follow_latest_log.py
        if sys.platform == "win32":
            subprocess.Popen(["start", "cmd", "/k", "python", "follow_latest_log.py"], shell=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Terminal", "python follow_latest_log.py"])
        elif sys.platform == "linux":
            subprocess.Popen(["gnome-terminal", "--", "python3", "follow_latest_log.py"])

        main_thread.join()
        update_hydration_thread.join()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)