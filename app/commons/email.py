from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail


# def send_async_email(app, msg):
#     with app.app_context():
#         mail.send(msg)
#
#
# def send_email(to, subject, template, **kwargs):
#     app = current_app._get_current_object()
#     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
#                   sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs)
#     msg.html = render_template(template + '.html', **kwargs)
#     thr = Thread(target=send_async_email, args=[app, msg])
#     thr.start()
#     return thr


def send_mail(recipients, subject, body):  # 接收者邮箱，邮件主题，内容
    if not isinstance(recipients, list):
        recipients = [recipients]
    sender = current_app.config['MAIL_USERNAME']
    message = Message(subject, sender=sender, recipients=recipients)
    message.html = body
    mail.send(message)
    return True

