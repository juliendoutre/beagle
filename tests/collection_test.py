import pytest
from beagle.collection import Document


class TestDocumentFiltering:
    def test_empty_list(self):
        doc = Document("", "", 0)
        doc.tokens = [str(i) for i in range(10)]

        doc.filter([])
        assert doc.tokens == [str(i) for i in range(10)]

    def test_full_list(self):
        doc = Document("", "", 0)
        doc.tokens = [str(i) for i in range(10)]

        doc.filter([str(i) for i in range(5)])
        assert doc.tokens == [str(i) for i in range(5, 10)]


class TestDocumentStats:
    def test_only_unique_terms(self):
        doc = Document("", "", 0)
        doc.tokens = [str(i) for i in range(10)]
        assert doc.stats() == {
            "max_frequency": 1,
            "sum_frequency": 10,
            "unique_terms_number": 10,
            "tokens_number": 10,
        }

    def test_without_unique_terms(self):
        doc = Document("", "", 0)
        doc.tokens = [str(1)] * 10 + [str(2)] * 6
        assert doc.stats() == {
            "max_frequency": 10,
            "sum_frequency": 16,
            "unique_terms_number": 0,
            "tokens_number": 16,
        }


def test_document_vocabulary():
    doc = Document("", "", 0)
    doc.tokens = [str(1)] * 10 + [str(2)] * 6 + [str(4)]
    assert doc.get_vocabulary() == set(str(a) for a in [1, 2, 4])


def test_document_term_positions():
    doc = Document("", "", 0)
    doc.tokens = [str(a) for a in [1, 3, 1, 2, 4, 2, 1]]
    assert doc.term_positions() == {
        "1": [3, [0, 2, 6]],
        "2": [2, [3, 5]],
        "3": [1, [1]],
        "4": [1, [4]],
    }
