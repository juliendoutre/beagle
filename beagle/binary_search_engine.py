from beagle.logging import timer
from beagle.index import InvertedIndex
from beagle.search_engines import SearchEngine
from nltk.stem import WordNetLemmatizer
from typing import List
import tt


class BinarySearchEngine(SearchEngine):
    def __init__(self, index: InvertedIndex) -> None:
        self.index: InvertedIndex = index

    def process_query(self, query: str) -> tt.ExpressionTreeNode:
        lemmatizer = WordNetLemmatizer()
        q = query.split()

        a = []
        for token in q:
            if token not in ["OR", "AND", "NAND"]:
                a.append(lemmatizer.lemmatize(token.lower()))
            else:
                a.append(token)

        return tt.BooleanExpression(" ".join(a)).tree

    def compute_query(self, node: tt.ExpressionTreeNode) -> List[int]:
        if node._symbol_name == "AND":
            return intersect(
                self.compute_query(node._l_child), self.compute_query(node._r_child)
            )
        elif node._symbol_name == "OR":
            return merge(
                self.compute_query(node._l_child), self.compute_query(node._r_child)
            )
        elif node._symbol_name == "NAND":
            return exclude(
                self.compute_query(node._l_child), self.compute_query(node._r_child)
            )
        else:
            try:
                return [a[0] for a in self.index.entries[node._symbol_name][1]]
            except Exception:
                return []

    @timer
    def query(self, query: str) -> List[int]:
        return self.compute_query(self.process_query(query))


def merge(a: List[int], b: List[int]) -> List[int]:
    result = []
    i, j = 0, 0

    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1

    return result


def intersect(a: List[int], b: List[int]) -> List[int]:
    result = []
    i, j = 0, 0

    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            result.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1

    return result


def exclude(a: List[int], b: List[int]) -> List[int]:
    return [i for i in a if i not in b]
