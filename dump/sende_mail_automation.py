from email.message import EmailMessage
import ssl
import smtplib
from templates import create_mail_template
def send_mail(user_id, name, gender, password, mail):
    email_sender = "srishti.ai.arnab.ashish.tasir@gmail.com"
    email_password = "jpouxzgtxjdzwysz"
    email_receiver = mail

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = "Registration for SRISHTI: Speech Recognition Internal System Host Technical Intelligent"
    em.set_content(create_mail_template(user_id, name, password))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    return True
# user_id = "123456789"
# name = "Alen"
# gender = "Male"
# password = "123456"
# mail = "arnabmondal203@gmail.com"
#
# send_mail(user_id, name, gender, password, mail)