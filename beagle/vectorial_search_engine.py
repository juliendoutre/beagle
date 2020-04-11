from beagle.logging import timer
from beagle.index import InvertedIndex
from beagle.search_engines import (
    SearchEngine,
    EngineType,
    DocumentPonderation,
    TermPonderation,
)
from nltk.stem import WordNetLemmatizer
from enum import Enum
from beagle.stats import Stats
from typing import List, Dict
import math


class VectorialSearchEngine(SearchEngine):
    def __init__(
        self,
        index: InvertedIndex,
        stats: Stats,
        threshold: int,
        document_ponderation: DocumentPonderation = DocumentPonderation.TF,
        term_ponderation: TermPonderation = TermPonderation.NONE,
        query_ponderation: DocumentPonderation = DocumentPonderation.TF,
        query_term_ponderation: TermPonderation = TermPonderation.NONE,
    ) -> None:
        self.index: InvertedIndex = index
        self.stats: Stats = stats
        self.document_ponderation = document_ponderation
        self.term_ponderation = term_ponderation
        self.query_ponderation = query_ponderation
        self.query_term_ponderation = query_term_ponderation
        self.threshold: int = threshold

    # ponderation functions that depends on a document and a term
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

    # ponderation functions that depend only on a term
    def idf(self, term: str) -> float:
        return math.log(self.stats.documents_number / self.index[term][0])

    def normalized(self, term: str) -> float:
        return max(
            0,
            (self.stats.documents_number - self.index[term][0])
            / self.stats.documents_number,
        )

    # helping functions to get a vector of weights from a querystring
    def process_query(self, query: str) -> List[str]:
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token.lower()) for token in query.split()]

    def build_query_vector(self, query: List[str]) -> (Dict[str, float], float):
        vector: Dict[str, float] = {}

        # query ponderation
        if self.query_ponderation == DocumentPonderation.BINARY:
            for token in query:
                if token not in vector:
                    vector[token] = 1
        else:
            # this step is mandatory for all the other ponderation methods
            tokens_number = len(query)
            for token in query:
                if token not in vector:
                    vector[token] = 1 / tokens_number
                else:
                    vector[token] += 1 / tokens_number

            # For some of them, we need to update the vector weights
            if self.query_ponderation == DocumentPonderation.FREQUENCY_NORMALIZED:
                max_f = max(vector.values())
                for term in vector:
                    vector[term] = 0.5 + 0.5 * vector[term] / max_f
            elif self.query_ponderation == DocumentPonderation.LOG:
                for term in vector:
                    vector[term] = 1 + math.log(vector[term])
            elif self.query_ponderation == DocumentPonderation.LOG_NORMALIZED:
                average = sum(vector.values())
                for term in vector:
                    vector[term] = (1 + math.log(vector[term])) / (
                        1 + math.log(average)
                    )

        # term ponderation
        if self.query_term_ponderation == TermPonderation.IDF:
            for term in vector:
                vector[term] *= self.idf(term)
        elif self.query_term_ponderation == TermPonderation.NORMALIZED:
            for term in vector:
                vector[term] *= self.normalized(term)

        return vector, norm2(vector)

    # function to compute the score of every document
    def compute_query(self, query: List[str]) -> Dict[int, float]:
        scores: Dict[int, float] = {}

        q, q_norm = self.build_query_vector(query)

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

    # return the ordered list of results
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

    def set_document_ponderation(self, ponderation: DocumentPonderation):
        self.document_ponderation = ponderation

    def set_term_ponderation(self, ponderation: TermPonderation):
        self.term_ponderation = ponderation

    def type(self) -> str:
        return EngineType.VECTORIAL_SEARCH


def norm2(vector: Dict[str, float]) -> float:
    n = 0

    for term in vector:
        n += vector[term] ** 2

    return math.sqrt(n)
