import pywhatkit as kit
import logging
import os
import pyautogui
import time

# WhatsApp Configuration
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")  # Replace with the recipient's WhatsApp number
WHATSAPP_MESSAGE = os.getenv("WHATSAPP_MESSAGE")

# Send WhatsApp Message
def send_whatsapp_message(message):
    try:
        # Send the message instantly
        kit.sendwhatmsg_instantly(WHATSAPP_NUMBER, message, wait_time=10, tab_close=False)
        logging.info("WhatsApp message opened in browser.")

        # Wait for the browser to open and load the message
        time.sleep(15)

        # Press 'Enter' to send the message
        pyautogui.press('enter')
        logging.info("WhatsApp message sent.")

        # Wait for a few seconds to ensure the message is sent
        time.sleep(5)

        # Close the tab using pyautogui
        pyautogui.hotkey('ctrl', 'w')
        logging.info("WhatsApp tab closed.")
    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {e}", exc_info=True)