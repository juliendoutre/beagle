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


def norm2(vector: Dict[str, float]) -> float:
    n = 0

    for term in vector:
        n += vector[term] ** 2

    return math.sqrt(n)


class VectorialSearchEngine(SearchEngine):
    def __init__(
        self,
        index: InvertedIndex,
        stats: Stats,
        document_ponderation: DocumentPonderation = DocumentPonderation.TF,
        term_ponderation: TermPonderation = TermPonderation.IDF,
        query_ponderation: DocumentPonderation = DocumentPonderation.TF,
        query_term_ponderation: TermPonderation = TermPonderation.NONE,
    ) -> None:
        self.index: InvertedIndex = index
        self.stats: Stats = stats
        self.document_ponderation = document_ponderation
        self.term_ponderation = term_ponderation
        self.query_ponderation = query_ponderation
        self.query_term_ponderation = query_term_ponderation

    # ponderation functions that depends on a document and a term
    def tf(self, f: int, id: int) -> int:
        return f / self.stats.documents[id]["tokens_number"]

    def frequency_normalized_tf(self, f: int, id: int) -> float:
        return 0.5 + 0.5 * self.tf(f, id) / (
            self.stats.documents[id]["max_frequency"]
            / self.stats.documents[id]["tokens_number"]
        )

    def log_tf(self, f: int, id: int) -> float:
        return 1 + math.log(self.tf(f, id))

    def log_frequency_normalized_tf(self, f: int, id: int) -> float:
        avg = (
            self.stats.documents[id]["sum_frequency"]
            / self.stats.documents[id]["tokens_number"]
        ) / (
            self.stats.documents[id]["unique_terms_number"] + 1
        )  # we add 1 to avoid zero division errors
        return (1 + self.log_tf(f, id)) / (1 + math.log(avg))

    # ponderation functions that depend only on a term
    def idf(self, term: str) -> float:
        return math.log(self.stats.documents_number / self.index.entries[term][0])

    def normalized(self, term: str) -> float:
        return max(
            0,
            (self.stats.documents_number - self.index.entries[term][0])
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

    def get_document_weight(self, f: int, term: str, id: int) -> float:
        w = 0

        # document ponderation
        if self.document_ponderation == DocumentPonderation.BINARY:
            w = 1
        elif self.document_ponderation == DocumentPonderation.TF:
            w = self.tf(f, id)
        elif self.document_ponderation == DocumentPonderation.FREQUENCY_NORMALIZED:
            w = self.frequency_normalized_tf(f, id)
        elif self.document_ponderation == DocumentPonderation.LOG:
            w = self.log_tf(f, id)
        elif self.document_ponderation == DocumentPonderation.LOG_NORMALIZED:
            w = self.log_frequency_normalized_tf(f, id)

        # term ponderation
        if self.term_ponderation == TermPonderation.IDF:
            w *= self.idf(term)
        elif self.term_ponderation == TermPonderation.NORMALIZED:
            w *= self.normalized(term)

        return w

    # function to compute the score of every document
    def compute_query(self, query: List[str]) -> Dict[int, float]:
        scores: Dict[int, float] = {}
        norms: Dict[int, float] = {}

        q, q_norm = self.build_query_vector(query)

        # for every query's term
        for term in q:
            # We get the doc ids that match this term from the index
            try:
                docs = [(doc[0], doc[1]) for doc in self.index.entries[term][1]]
            except Exception:
                docs = []

            # for every one of them we update their dot product saved un scores
            for doc in docs:
                id = doc[0]
                f = doc[1]
                w = self.get_document_weight(f, term, id)
                if id in scores:
                    scores[id] += q[term] * w
                    norms[id] += w ** 2
                else:
                    scores[id] = q[term] * w
                    norms[id] = w ** 2
        for id in scores:
            scores[id] /= q_norm
            scores[id] /= math.sqrt(norms[id])

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
            )
        }

    def __str__(self) -> str:
        return f"{EngineType.VECTORIAL_SEARCH.value} (documents ponderations: {self.document_ponderation}, {self.term_ponderation} ; query ponderations: {self.query_ponderation}, {self.query_term_ponderation})"

    def set_document_ponderation(self, ponderation: DocumentPonderation):
        self.document_ponderation = ponderation

    def set_term_ponderation(self, ponderation: TermPonderation):
        self.term_ponderation = ponderation

    def set_query_ponderation(self, ponderation: DocumentPonderation):
        self.query_ponderation = ponderation

    def set_query_term_ponderation(self, ponderation: TermPonderation):
        self.query_term_ponderation = ponderation

    def type(self) -> str:
        return EngineType.VECTORIAL_SEARCH
