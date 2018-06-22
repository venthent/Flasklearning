import unittest
from Flasklearning.flaskyy.app.models import User

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u=User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        # 访问password时，我们期待抛出AttributeError：
        with self.assertRaises(AttributeError):
            u.password

    def test_password_vertify(self):
        u=User(password='cat')
        self.assertTrue(u.verity_password('cat'))
        self.assertTrue(u.verity_password('dog') is False)

    def test_password_salt_are_random(self):
        u1=User(password='cat')
        u2=User(password='cat')
        self.assertFalse(u1.password_hash==u2.password_hash)

#if __name__=="__main__":
 #   unittest.main()