#  import unittest
from unittest import TestCase
import os
from . import util


class TestLastLine(TestCase):
    def setUp(self):
        self._filename = "test_last_line.txt"
        with open(self._filename, "w+") as f:
            f.write("#id;utc;jamInd;lat;lon\n")
            f.write("1;2017-08-17 23:57:15;4;-1;-1\n")
            f.write("2;2017-08-17 23:57:16;4;63.4078222;10.4283095\n")
            f.write("3;2017-08-17 23:57:17;4;63.4078224;10.4283088\n")
            f.write("4;2017-08-17 23:57:18;4;63.407822599999996;10.4283086\n")
            f.write("5;2017-08-17 23:57:19;4;63.407822499999995;10.4283086\n")
            f.write("6;2017-08-17 23:57:20;3;63.4078215;10.428308699999999\n")
            f.write("7;2017-08-17 23:57:21;4;63.407820799999996;10.4283088\n")

    def test_actual_last_line(self):
        result = util.last_line(self._filename)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, bytes)

    def test_handling_bad_filename(self):
        result = util.last_line("asdfdgdfgersdfghfdsgdsdf.txt")
        self.assertIsNone(result)

    def tearDown(self):
        if os.path.exists(self._filename):
            os.remove(self._filename)
