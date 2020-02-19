from enum import Enum
from beagle.logging import timer
from beagle.index import InvertedIndex


class EngineType(Enum):
    BINARY_SEARCH = "binary"

    def __str__(self) -> str:
        return self.value


class BinarySearchEngine:
    def __init__(self, index: InvertedIndex) -> None:
        pass

    @timer
    def query(self, query: str) -> None:
        return None
