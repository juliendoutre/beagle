from typing import Dict, Optional, List, Tuple, Any
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


class InvertedIndex:
    def __init__(self, index_type: InvertedIndexType) -> None:
        self.entries: Dict[str, Any] = {}
        self.type: InvertedIndexType = index_type

    def update(self, index: "InvertedIndex") -> None:
        for term in index.entries:
            if term in self.entries:
                self.entries[term][0] += index.entries[term][0]
                self.entries[term][1] += index.entries[term][1]
            else:
                self.entries[term] = index.entries[term]

    @timer
    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump({"type": self.type.value, "entries": self.entries}, f)


@timer
def load_index(path: str) -> InvertedIndex:
    with open(path, "r") as f:
        raw = json.load(f)
        index = InvertedIndex(raw["type"])
        index.entries = raw["entries"]
        return index
