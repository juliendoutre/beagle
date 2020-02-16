import os
import typing
from typing import List
from collections import Counter


class Document:
    def __init__(self, name: str, path: str) -> None:
        self.name: str = name
        self.path: str = path
        self.tokens: List[str] = []

    def __str__(self) -> str:
        return f"document {self.name} ({self.path}): {len(self.tokens)} tokens"

    def load(self) -> None:
        with open(self.path, "r") as f:
            self.tokens = f.read().split()

    def term_frequencies(self) -> typing.Counter[str]:
        return Counter(self.tokens)


class Shard:
    def __init__(self, name: str, path: str) -> None:
        self.name: str = name
        self.path: str = path
        self.documents: List[Document] = []

    def __str__(self) -> str:
        return f"shard {self.name} ({self.path}): {len(self.documents)} documents"

    def scan_documents(self) -> None:
        for f in os.scandir(self.path):
            if f.is_file():
                self.documents.append(Document(f.name, f.path))

    def load(self) -> None:
        for d in self.documents:
            d.load()

    def term_frequencies(self) -> typing.Counter[str]:
        frequencies: typing.Counter[str] = Counter()

        for d in self.documents:
            frequencies.update(d.term_frequencies())

        return frequencies


class Collection:
    def __init__(self, name: str, path: str) -> None:
        self.name: str = name
        self.path: str = path
        self.shards: List[Shard] = []

    def __str__(self) -> str:
        return f"collection {self.name} ({self.path}): {len(self.shards)} shards"

    def scan_shards(self) -> None:
        for d in os.scandir(self.path):
            if d.is_dir():
                self.shards.append(Shard(d.name, d.path))

    def scan_documents(self) -> None:
        for s in self.shards:
            s.scan_documents()

    def load(self) -> None:
        for s in self.shards:
            s.load()

    def term_frequencies(self) -> typing.Counter[str]:
        frequencies: typing.Counter[str] = Counter()

        for s in self.shards:
            frequencies.update(s.term_frequencies())

        return frequencies
