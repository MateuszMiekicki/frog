import smtplib
from email.mime.text import MIMEText
import logging


class Smtp():
    def __connect(self):
        self.server.connect(self.host, self.port)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.user_name, self.password)

    def __init__(self, host, port, user_name, password):
        logging.info(
            f"Initializing SMTP server. Host: {host}, Port: {port}, User: {user_name}")
        self.host = host
        self.port = port
        self.user_name = user_name
        self.password = password

        self.server = smtplib.SMTP(host, port)

    def __is_connected(self):
        try:
            status = self.server.noop()[0]
        except Exception:
            status = -1
        return True if status == 250 else False

    def send_email(self, sender, recipient, subject, message):
        msg = MIMEText(message)

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        self.__connect()
        if not self.__is_connected():
            self.server.connect()
            self.server.ehlo()
            self.server.starttls()
            self.server.login(sender, password)
        try:
            self.server.send_message(msg)
        except Exception as e:
            logging.error(f"Error sending email: {e}")
        finally:
            self.server.quit()

    def send_noreply_email(self, recipient, subject, message):
        self.send_email("noreply@smart-terrarium.com",
                        recipient, subject, message)
