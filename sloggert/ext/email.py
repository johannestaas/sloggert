'''
sloggert.ext.email
==================

Email alerter.
'''
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from ..alert import Alerter
from ..config import CONF


class EmailAlerter(Alerter):

    def init_email(self, subject=None, sender=None, recipients=None,
                   header=None, footer=None, host=None, username=None,
                   password=None):
        self.subject = subject or CONF.get(
            'EMAIL_SUBJECT', '{s.name} Alerts'.format(s=self).title())
        self.email_text = ''
        self.header_text = header or CONF.get('EMAIL_HEADER', 'alerts\n======')
        self.footer_text = footer or CONF.get('EMAIL_FOOTER', '')
        self.sender = sender or CONF.get('EMAIL_SENDER')
        self.recipients = recipients or CONF.get('EMAIL_RECIPIENTS')
        self.email_host = host or CONF.get('EMAIL_HOST', 'smtp.gmail.com')
        self.username = username or CONF.get('EMAIL_USERNAME')
        self.password = password or CONF.get('EMAIL_PASSWORD')

    def add_to_email(self, name):
        if isinstance(name, str):
            for proc in self.process(name):
                self.email_text += proc + '\n'
        else:
            for n in name:
                for proc in self.process(n):
                    self.email_text += proc + '\n'

    def send_email(self, text_type='plain', username=None, password=None,
                   recipients=None):
        email_text = '\n'.join([self.header_text, self.email_text,
                                self.footer_text])
        msg = MIMEText(email_text, text_type)
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        conn = SMTP_SSL(self.email_host)
        conn.set_debuglevel(False)
        username = username or self.username
        password = password or self.password
        if not any([username, password]):
            raise ValueError('Must supply username and password to send email.')
        conn.login(username, password)
        recipients = recipients or self.recipients
        try:
            conn.sendmail(self.sender, recipients, msg.as_string())
        finally:
            conn.quit()
        return msg
