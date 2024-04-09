from unittest import TestCase
from time import sleep
from k_means_utils import *


class TestGetAveragePixel(TestCase):
    # Should calculate correct averages with rounding for random set of pixels
    def test_get_average_pixel(self):
        # NB (x, y) coord part of tuple does not matter
        cluster = [((0, 0), (0, 0, 0)), ((0, 0), (174, 4, 6)),
                   ((0, 0), (255, 255, 255)), ((0, 0), (81, 160, 37)),
                   ((0, 0), (149, 156, 182)), ((0, 0), (13, 77, 122)),
                   ((0, 0), (244, 133, 47)), ((0, 0), (4, 132, 78)),
                   ((0, 0), (25, 206, 114)), ((0, 0), (44, 32, 13))]
        expected_average_pixel = (99, 116, 85)
        actual_average_pixel = get_average_pixel(cluster)
        self.assertEqual(expected_average_pixel, actual_average_pixel)

    # Should raise ZeroDivisionError when cluster contains no pixels
    def test_empty_cluster(self):
        cluster = []
        self.assertRaises(ZeroDivisionError, get_average_pixel, cluster)


class TestCompareTupleLists(TestCase):
    # Should return true for identical tuple lists (same content, same order)
    def test_same_lists_comparison(self):
        tuple_list1 = [(123, 24, 13), (0, 0, 0), (255, 255, 255)]
        tuple_list2 = [(123, 24, 13), (0, 0, 0), (255, 255, 255)]
        self.assertEqual(compare_tuple_lists(tuple_list1, tuple_list2), True)

    # Should return false for different tuple content
    def test_different_tuple_content(self):
        tuple_list1 = [(123, 24, 13), (0, 0, 0), (255, 255, 255)]
        tuple_list2 = [(123, 24, 13), (0, 0, 1), (255, 255, 255)]
        self.assertEqual(compare_tuple_lists(tuple_list1, tuple_list2), False)

    # Should return false for different number of tuples
    def test_different_length(self):
        tuple_list1 = [(123, 24, 13), (0, 0, 0), (255, 255, 255)]
        tuple_list2 = [(123, 24, 13), (0, 0, 0)]
        self.assertEqual(compare_tuple_lists(tuple_list1, tuple_list2), False)

    # Should return false for tuples in different order
    def test_different_order(self):
        tuple_list1 = [(123, 24, 13), (0, 0, 0), (255, 255, 255)]
        tuple_list2 = [(123, 24, 13), (255, 255, 255), (0, 0, 0)]
        self.assertEqual(compare_tuple_lists(tuple_list1, tuple_list2), False)


class TestGetTimestampStr(TestCase):
    # Should generate timestamp strings that are sortable (i.e. earlier strings come first)
    def test_timestamp_str_sortable(self):
        time_str1 = get_timestamp_str()
        sleep(2)
        time_str2 = get_timestamp_str()
        sleep(2)
        time_str3 = get_timestamp_str()
        str_list = [time_str1, time_str2, time_str3]
        self.assertEqual(str_list, sorted(str_list))
