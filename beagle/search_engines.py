from enum import Enum
import abc
from typing import List


class SearchEngine(abc.ABC):
    @abc.abstractmethod
    def query(self, query: str) -> List[int]:
        raise NotImplementedError


class EngineType(Enum):
    BINARY_SEARCH = "binary"
    VECTORIAL_SEARCH = "vectorial"

    def __str__(self) -> str:
        return self.value
