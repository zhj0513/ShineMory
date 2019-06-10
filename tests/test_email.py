import time
import unittest

from app import create_app, db
from app.commons.email import send_mail


class TestEmail(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_email(self):
        self.assertEqual(True, send_mail('1264728987@qq.com', '测试', '测试'))


if __name__ == '__main__':
    unittest.main(verbosity=1)  # 详细程度0，1，2
