class SMTPServer():
    def __init__(self, smtp_host, smtp_port, smtp_username, smtp_password, sender_email):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
