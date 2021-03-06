from typing import Dict, Any, List
from beagle.logging import timer
from enum import Enum
import json
import os


class InvertedIndexType(Enum):
    DOCUMENTS_INDEX = "documents"
    FREQUENCIES_INDEX = "frequencies"
    POSITIONS_INDEX = "positions"

    def __str__(self) -> str:
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
        dirpath = os.path.dirname(path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        with open(path, "w") as f:
            json.dump({"type": self.type.value, "entries": self.entries}, f)


@timer
def load_index(path: str) -> InvertedIndex:
    with open(path, "r") as f:
        raw = json.load(f)
        index = InvertedIndex(raw["type"])
        index.entries = raw["entries"]
    return index


class DocIndex:
    def __init__(self) -> None:
        self.entries: Dict[str, Any] = {}

    @timer
    def save(self, path: str) -> None:
        dirpath = os.path.dirname(path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        with open(path, "w") as f:
            return json.dump(self.entries, f)

    def format_results(self, results: Dict[int, float]) -> List[str]:
        formatted_results: List[str] = []

        for doc_id, score in results.items():
            doc = self.entries[str(doc_id)]
            formatted_results.append(f"{doc['name']}: {score} ({doc['path']})")

        return formatted_results


@timer
def load_doc_index(path: str) -> DocIndex:
    with open(path, "r") as f:
        raw = json.load(f)
        index = DocIndex()
        index.entries = raw
    return index
