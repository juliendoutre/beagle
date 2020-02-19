from beagle.logging import timer
from beagle.index import InvertedIndex
from beagle.search_engines import SearchEngine
from nltk.stem import WordNetLemmatizer
from typing import List


class VectorialSearchEngine(SearchEngine):
    def __init__(self, index: InvertedIndex) -> None:
        self.index: InvertedIndex = index

    @timer
    def query(self, query: str) -> List[int]:
        return []
