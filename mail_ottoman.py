# https://stackoverflow.com/questions/16512592/login-credentials-not-working-with-gmail-smtp
# mail atabilmek için verilen mail adresinin az güvenli uygulama moduna alınması gerekmektedir.

import logging
from datetime import datetime, timedelta
from os import getenv
import pymssql
import sys
from os import walk

from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText

import json

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart 
from os.path import basename

now = datetime.now()
yesterday = now - timedelta(days=1)

logger = logging.getLogger('automaticEmail')



email_config = {
    'server': getenv('MAIL_SMTP', 'smtp.gmail.com'),
    'port': int(getenv('MAIL_SMTP_PORT', 465)),
    'sender': getenv('MAIL_SENDER', 'ottoman.design.project2021@gmail.com'),
    'recepients': json.loads(getenv('MAIL_RECEPIENTS', '["n******@gmail.com"]')),
    'username': getenv('MAIL_SMTP_USER', 'o*********1@gmail.com'),
    'password': getenv('MAIL_SMTP_PASS', 'o********1')
}



def sendMail():
    # typical values for text_subtype are plain, html, xml
    text_subtype = 'plain'


    content=(f"""Yeni veriler ektedir.
                 İyi Çalışmalar.""")
              

    subject = "Osmanlıca Etiketlenmiş Veriler"

    try:
        # msg = MIMEText(content, text_subtype)
        msg = MIMEMultipart()

        msg.attach(MIMEText(content))


        _, _, filenames = next(walk("sendMail"))
        #dosya konumu uygulmaya göre düzenlenmeli

        # files = ["1.png","2.png"]
        for f in filenames or []:
            f = "sendMail/"+ f 
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)
            
        msg['Subject']= subject
        msg['From']   = email_config['sender']

        conn_mail = SMTP(email_config['server'], email_config['port'])

        conn_mail.set_debuglevel(False)
        conn_mail.login(email_config['username'], email_config['password'])
        
        try:
            conn_mail.sendmail(email_config['sender'], email_config['recepients'], msg.as_string())
            print("mail gönderimi başarılı")
        finally:
            conn_mail.quit()

    except:
        sys.exit( "mail failed CUSTOM_ERROR" ) 

