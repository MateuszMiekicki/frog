import smtplib
from email.mime.text import MIMEText
import logging


class Smtp():
    def __init__(self, host, port, user_name, password):
        logging.info(
            f"Initializing SMTP server. Host: {host}, Port: {port}, User: {user_name}")

        self.server = smtplib.SMTP(host, port)
        self.server.connect(host, port)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(user_name, password)

    def send_email(self, sender, recipient, subject, message):
        msg = MIMEText(message)

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        try:
            self.server.send_message(msg)
        except Exception as e:
            logging.error(f"Error sending email: {e}")

    def send_noreply_email(self, recipient, subject, message):
        self.send_email("noreply@smart-terrarium.com",
                        recipient, subject, message)
