import smtplib
from email.mime.text import MIMEText


class Smtp():
    def __init__(self, host, port, user_name, password):
        self.user_name = user_name
        self.password = password
        self.server = smtplib.SMTP(host, port)

    def send_email(self, sender, recipient, subject, message):
        msg = MIMEText(message)

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        self.server.connect()
        # self.server.starttls()
        self.server.login(self.user_name, self.password)
        try:
            self.server.send_message(msg)
        finally:
            self.server.close()

    def send_noreply_email(self, recipient, subject, message):
        self.send_email("noreply@smart-terrarium.com",
                        recipient, subject, message)

    def __del__(self):
        self.server.quit()
