import os
import json
import typing
from beagle.index import (
    InvertedIndex,
    InvertedIndexEntry,
    InvertedIndexType,
    DocumentsInvertedIndexEntry,
    DocumentsInvertedIndex,
    FrequenciesInvertedIndexEntry,
    FrequenciesInvertedIndex,
    PositionsInvertedIndexEntry,
    PositionsInvertedIndex,
)
from typing import List, Set, Dict, Tuple, Any
from collections import Counter
from beagle.logging import timer
from nltk.stem import WordNetLemmatizer


class Document:
    def __init__(self, name: str, path: str, id: int) -> None:
        self.name: str = name
        self.path: str = path
        self.id: int = id
        self.tokens: List[str] = []

    def __str__(self) -> str:
        return f"document {self.name} ({self.path}): {len(self.tokens)} tokens"

    def load(self) -> None:
        with open(self.path, "r") as f:
            self.tokens = f.read().split()

    def filter(self, stop_words: List[str]) -> None:
        filtered_tokens: List[str] = []

        for t in self.tokens:
            if t not in stop_words:
                filtered_tokens.append(t)

        self.tokens = filtered_tokens

    def lemmatize(self) -> None:
        lems: List[str] = []
        lemmatizer = WordNetLemmatizer()

        for t in self.tokens:
            lems.append(lemmatizer.lemmatize(t))

    def get_vocabulary(self) -> Set[str]:
        return set(self.tokens)

    def term_frequencies(self) -> typing.Counter[str]:
        return Counter(self.tokens)

    def term_positions(self) -> Dict[str, List[Any]]:
        positions: Dict[str, List[Any]] = {}

        for (i, t) in enumerate(self.tokens):
            if t in positions:
                positions[t][0] += 1
                positions[t][1].append(i)
            else:
                positions[t] = [1, [i]]

        return positions


class Shard:
    def __init__(self, name: str, path: str) -> None:
        self.name: str = name
        self.path: str = path
        self.documents: List[Document] = []

    def __str__(self) -> str:
        return f"shard {self.name} ({self.path}): {len(self.documents)} documents"

    def scan_documents(self) -> None:
        id = 10 ** 6 * int(self.name)
        for f in os.scandir(self.path):
            if f.is_file():
                self.documents.append(Document(f.name, f.path, id))
                id += 1

    def load(self) -> None:
        for d in self.documents:
            d.load()

    def filter_documents(self, stop_words: List[str]) -> None:
        for d in self.documents:
            d.filter(stop_words)

    def lemmatize_documents(self) -> None:
        for d in self.documents:
            d.lemmatize()

    def get_vocabulary(self) -> Set[str]:
        vocabulary: Set[str] = set()

        for d in self.documents:
            vocabulary.update(d.get_vocabulary())

        return vocabulary

    def term_frequencies(self) -> typing.Counter[str]:
        frequencies: typing.Counter[str] = Counter()

        for d in self.documents:
            frequencies.update(d.term_frequencies())

        return frequencies

    def index(self, index_type: InvertedIndexType) -> InvertedIndex:
        if index_type == InvertedIndexType.DOCUMENTS_INDEX:
            index = DocumentsInvertedIndex()
            for d in self.documents:
                frequencies = d.term_frequencies()
                for t in frequencies:
                    if t in index.entries:
                        index.entries[t].frequency += 1
                        index.entries[t].ids.append(d.id)
                    else:
                        index.entries[t] = DocumentsInvertedIndexEntry(d.id)

        elif index_type == InvertedIndexType.FREQUENCIES_INDEX:
            index = FrequenciesInvertedIndex()
            for d in self.documents:
                frequencies = d.term_frequencies()
                for t in frequencies:
                    if t in index.entries:
                        index.entries[t].frequency += 1
                        index.entries[t].ids.append((d.id, frequencies[t]))
                    else:
                        index.entries[t] = FrequenciesInvertedIndexEntry(
                            d.id, frequencies[t]
                        )
        else:
            index = PositionsInvertedIndex()
            for d in self.documents:
                positions = d.term_positions()
                for t in positions:
                    if t in index.entries:
                        index.entries[t].frequency += 1
                        index.entries[t].ids.append(
                            (d.id, positions[t][0], positions[t][1])
                        )
                    else:
                        index.entries[t] = PositionsInvertedIndexEntry(
                            d.id, positions[t][0], positions[t][1]
                        )

        return index


class Collection:
    def __init__(self, name: str, path: str) -> None:
        self.name: str = name
        self.path: str = path
        self.shards: List[Shard] = []
        self.stop_words: List[str] = []

    def __str__(self) -> str:
        return f"collection {self.name} ({self.path}): {len(self.shards)} shards"

    @timer
    def scan_shards(self) -> None:
        for d in os.scandir(self.path):
            if d.is_dir():
                self.shards.append(Shard(d.name, d.path))

    @timer
    def scan_documents(self) -> None:
        for s in self.shards:
            s.scan_documents()

    @timer
    def load_documents(self) -> None:
        for s in self.shards:
            s.load()

    @timer
    def load_stop_words_list(self, path: str) -> None:
        with open(path, "r") as f:
            self.stop_words = json.load(f)

    @timer
    def filter_documents(self) -> None:
        for s in self.shards:
            s.filter_documents(self.stop_words)

    @timer
    def lemmatize_documents(self) -> None:
        for s in self.shards:
            s.lemmatize_documents()

    def get_vocabulary(self) -> Set[str]:
        vocabulary: Set[str] = set()

        for s in self.shards:
            vocabulary.update(s.get_vocabulary())

        return vocabulary

    @timer
    def term_frequencies(self) -> typing.Counter[str]:
        frequencies: typing.Counter[str] = Counter()

        for s in self.shards:
            frequencies.update(s.term_frequencies())

        return frequencies

    @timer
    def index(self, index_type: InvertedIndexType) -> InvertedIndex:
        if index_type == InvertedIndexType.DOCUMENTS_INDEX:
            index = DocumentsInvertedIndex()
        elif index_type == InvertedIndexType.FREQUENCIES_INDEX:
            index = FrequenciesInvertedIndex()
        else:
            index = PositionsInvertedIndex()

        for s in self.shards:
            index.update(s.index(index_type))

        return index
