# Hydration Tracker

**Description**:  
Hydration Tracker is an intuitive application designed to help you stay hydrated throughout the day. It allows you to set daily water intake goals, track your water consumption, and receive reminders to drink water at regular intervals. With its customizable features, the app ensures you maintain optimal hydration levels for improved health and well-being.

---

## Features
- Set personalized daily water intake goals.
- Log water consumption with ease.
- Receive reminders to drink water at regular intervals.
- View daily, weekly, and monthly hydration statistics.
- Customize reminder intervals and notification settings.
- Notifications via desktop, email, and WhatsApp.

---

## Technologies Used
- **Programming Language**: Python  
- **Database**: MySQL  
- **Version Control**: Git  

---

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/hydration-tracker.git
   ```
2. **Navigate to the Project Directory**:
   ```bash
   cd hydration-tracker
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```
5. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
6. **Configure Environment Variables**:
   - Copy the `.env.example` file to `.env` and fill in the required values.
     ```bash
     cp .env.example .env
     ```

7. **Set Up the Database**:
   - Configure the MySQL database and update the settings in the project configuration.

8. **Run the Application**:
   ```bash
   python main.py
   ```

---

## File Overview

### **main.py**
The core script that orchestrates the application’s functionality.  
**Responsibilities**:
- Configures logging with daily rotation.
- Ensures the `logs` folder exists.
- Manages threads for sending notifications and updating hydration logs.
- Opens another terminal to run `follow_latest_log.py`.
- Handles graceful shutdown using signal handling.

---

### **handlers/notification_handler.py**
Manages sending hydration reminders and notifications.  
**Responsibilities**:
- Sends desktop notifications via the `plyer` library.
- Sends email reminders using `channels/email_notification.py`.
- Sends WhatsApp messages using `channels/whatsapp_notification.py`.
- Prompts users to confirm water intake in the terminal.
- Logs hydration reminders and weekly goals to the database.

---

### **utils/db_utils.py**
Handles database interactions and provides a CLI for updating hydration logs.  
**Responsibilities**:
- Initializes the database and creates necessary tables.
- Fetches the last hydration log time and email log time.
- Logs hydration reminders and email statuses to the database.
- Checks and logs weekly hydration goals.
- Provides a CLI to update pending hydration logs.

---

### **channels/email_notification.py**
Handles sending email notifications.  
**Responsibilities**:
- Sends email reminders using the SMTP protocol.
- Logs the status of email notifications to the database.

---

### **channels/whatsapp_notification.py**
Handles sending WhatsApp notifications.  
**Responsibilities**:
- Sends WhatsApp messages using the `pywhatkit` library.
- Logs the status of WhatsApp notifications.

---

### **follow_latest_log.py**
Monitors logs dynamically.  
**Responsibilities**:
- Finds the latest log file based on creation time.
- Follows the latest log file, similar to `tail -f`.

---

## Example Usage

1. **Run the Application**:
   ```bash
   python main.py
   ```
2. **Follow Logs**:
   - The `main.py` script will automatically open another terminal and run `follow_latest_log.py` to monitor logs dynamically.

3. **Update Logs Using CLI**:
   ```bash
   python utils/db_utils.py
   ```
4. **Stop the Application**:
   - Use `Ctrl+C` to stop the script gracefully.

---

## Folder Structure

```
hydration/
├── channels/
│   ├── email_notification.py
│   └── whatsapp_notification.py
├── utils/
│   └── db_utils.py
├── follow_latest_log.py
├── main.py
└── handlers/
    └── notification_handler.py
```

---

## Summary
- `main.py`: Manages the application lifecycle, logging, and opens a terminal to follow logs.
- `notification_handler.py`: Sends reminders and logs hydration data.
- `db_utils.py`: Handles database interactions and provides a CLI.
- `email_notification.py`: Sends email notifications.
- `whatsapp_notification.py`: Sends WhatsApp notifications.
- `follow_latest_log.py`: Monitors logs dynamically.

This robust setup ensures smooth operation and easy tracking of your hydration habits.

