from enum import Enum
import abc
from typing import Dict


class EngineType(Enum):
    BINARY_SEARCH = "binary"
    VECTORIAL_SEARCH = "vectorial"

    def __str__(self) -> str:
        return self.value


class DocumentPonderation(Enum):
    BINARY = "binary"
    TF = "tf"
    FREQUENCY_NORMALIZED = "frequency-normalized"
    LOG = "log"
    LOG_NORMALIZED = "log-normalized"

    def __str__(self) -> str:
        return self.value


class TermPonderation(Enum):
    NONE = "none"
    IDF = "idf"
    NORMALIZED = "normalized"

    def __str__(self) -> str:
        return self.value


class SearchEngine(abc.ABC):
    @abc.abstractmethod
    def query(self, query: str) -> Dict[int, float]:
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def set_document_ponderation(self, ponderation: DocumentPonderation):
        raise NotImplementedError

    @abc.abstractmethod
    def set_term_ponderation(self, ponderation: TermPonderation):
        raise NotImplementedError

    @abc.abstractmethod
    def type(self) -> str:
        raise NotImplementedError
