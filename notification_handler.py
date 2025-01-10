import time
from datetime import datetime, timedelta
from plyer import notification
import logging
from db_utils import initialize_database, get_last_hydration_log_time, get_last_email_log_time, log_hydration_reminder, check_weekly_goal, send_email, show_hydration_popup

# Hydration Tracker Configuration
DRINK_INTERVAL = 100  # minutes (1.67 hours)
BOTTLE_VOLUME = 0.5  # liters
DAILY_GOAL = 2  # liters
PRIZE_DAY = "Sunday"  # Day to evaluate prizes

# Notification Settings
NOTIFICATION_TITLE = "Hydration Reminder"
NOTIFICATION_MESSAGE = "Time to drink water!"
SLEEP_INTERVAL = 60  # seconds

# Send Notification
def send_notification():
    try:
        notification.notify(
            title=NOTIFICATION_TITLE,
            message=NOTIFICATION_MESSAGE,
            timeout=10
        )
        logging.info("Notification sent.")
    except Exception as e:
        logging.error(f"Error sending notification: {e}")

# Main Hydration Reminder Loop
def main(stop_event):
    logging.debug("Starting main hydration reminder loop.")
    initialize_database()

    # Get the last hydration log time and email log time
    last_hydration_log_time = get_last_hydration_log_time()
    last_email_log_time = get_last_email_log_time()

    # Determine the last drink time based on the latest log
    last_drink_time = max(last_hydration_log_time, last_email_log_time) if last_hydration_log_time and last_email_log_time else datetime.now() - timedelta(minutes=DRINK_INTERVAL)

    while not stop_event.is_set():
        now = datetime.now()
        current_hour = now.hour

        # Check if the current time is within the allowed range (9 AM to 12 AM)
        if 9 <= current_hour < 24:
            logging.info(f"Current time: {now}, Last drink time: {last_drink_time}")
            # Check if it's time to remind
            time_since_last_drink = (now - last_drink_time).total_seconds()
            logging.debug(f"Time since last drink: {time_since_last_drink} seconds")
            if time_since_last_drink >= DRINK_INTERVAL * 60:
                # Check if a notification has already been sent within the same period
                if last_hydration_log_time and (now - last_hydration_log_time).total_seconds() < DRINK_INTERVAL * 60:
                    logging.info("A notification has already been sent within the same period. Skipping this reminder.")
                else:
                    logging.info("Time to send a hydration reminder.")
                    send_notification()
                    send_email("Hydration Reminder", "It's time to drink 0.5L of water!")
                    log_hydration_reminder(False, status='pending')  # Log as pending
                    is_drunk = show_hydration_popup()
                    if is_drunk is None:
                        log_hydration_reminder(False, status='pending')
                    else:
                        log_hydration_reminder(is_drunk, status='completed')
                    last_drink_time = now

            # Check weekly goal at the end of the week
            if now.strftime('%A') == PRIZE_DAY:
                check_weekly_goal()

        # Wait before the next check
        logging.debug(f"Waiting for {SLEEP_INTERVAL} seconds before next check.")
        stop_event.wait(SLEEP_INTERVAL)