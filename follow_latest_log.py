import os
import time
import glob

def get_latest_log_file():
    log_files = glob.glob("logs/hydration_tracker.log*")
    if not log_files:
        return None
    latest_log_file = max(log_files, key=os.path.getctime)
    return latest_log_file

def follow_log_file(log_file):
    with open(log_file, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            print(line, end='')

if __name__ == "__main__":
    latest_log_file = get_latest_log_file()
    if latest_log_file:
        print(f"Following log file: {latest_log_file}")
        follow_log_file(latest_log_file)
    else:
        print("No log files found.")