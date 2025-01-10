import os
import time
from datetime import datetime, timedelta
from plyer import notification
import mysql.connector
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
import smtplib
import threading
import signal
import sys
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(filename=os.getenv("LOG_FILE", "hydration_tracker.log"), level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USERNAME", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_DATABASE", "hydration"),
}

# Email Configuration
EMAIL = os.getenv("MAIL_USERNAME")
PASSWORD = os.getenv("MAIL_PASSWORD")
TO_EMAIL = os.getenv("MAIL_TO")
MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_ENCRYPTION = os.getenv("MAIL_ENCRYPTION")

# Hydration Tracker Configuration
DRINK_INTERVAL = float(os.getenv("DRINK_INTERVAL", 100))  # minutes (1.67 hours)
BOTTLE_VOLUME = float(os.getenv("BOTTLE_CAPACITY", 0.5))  # liters
DAILY_GOAL = float(os.getenv("DAILY_GOAL", 2))  # liters
PRIZE_DAY = os.getenv("PRIZE_DAY", "Sunday")  # Day to evaluate prizes

# Notification Settings
NOTIFICATION_TITLE = os.getenv("NOTIFICATION_TITLE", "Hydration Reminder")
NOTIFICATION_MESSAGE = os.getenv("NOTIFICATION_MESSAGE", "Time to drink water!")
SLEEP_INTERVAL = int(os.getenv("SLEEP_INTERVAL", 60))  # seconds
PROMPT_TIMEOUT = int(os.getenv("PROMPT_TIMEOUT", 60))  # seconds

# Initialize DB Connection
def db_connect():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to database: {err}")
        sys.exit(1)

# Initialize Database Tables
def initialize_database():
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hydration_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date_time DATETIME NOT NULL,
                bottle_volume FLOAT NOT NULL,
                is_drunk BOOLEAN DEFAULT FALSE,
                status VARCHAR(10) DEFAULT 'pending'
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_goals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                total_bottles INT NOT NULL,
                goal_met BOOLEAN DEFAULT FALSE,
                prize_awarded BOOLEAN DEFAULT FALSE
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date_time DATETIME NOT NULL,
                subject VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT
            )
            """)
            conn.commit()
            logging.info("Database tables initialized successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Error initializing database: {err}")
        sys.exit(1)

# Log hydration reminder
def log_hydration_reminder(is_drunk, status='completed', log_time=None):
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            now = log_time if log_time else datetime.now()
            cursor.execute("""
            INSERT INTO hydration_logs (date_time, bottle_volume, is_drunk, status)
            VALUES (%s, %s, %s, %s)
            """, (now, BOTTLE_VOLUME, is_drunk, status))
            conn.commit()
            logging.info(f"Hydration reminder logged: {now}, Drunk: {is_drunk}, Status: {status}")
    except mysql.connector.Error as err:
        logging.error(f"Error logging hydration reminder: {err}")

# Log email status
def log_email_status(subject, message, success, error_message=None):
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute("""
            INSERT INTO email_logs (date_time, subject, message, success, error_message)
            VALUES (%s, %s, %s, %s, %s)
            """, (now, subject, message, success, error_message))
            conn.commit()
            logging.info(f"Email log: {subject}, Success: {success}, Error: {error_message}")
    except mysql.connector.Error as err:
        logging.error(f"Error logging email status: {err}")

# Check and log weekly goals
def check_weekly_goal():
    try:
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        with db_connect() as conn:
            cursor = conn.cursor()
            # Check if the week is already recorded
            cursor.execute("""
            SELECT COUNT(*), SUM(is_drunk)
            FROM hydration_logs
            WHERE date_time BETWEEN %s AND %s
            """, (start_of_week, end_of_week))
            total_reminders, bottles_drunk = cursor.fetchone()

            goal_met = bottles_drunk >= (DAILY_GOAL / BOTTLE_VOLUME) * 7
            prize_awarded = goal_met and today.strftime('%A') == PRIZE_DAY

            # Insert weekly data
            cursor.execute("""
            INSERT INTO weekly_goals (start_date, end_date, total_bottles, goal_met, prize_awarded)
            VALUES (%s, %s, %s, %s, %s)
            """, (start_of_week.date(), end_of_week.date(), bottles_drunk, goal_met, prize_awarded))
            conn.commit()

            if prize_awarded:
                logging.info("Congratulations! You've won this week's hydration prize!")
                print("Congratulations! You've won this week's hydration prize!")
    except mysql.connector.Error as err:
        logging.error(f"Error checking weekly goal: {err}")

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

# Send Email
def send_email(subject, message):
    try:
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, TO_EMAIL, f"Subject: {subject}\n\n{message}")
        log_email_status(subject, message, True)
        logging.info("Email sent successfully.")
    except Exception as e:
        log_email_status(subject, message, False, str(e))
        logging.error(f"Failed to send email: {e}")

# Show popup for hydration response with timeout
def show_hydration_popup():
    def on_yes():
        nonlocal is_drunk
        is_drunk = True
        root.destroy()

    def on_no():
        nonlocal is_drunk
        is_drunk = False
        root.destroy()

    def on_timeout():
        nonlocal is_drunk
        is_drunk = None  # Set to None to indicate pending status
        root.destroy()

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.title("Hydration Check")
    root.geometry("300x100")

    is_drunk = None

    response = messagebox.askyesno(
        "Hydration Check", "Did you drink 0.5L of water as prompted?"
    )

    if response:
        on_yes()
    else:
        on_no()

    # Set a timer to automatically close the popup after the timeout
    timer = threading.Timer(PROMPT_TIMEOUT, on_timeout)
    timer.start()

    root.mainloop()
    timer.cancel()  # Cancel the timer if the user responds in time
    return is_drunk

# Main Hydration Reminder Loop
def main():
    initialize_database()
    last_drink_time = datetime.now() - timedelta(minutes=DRINK_INTERVAL)

    while not stop_event.is_set():
        now = datetime.now()
        current_hour = now.hour

        # Check if the current time is within the allowed range (9 AM to 12 AM)
        if 9 <= current_hour < 24:
            # Check if it's time to remind
            if (now - last_drink_time).total_seconds() >= DRINK_INTERVAL * 60:
                send_notification()
                send_email("Hydration Reminder", "It's time to drink 0.5L of water!")
                is_drunk = show_hydration_popup()
                if is_drunk is None:
                    log_hydration_reminder(False, status='pending')
                else:
                    log_hydration_reminder(is_drunk)
                last_drink_time = now

            # Check weekly goal at the end of the week
            if now.strftime('%A') == PRIZE_DAY:
                check_weekly_goal()

        # Wait before the next check
        stop_event.wait(SLEEP_INTERVAL)

# CLI to update pending hydration logs
def update_hydration_logs():
    while True:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, date_time
            FROM hydration_logs
            WHERE status = 'pending'
            """)
            pending_logs = cursor.fetchall()

        if not pending_logs:
            print("No pending hydration logs.")
            break

        print("Pending hydration logs:")
        for i, (log_id, date_time) in enumerate(pending_logs, start=1):
            print(f"{i}. {date_time}")

        selection = input("Enter the number of the log you want to update (or 'q' to quit): ")
        if selection.lower() == 'q':
            break

        try:
            selection = int(selection)
            if 1 <= selection <= len(pending_logs):
                log_id = pending_logs[selection - 1][0]
                with db_connect() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                    UPDATE hydration_logs
                    SET is_drunk = %s, status = 'completed'
                    WHERE id = %s
                    """, (True, log_id))
                    conn.commit()
                print(f"Updated hydration reminder for log ID {log_id}.")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Signal handler to gracefully stop the script
def signal_handler(sig, frame):
    print("Stopping the script...")
    logging.info("Stopping the script...")
    stop_event.set()
    main_thread.join()
    sys.exit(0)

if __name__ == "__main__":
    initialize_database()  # Ensure tables are created before starting
    stop_event = threading.Event()
    signal.signal(signal.SIGINT, signal_handler)
    main_thread = threading.Thread(target=main)
    main_thread.start()

    update_hydration_logs()