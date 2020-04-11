import pytest
from beagle.index import InvertedIndex, InvertedIndexType
from beagle.collection import Shard, Document


class TestIndexUpdate:
    def test_both_empty_index(self):
        idx = InvertedIndex(InvertedIndexType.DOCUMENTS_INDEX)
        idx.update(InvertedIndex(InvertedIndexType.DOCUMENTS_INDEX))
        assert len(idx.entries) == 0

    def test_one_empty_index(self):
        idx = InvertedIndex(InvertedIndexType.DOCUMENTS_INDEX)
        idx.entries = {"1": [3, [1, 2, 3]], "2": [4, [4, 3, 2, 1]]}

        idx.update(InvertedIndex(InvertedIndexType.DOCUMENTS_INDEX))
        assert idx.entries == {"1": [3, [1, 2, 3]], "2": [4, [4, 3, 2, 1]]}

    def test_full_indexes(self):
        idx1 = InvertedIndex(InvertedIndexType.DOCUMENTS_INDEX)
        idx1.entries = {"1": [3, [1, 2, 3]], "2": [4, [4, 3, 2, 1]]}

        idx2 = InvertedIndex(InvertedIndexType.DOCUMENTS_INDEX)
        idx2.entries = {"2": [2, [8, 7]], "3": [4, [4, 3, 2, 1]]}

        idx1.update(idx2)

        assert idx1.entries == {
            "1": [3, [1, 2, 3]],
            "2": [6, [4, 3, 2, 1, 8, 7]],
            "3": [4, [4, 3, 2, 1]],
        }


class TestIndexing:
    def test_document_index(self):
        doc0 = Document("", "", 0)
        doc0.tokens = ["0", "1", "2"]

        doc1 = Document("", "", 1)
        doc1.tokens = ["3", "4", "2", "2", "2"]

        doc2 = Document("", "", 2)
        doc2.tokens = ["5"]

        doc3 = Document("", "", 3)
        doc3.tokens = ["3", "3"]

        s = Shard("", "")
        s.documents = [doc0, doc1, doc2, doc3]

        assert s.index(InvertedIndexType.DOCUMENTS_INDEX).entries == {
            "0": [1, [0]],
            "1": [1, [0]],
            "2": [2, [0, 1]],
            "3": [2, [1, 3]],
            "4": [1, [1]],
            "5": [1, [2]],
        }

    def test_frequencies_index(self):
        doc0 = Document("", "", 0)
        doc0.tokens = ["0", "1", "2"]

        doc1 = Document("", "", 1)
        doc1.tokens = ["3", "4", "2", "2", "2"]

        doc2 = Document("", "", 2)
        doc2.tokens = ["5"]

        doc3 = Document("", "", 3)
        doc3.tokens = ["3", "3"]

        s = Shard("", "")
        s.documents = [doc0, doc1, doc2, doc3]

        assert s.index(InvertedIndexType.FREQUENCIES_INDEX).entries == {
            "0": [1, [(0, 1)]],
            "1": [1, [(0, 1)]],
            "2": [2, [(0, 1), (1, 3)]],
            "3": [2, [(1, 1), (3, 2)]],
            "4": [1, [(1, 1)]],
            "5": [1, [(2, 1)]],
        }

    def test_positions_index(self):
        doc0 = Document("", "", 0)
        doc0.tokens = ["0", "1", "2"]

        doc1 = Document("", "", 1)
        doc1.tokens = ["3", "4", "2", "2", "2"]

        doc2 = Document("", "", 2)
        doc2.tokens = ["5"]

        doc3 = Document("", "", 3)
        doc3.tokens = ["3", "3"]

        s = Shard("", "")
        s.documents = [doc0, doc1, doc2, doc3]

        assert s.index(InvertedIndexType.POSITIONS_INDEX).entries == {
            "0": [1, [(0, 1, [0])]],
            "1": [1, [(0, 1, [1])]],
            "2": [2, [(0, 1, [2]), (1, 3, [2, 3, 4])]],
            "3": [2, [(1, 1, [0]), (3, 2, [0, 1])]],
            "4": [1, [(1, 1, [1])]],
            "5": [1, [(2, 1, [0])]],
        }
