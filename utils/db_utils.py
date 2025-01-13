import mysql.connector
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import smtplib
import tkinter as tk
from tkinter import messagebox
import threading
import sys

# Load environment variables
load_dotenv()

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

# Initialize DB Connection
def db_connect():
    try:
        logging.debug("Attempting to connect to the database.")
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

# Get the last hydration log time
def get_last_hydration_log_time():
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT MAX(date_time) FROM hydration_logs
            """)
            last_log_time = cursor.fetchone()[0]
            return last_log_time
    except mysql.connector.Error as err:
        logging.error(f"Error fetching last hydration log time: {err}")
        return None

# Get the last email log time
def get_last_email_log_time():
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT MAX(date_time) FROM email_logs
            """)
            last_email_time = cursor.fetchone()[0]
            return last_email_time
    except mysql.connector.Error as err:
        logging.error(f"Error fetching last email log time: {err}")
        return None

# Log hydration reminder
def log_hydration_reminder(is_drunk, status='pending', log_time=None, update_pending=False):
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            now = log_time if log_time else datetime.now()
            if update_pending:
                # Update the latest pending log entry to completed
                cursor.execute("""
                UPDATE hydration_logs
                SET is_drunk = %s, status = %s
                WHERE status = 'pending'
                ORDER BY date_time DESC
                LIMIT 1
                """, (is_drunk, status))
            else:
                # Check if a log entry already exists within the same minute
                cursor.execute("""
                SELECT COUNT(*) FROM hydration_logs
                WHERE DATE_FORMAT(date_time, '%Y-%m-%d %H:%i') = DATE_FORMAT(%s, '%Y-%m-%d %H:%i')
                """, (now,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                    INSERT INTO hydration_logs (date_time, bottle_volume, is_drunk, status)
                    VALUES (%s, %s, %s, %s)
                    """, (now, 0.5, is_drunk, status))
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

            goal_met = bottles_drunk >= (2 / 0.5) * 7
            prize_awarded = goal_met and today.strftime('%A') == "Sunday"

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
    timer = threading.Timer(60, on_timeout)
    timer.start()

    root.mainloop()
    timer.cancel()  # Cancel the timer if the user responds in time
    return is_drunk

# Get pending hydration logs
def get_pending_hydration_logs():
    try:
        with db_connect() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
            SELECT id, date_time
            FROM hydration_logs
            WHERE status = 'pending'
            """)
            pending_logs = cursor.fetchall()
            return pending_logs
    except mysql.connector.Error as err:
        logging.error(f"Error fetching pending hydration logs: {err}")
        return []

# Update hydration log status
def update_hydration_log_status(log_id, is_drunk, status):
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE hydration_logs
            SET is_drunk = %s, status = %s
            WHERE id = %s
            """, (is_drunk, status, log_id))
            conn.commit()
            logging.info(f"Hydration log {log_id} updated to {status}.")
    except mysql.connector.Error as err:
        logging.error(f"Error updating hydration log {log_id}: {err}")

# CLI to update pending hydration logs
def update_hydration_logs(stop_event):
    logging.debug("Starting CLI to update pending hydration logs.")
    while not stop_event.is_set():
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
            logging.info("No pending hydration logs.")
            break

        print("Pending hydration logs:")
        for i, (log_id, date_time) in enumerate(pending_logs, start=1):
            print(f"{i}. {date_time}")

        selection = input("Enter the numbers of the logs you want to update (comma-separated, or 'q' to quit): ")
        if selection.lower() == 'q':
            break

        try:
            indices = [int(x) for x in selection.split(',') if x.isdigit()]
            for i in indices:
                if 1 <= i <= len(pending_logs):
                    log_id = pending_logs[i - 1][0]
                    with db_connect() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                        UPDATE hydration_logs
                        SET is_drunk = %s, status = 'completed'
                        WHERE id = %s
                        """, (True, log_id))
                        conn.commit()
                    print(f"Updated hydration reminder for log ID {log_id}.")
                    logging.info(f"Updated hydration reminder for log ID {log_id}.")
                else:
                    print(f"Invalid selection: {i}. Please try again.")
                    logging.warning(f"Invalid selection: {i}.")
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")
            logging.warning("Invalid input. Please enter numbers separated by commas.")