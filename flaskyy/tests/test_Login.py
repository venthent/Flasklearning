import unittest
from Flasklearning.flaskyy.app import create_app,db
from Flasklearning.flaskyy.app.models import User



class LoginTest(unittest.TestCase):

    def setUp(self):
        self.app=create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()#Why must have context?
        db.create_all()
        u = User(email='wangjie@163.com', username='wangjie', password='1111')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        u1=User.query.filter_by(username='wangjie').first()
        self.assertTrue(u1 is not None)


#if __name__=="__main__":
 #   unittest.main()
