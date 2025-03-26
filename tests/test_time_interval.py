import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))
from time_interval import add_interval

class TestAddInterval(unittest.TestCase):
    def test_basic_overlap(self):
        intervals = [["01-01-2024", "10-01-2024"], ["15-01-2024", "20-01-2024"]]
        expected = [["01-01-2024", "10-01-2024"], ["15-01-2024", "25-01-2024"]]
        self.assertEqual(add_interval(intervals, "17-01-2024", "25-01-2024"), expected)

    def test_no_overlap(self):
        intervals = [["01-03-2024", "05-01-2024"], ["10-01-2024", "15-01-2024"]]
        expected = [["01-01-2024", "05-01-2024"], ["10-01-2024", "15-01-2024"], ["17-01-2024", "19-01-2024"]]
        self.assertEqual(add_interval(intervals, "17-01-2024", "19-01-2024"), expected)

    def test_new_inside_existing(self):
        intervals = [["01-01-2024", "10-01-2024"]]
        expected = [["01-01-2024", "01-07-2024"]]
        self.assertEqual(add_interval(intervals, "03-01-2024", "01-07-2024"), expected)

    def test_new_covers_existing(self):
        intervals = [["05-01-2024", "10-01-2024"]]
        expected = [["01-01-2024", "15-01-2024"]]
        self.assertEqual(add_interval(intervals, "01-01-2024", "15-01-2024"), expected)

    def test_exact_match(self):
        intervals = [["05-01-2024", "10-01-2024"]]
        expected = [["05-01-2024", "10-01-2024"]]
        self.assertEqual(add_interval(intervals, "05-01-2024", "10-01-2024"), expected)

    def test_adjacent_merge(self):
        intervals = [["01-01-2024", "10-01-2024"], ["11-01-2024", "20-01-2024"]]
        expected = [["01-01-2024", "20-01-2024"]]
        self.assertEqual(add_interval(intervals, "10-01-2024", "11-01-2024"), expected)

    def test_bridge_merge(self):
        intervals = [["01-01-2024", "15-01-2024"]]  
        expected = [["01-01-2024", "15-01-2024"]]
        self.assertEqual(add_interval(intervals, "04-01-2024", "11-01-2024"), expected)

    def test_empty_list(self):
        intervals = []
        expected = [["01-01-2024", "10-01-2024"]]
        self.assertEqual(add_interval(intervals, "01-01-2024", "10-01-2024"), expected)

    def test_single_non_overlapping(self):
        intervals = [["01-01-2024", "10-01-2024"]]
        expected = [["01-01-2024", "10-01-2024"], ["15-01-2024", "20-01-2024"]]
        self.assertEqual(add_interval(intervals, "15-01-2024", "20-01-2024"), expected)

    def test_multiple_merging(self):
        intervals = [["01-01-2024", "05-01-2024"], ["03-01-2024", "01-07-2024"], ["01-06-2024", "01-12-2024"]]
        expected = [["01-01-2024", "01-12-2024"]]
        self.assertEqual(add_interval(intervals, "05-01-2024", "15-06-2024"), expected)

if __name__ == "__main__":
    unittest.main()
