from typing import Dict
import json
from beagle.logging import timer


class Stats:
    def __init__(self) -> None:
        self.documents: Dict[int, Dict[str, int]] = {}
        self.documents_number: int = 0

    def update(self, stats: "Stats") -> None:
        self.documents_number += stats.documents_number
        self.documents.update(stats.documents)

    @timer
    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(
                {
                    "documents_number": self.documents_number,
                    "documents": self.documents,
                },
                f,
            )


def load_stats(path: str) -> Stats:
    with open(path, "r") as f:
        stats = Stats()

        raw = json.load(f)
        stats.documents_number = raw["documents_number"]
        stats.documents = raw["documents"]

        return stats
