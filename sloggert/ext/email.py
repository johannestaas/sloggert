'''
sloggert.ext.email
==================

Email alerter.
'''
import smtplib
from email.mime.text import MIMEText


def send_email(subject, messages):
    msg['Subject'] = '
    msg['From'] = me
    msg['To'] = you
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
