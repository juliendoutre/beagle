import pytest
from beagle.stats import Stats


class TestStatsUpdate:
    def test_both_empty_update(self):
        stats = Stats()
        stats.update(Stats())

        assert len(stats.documents) == 0

    def test_one_empty_update(self):
        stats = Stats()
        initial_stats = {
            "1": [3, [0, 2, 6]],
            "2": [2, [3, 5]],
            "3": [1, [1]],
            "4": [1, [4]],
        }
        stats.documents[0] = initial_stats
        stats.update(Stats())

        assert len(stats.documents) == 1
        assert stats.documents[0] == initial_stats

    def test_one_document_to_update(self):
        stats1 = Stats()
        stats2 = Stats()

        stats1.documents[0] = {"1": [3, [0, 2, 6]], "2": [2, [3, 5]]}
        stats2.documents[1] = {"3": [1, [1]], "4": [1, [4]]}

        stats1.update(stats2)

        assert len(stats1.documents) == 2
        assert stats1.documents[0] == {"1": [3, [0, 2, 6]], "2": [2, [3, 5]]}
        assert stats1.documents[1] == {"3": [1, [1]], "4": [1, [4]]}
