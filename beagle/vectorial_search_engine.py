from beagle.logging import timer
from beagle.index import InvertedIndex
from beagle.search_engines import SearchEngine, EngineType
from nltk.stem import WordNetLemmatizer
from enum import Enum
from beagle.stats import Stats
from typing import List, Dict
import math


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


class VectorialSearchEngine(SearchEngine):
    def __init__(
        self,
        index: InvertedIndex,
        stats: Stats,
        threshold: int,
        document_ponderation: DocumentPonderation = DocumentPonderation.TF,
        term_ponderation: TermPonderation = TermPonderation.NONE,
    ) -> None:
        self.index: InvertedIndex = index
        self.stats: Stats = stats
        self.document_ponderation = document_ponderation
        self.term_ponderation = term_ponderation
        self.threshold: int = threshold

    def tf(self, term: str, id: int) -> int:
        docs = self.index.entries[term][1]
        for d in docs:
            if d[0] == id:
                return d[1]
        return 0

    def fn_tf(self, term: str, id: int) -> float:
        return 0.5 + 0.5 * self.tf(term, id) / self.stats.documents[id]["max_frequency"]

    def log_tf(self, term: str, id: int) -> float:
        tf = self.tf(term, id)
        if tf > 0:
            return 1 + math.log(tf)
        return 0

    def log_fn_tf(self, term: str, id: int) -> float:
        avg = self.stats[id]["summed_frequency"] / self.stats[id]["unique_terms_number"]
        return self.log_tf(term, id) / (1 + math.log(avg))

    def idf(self, term: str) -> float:
        return math.log(self.stats.documents_number / self.index[term][0])

    def process_query(self, query: str) -> List[str]:
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token.lower()) for token in query.split()]

    def compute_query(self, query: List[str]) -> Dict[int, float]:
        scores: Dict[int, float] = {}

        for query_term in query:
            try:
                docs = [d[0] for d in self.index.entries[query_term][1]]
            except Exception:
                docs = []

            for d in docs:
                if d in scores:
                    scores[d] += self.tf(query_term, d)
                else:
                    scores[d] = self.tf(query_term, d)

        return scores

    @timer
    def query(self, query: str) -> Dict[int, float]:
        return {
            d[0]: d[1]
            for d in list(
                {
                    k: v
                    for k, v in sorted(
                        self.compute_query(self.process_query(query)).items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                }.items()
            )[: self.threshold]
        }

    def __str__(self) -> str:
        return f"{EngineType.VECTORIAL_SEARCH.value} ({self.document_ponderation}, {self.term_ponderation})"
