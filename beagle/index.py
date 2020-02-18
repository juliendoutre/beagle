from typing import Dict, Optional, List


class InvertedIndexEntry:
    def __init__(self, id: int) -> None:
        self.frequency: int = 1
        self.ids: List[int] = []


class InvertedIndex:
    def __init__(self) -> None:
        self.entries: Dict[str, InvertedIndexEntry] = {}

    def get(self, term: str) -> Optional[InvertedIndexEntry]:
        return self.entries.get(term)

    def update(self, index: "InvertedIndex") -> None:
        for term in index.entries:
            if term in self.entries:
                self.entries[term].frequency += index.entries[term].frequency
                self.entries[term].ids += index.entries[term].ids
            else:
                self.entries[term] = index.entries[term]
