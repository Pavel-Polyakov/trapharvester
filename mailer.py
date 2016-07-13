# It's copied from stackoverflow
# http://stackoverflow.com/questions/6270782/how-to-send-an-email-with-python

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import MAIL_FROM

def send_mail(subject,to_address,text):
    if type(to_address) != list:
        to_address = [to_address]
    for address in to_address:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = MAIL_FROM
        msg['To'] = address
        part1 = MIMEText(text.encode('utf-8'), 'html', 'utf-8')
        msg.attach(part1)
        server = smtplib.SMTP('localhost')
        server.sendmail(MAIL_FROM,address,msg.as_string())
        server.close()

