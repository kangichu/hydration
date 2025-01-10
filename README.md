Here’s a coherent and structured version of the provided description:

---

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
3. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```
4. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
5. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Set Up the Database**:
   - Configure the MySQL database and update the settings in the project configuration.

7. **Run the Application**:
   ```bash
   python main.py
   ```

---

## File Overview

### **main.py**
The core script that orchestrates the application’s functionality.  
**Responsibilities**:
- Configures logging with daily rotation.
- Manages threads for sending notifications and updating hydration logs.
- Handles graceful shutdown using signal handling.

---

### **notification_handler.py**
Manages sending hydration reminders and notifications.  
**Responsibilities**:
- Sends desktop notifications via the `plyer` library.
- Sends email reminders.
- Prompts users to confirm water intake in the terminal.
- Logs hydration reminders and weekly goals to the database.

---

### **db_utils.py**
Provides database utility functions for interacting with hydration and email logs.  
**Responsibilities**:
- Initializes database tables.
- Fetches and logs hydration and email data.
- Includes a CLI to update pending hydration logs.

---

### **follow_latest_log.py**
Monitors the latest log file dynamically, similar to `tail -f`.  
**Responsibilities**:
- Identifies and follows the latest log file for real-time monitoring.

---

## Example Usage

1. **Run the Application**:
   ```bash
   python main.py
   ```
2. **Follow Logs**:
   ```bash
   python follow_latest_log.py
   ```
3. **Update Logs Using CLI**:
   ```bash
   python db_utils.py
   ```
4. **Stop the Application**:
   - Use `Ctrl+C` to stop the script gracefully.

---

## Summary
- `main.py`: Manages the application lifecycle and logging.  
- `notification_handler.py`: Sends reminders and logs hydration data.  
- `db_utils.py`: Handles database interactions and provides a CLI.  
- `follow_latest_log.py`: Monitors logs dynamically.  

This robust setup ensures smooth operation and easy tracking of your hydration habits.