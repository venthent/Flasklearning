import unittest
from flask_login import current_user
from Flasklearning.flaskyy.app import create_app,db
from flask import current_app
from Flasklearning.flaskyy.app.models import User


from flask import current_app,render_template
from threading import Thread
from Flasklearning.flaskyy.app import mail
from flask_mail import Message




class Email_test(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()


    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_email(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        def send_async_email(app, msg):
            with self.app_context:
                mail.send(msg)

        def send_email(subject, to, text, **kwargs):
            msg = Message(subject=subject, sender='1627237372@qq.com', recipients=[to])
            msg.body = text
            thr = Thread(target=send_async_email, args=[current_app, msg])
            thr.start()
            return thr

        u = User(email='wangjie@163.com', username='wangjie', password='1111')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        send_email(subject='Confirm your account', to='13533801264@163.com', text='Helo,test')

if __name__=="__main__":
    unittest.main()