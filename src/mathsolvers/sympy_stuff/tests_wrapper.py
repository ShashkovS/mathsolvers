import unittest
from mathsolvers import math_worker


def tnesc(name):
    return name.replace('/', '⁄').replace('\\', '⑊')


_to_spreadsheet = ['task\tstep\taction\tsolution\tanswer\tfinal_answer']


class TestSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worker = math_worker.MathWorker()

    @classmethod
    def tearDownClass(cls):
        cls.worker.shutdown()
