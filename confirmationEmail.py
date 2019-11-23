from flask_mail import Message
from application import app, mail
import threading


def send_async_email(msg):
    with app.app_context():
        mail.send(msg)
 
 
def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = threading.Thread(target=send_async_email, args=[msg])
    thr.start()

