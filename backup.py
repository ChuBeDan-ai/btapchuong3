import os
import shutil
import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import schedule
import time

# Load environment variables from .env file
load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
BACKUP_FOLDER = os.getenv("BACKUP_FOLDER")
DATABASE_FOLDER = os.getenv("DATABASE_FOLDER")

def send_email(subject, body):
    """Sends an email notification."""
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        server.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def backup_database():
    """Backups .sql and .sqlite3 database files."""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_FOLDER, timestamp)
    os.makedirs(backup_path, exist_ok=True)
    backup_successful = False
    backed_up_files = []

    try:
        for filename in os.listdir(DATABASE_FOLDER):
            if filename.endswith(".sql") or filename.endswith(".sqlite3"):
                source_path = os.path.join(DATABASE_FOLDER, filename)
                destination_path = os.path.join(backup_path, filename)
                shutil.copy2(source_path, destination_path) # copy2 preserves metadata
                backed_up_files.append(filename)
        if backed_up_files:
            backup_successful = True
            subject = "Backup Database Thành Công"
            body = f"Các file database sau đã được backup thành công vào lúc {now}:\n" + "\n".join(backed_up_files)
        else:
            subject = "Không Tìm Thấy File Database"
            body = "Không tìm thấy file database (.sql hoặc .sqlite3) nào để backup."

    except Exception as e:
        subject = "Backup Database Thất Bại"
        body = f"Đã xảy ra lỗi trong quá trình backup database: {e}"

    send_email(subject, body)
    print(f"Backup completed at {now}. Successful: {backup_successful}")

def schedule_backup():
    """Schedules the backup to run every 10 seconds (for testing)."""
    schedule.every(10).seconds.do(backup_database)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Create the backup folder if it doesn't exist
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    schedule_backup()
