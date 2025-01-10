import pywhatkit as kit
import logging
import os
from datetime import datetime, timedelta

# WhatsApp Configuration
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")  # Replace with the recipient's WhatsApp number
WHATSAPP_MESSAGE = os.getenv("WHATSAPP_MESSAGE")

# Send WhatsApp Message
def send_whatsapp_message():
    try:
        now = datetime.now()
        # Send the message 1 minute from now to give time for the browser to open
        send_time = now + timedelta(minutes=1)
        kit.sendwhatmsg(WHATSAPP_NUMBER, WHATSAPP_MESSAGE, send_time.hour, send_time.minute)
        logging.info("WhatsApp message sent.")
    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {e}")