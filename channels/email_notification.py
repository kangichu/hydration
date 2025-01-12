import os
import smtplib
import logging
from datetime import datetime
from utils.db_utils import log_email_status

# Email Configuration
EMAIL = os.getenv("MAIL_USERNAME")
PASSWORD = os.getenv("MAIL_PASSWORD")
TO_EMAIL = os.getenv("MAIL_TO")
MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_ENCRYPTION = os.getenv("MAIL_ENCRYPTION")

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