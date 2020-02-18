from typing import Dict, Optional, List
from enum import Enum
import json
import abc


class InvertedIndexTypes(Enum):
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
        self.ids: List[int] = []


class DocumentsInvertedIndex(InvertedIndex):
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

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self, f, default=lambda x: x.__dict__)
