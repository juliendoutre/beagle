import pytest
import itertools
from beagle.index import load_index, load_doc_index, InvertedIndex, DocIndex
from beagle.stats import load_stats, Stats
from beagle.search_engines import DocumentPonderation, TermPonderation
from beagle.vectorial_search_engine import VectorialSearchEngine
from typing import List
import matplotlib
import matplotlib.pyplot as plt


@pytest.fixture
def index() -> InvertedIndex:
    return load_index("./index/index.json")


@pytest.fixture
def stats() -> Stats:
    return load_stats("./index/stats.json")


@pytest.fixture
def mapping() -> DocIndex:
    return load_doc_index("./index/doc_index.json")


def load_query(id: int) -> List[str]:
    with open(f"./tests/queries/query.{id}", "r") as f:
        return f.read().split("\n")[0]


def load_expected_results(id: int) -> List[str]:
    with open(f"./tests/queries/query.{id}.out", "r") as f:
        return f.read().split("\n")


def evaluate(results: List[str], expected_results: List[str]) -> int:
    score = 0

    for i, r in enumerate(expected_results):
        try:
            j = results.index(r)
        except Exception:
            continue
        score += 1 / (abs(i - j) + 1)

    return score


class TestVectorialQueries:
    @pytest.mark.skip(
        reason="this test was used to perform benchmarks and is pretty long to run."
    )
    @pytest.mark.parametrize("i", [1, 2, 3, 4, 5, 6, 7, 8])
    def test_query(self, index, stats, mapping, i):
        query = load_query(i)
        expected_results = load_expected_results(i)
        to_save: List[str] = [f"Beagle benchmark against query: {query}"]

        # we test all the possible ponderations (for the docs and the query)
        for config in itertools.product(
            DocumentPonderation, TermPonderation, DocumentPonderation, TermPonderation
        ):
            engine = VectorialSearchEngine(
                index, stats, config[0], config[1], config[2], config[3]
            )
            results_ids = [str(r) for r in engine.query(query)]
            results = [mapping.entries[id]["path"][10:] for id in results_ids]

            to_save.append(
                f"({config[0]},{config[1]},{config[2]},{config[3]}): {evaluate(results, expected_results)}"
            )

        with open(f"./tests/queries/query.{i}.benchmark", "w") as f:
            f.write("\n".join(to_save))

    @pytest.mark.skip(reason="this test was used to perform benchmarks")
    @pytest.mark.parametrize("i", [1, 2, 3, 4, 8])
    def test_charts(self, i):
        with open(f"./tests/queries/query.{i}.benchmark", "r") as f:
            _, ax = plt.subplots()

            lines = f.readlines()

            ax.set_title(f"{lines[0]}")
            ax.set_xlabel("Vectorial engine config")
            ax.set_ylabel("Score")

            labels = []
            scores = []

            for line in lines[1:]:
                data = line.split(":")
                labels.append(data[0])
                scores.append(float(data[1]))

            _, _, _ = ax.hist(scores, range(276))
            plt.savefig(f"./tests/queries/query.{i}.benchmark.png")

            with open(f"./tests/queries/query.{i}.benchmark.top", "w") as fw:
                fw.write(
                    "\n".join(
                        [
                            a[0]
                            for a in sorted(
                                [
                                    (line.split(":")[0], line.split(":")[1])
                                    for line in lines[1:]
                                ],
                                key=lambda x: x[1],
                                reverse=True,
                            )
                        ]
                    )
                )

    @pytest.mark.skip(reason="this test was used to perform benchmarks")
    def test_top(self):
        top = {}

        for i in [1, 2, 3, 4, 8]:
            with open(f"./tests/queries/query.{i}.benchmark", "r") as f:
                lines = f.readlines()

                for line in lines[1:]:
                    data = line.split(":")
                    if data[0] not in top:
                        top[data[0]] = float(data[1])
                    else:
                        top[data[0]] += float(data[1])

        _, ax = plt.subplots()

        ax.set_title(f"All requests")
        ax.set_xlabel("Vectorial engine config")
        ax.set_ylabel("Score")

        _, _, _ = ax.hist([a / 5 for a in top.values()], range(276))
        plt.savefig(f"./tests/queries/top.png")

        with open("./tests/queries/top.txt", "w") as fw:
            fw.write(
                "\n".join(
                    [
                        a[0]
                        for a in sorted(top.items(), key=lambda x: x[1], reverse=True)
                    ]
                )
            )
