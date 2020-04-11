from enum import Enum
import abc
from typing import Dict


class SearchEngine(abc.ABC):
    @abc.abstractmethod
    def query(self, query: str) -> Dict[int, float]:
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class EngineType(Enum):
    BINARY_SEARCH = "binary"
    VECTORIAL_SEARCH = "vectorial"

    def __str__(self) -> str:
        return self.value
