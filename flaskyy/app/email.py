from flask import current_app,render_template
from threading import Thread
from Flasklearning.flaskyy.app import mail
from flask_mail import Message


def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject,to,template,**kwargs):
    msg=Message(subject=subject,sender='1627237372@qq.com',recipients=[to])
    msg.html=render_template(template+'.html',**kwargs)
    thr=Thread(target='send_async_email',args=[current_app,msg])
    thr.start()
    return thr


