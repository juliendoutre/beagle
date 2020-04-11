import pytest
from beagle.binary_search_engine import merge, exclude, intersect


class TestMerge:
    def test_one_empty_list(self):
        assert merge([], [1, 2, 3]) == [1, 2, 3]

    def test_both_empty_list(self):
        assert merge([], []) == []

    def test_full_lists(self):
        assert sorted(merge([1, 6, 3], [2, 4, 5])) == [1, 2, 3, 4, 5, 6]


class TestIntersect:
    def test_one_empty_list(self):
        assert intersect([], [1, 2, 3]) == []

    def test_both_empty_list(self):
        assert intersect([], []) == []

    def test_full_lists(self):
        assert intersect([1, 2, 3], [2, 3, 4, 5]) == [2, 3]


class TestExclude:
    def test_one_empty_list(self):
        assert exclude([1, 2, 3], []) == [1, 2, 3]

    def test_both_empty_list(self):
        assert exclude([], []) == []

    def test_full_lists(self):
        assert exclude([2, 3, 4, 5], [1, 2, 3]) == [4, 5]
