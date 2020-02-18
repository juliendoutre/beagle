from typing import Dict, Optional, List, Tuple
from beagle.logging import timer
from enum import Enum
import json
import abc


class InvertedIndexType(Enum):
    DOCUMENTS_INDEX = "documents"
    FREQUENCIES_INDEX = "frequencies"
    POSITIONS_INDEX = "positions"

    def __str__(self):
        return self.value


class InvertedIndexEntry(abc.ABC):
    pass


class InvertedIndex(abc.ABC):
    @abc.abstractmethod
    def update(self, index: "InvertedIndex") -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, term: str) -> Optional[InvertedIndexEntry]:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, path: str) -> None:
        raise NotImplementedError


class DocumentsInvertedIndexEntry(InvertedIndexEntry):
    def __init__(self, id: int) -> None:
        self.frequency: int = 1
        self.ids: List[int] = [id]


class DocumentsInvertedIndex(InvertedIndex):
    index_type: InvertedIndexType = InvertedIndexType.DOCUMENTS_INDEX

    def __init__(self) -> None:
        self.entries: Dict[str, DocumentsInvertedIndexEntry] = {}

    def get(self, term: str) -> Optional[DocumentsInvertedIndexEntry]:
        return self.entries.get(term)

    def update(self, index: "DocumentsInvertedIndex") -> None:
        for term in index.entries:
            if term in self.entries:
                self.entries[term].frequency += index.entries[term].frequency
                self.entries[term].ids += index.entries[term].ids
            else:
                self.entries[term] = index.entries[term]

    @timer
    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self, f, default=lambda x: x.__dict__)


class FrequenciesInvertedIndexEntry(InvertedIndexEntry):
    def __init__(self, id: int, f: int) -> None:
        self.frequency: int = 1
        self.ids: List[Tuple[int, int]] = [(id, f)]


class FrequenciesInvertedIndex(InvertedIndex):
    index_type: InvertedIndexType = InvertedIndexType.FREQUENCIES_INDEX

    def __init__(self) -> None:
        self.entries: Dict[str, FrequenciesInvertedIndexEntry] = {}

    def get(self, term: str) -> Optional[FrequenciesInvertedIndexEntry]:
        return self.entries.get(term)

    def update(self, index: "FrequenciesInvertedIndex") -> None:
        for term in index.entries:
            if term in self.entries:
                self.entries[term].frequency += index.entries[term].frequency
                self.entries[term].ids += index.entries[term].ids
            else:
                self.entries[term] = index.entries[term]

    @timer
    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self, f, default=lambda x: x.__dict__)


class PositionsInvertedIndexEntry(InvertedIndexEntry):
    def __init__(self, id: int, f: int, positions: List[int]) -> None:
        self.frequency: int = 1
        self.ids: List[Tuple[int, int, List[int]]] = [(id, f, positions)]


class PositionsInvertedIndex(InvertedIndex):
    index_type: InvertedIndexType = InvertedIndexType.POSITIONS_INDEX

    def __init__(self) -> None:
        self.entries: Dict[str, PositionsInvertedIndexEntry] = {}

    def get(self, term: str) -> Optional[PositionsInvertedIndexEntry]:
        return self.entries.get(term)

    def update(self, index: "PositionsInvertedIndex") -> None:
        for term in index.entries:
            if term in self.entries:
                self.entries[term].frequency += index.entries[term].frequency
                self.entries[term].ids += index.entries[term].ids
            else:
                self.entries[term] = index.entries[term]

    @timer
    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self, f, default=lambda x: x.__dict__)
