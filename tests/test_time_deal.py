import time
import unittest
from app.commons.time_deal import millisecond_timestamp


class TestTimeDeal(unittest.TestCase):
    def test_time_deal(self):
        self.assertEqual(int(time.time()*1000), millisecond_timestamp())


if __name__ == '__main__':
    unittest.main(verbosity=1)  # 详细程度0，1，2
