#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from beagle.logging import init_logger
from beagle.collection import Collection
from beagle.index import InvertedIndexType, load_index
from beagle.binary_search_engine import BinarySearchEngine
from beagle.vectorial_search_engine import VectorialSearchEngine
from beagle.search_engines import EngineType, SearchEngine
from beagle.stats import load_stats


def main() -> None:
    init_logger()

    parser = argparse.ArgumentParser(
        prog="beagle",
        description="A text search-engine over the Stanford CS276 document collection.",
    )
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")

    subparsers = parser.add_subparsers(help="available commands", dest="cmd")

    index_parser = subparsers.add_parser("index", help="to index the collection")
    index_parser.add_argument(
        "-d", "--dataset", type=str, default="./dataset", help="path to the dataset"
    )
    index_parser.add_argument(
        "-t",
        "--type",
        type=InvertedIndexType,
        choices=list(InvertedIndexType),
        default=InvertedIndexType.POSITIONS_INDEX,
        help="type of index",
    )
    index_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./index/",
        help="path to which save the index and stats",
    )

    search_parser = subparsers.add_parser("search", help="to query the collection")
    search_parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="./index/",
        help="path to the saved index and stats",
    )
    engines = ", ".join(engine.value for engine in EngineType)
    search_parser.add_argument(
        "-e",
        "--engine",
        type=EngineType,
        default=EngineType.BINARY_SEARCH,
        help=f"the engine to use to perform queries among ({engines})",
    )

    args = parser.parse_args()
    if args.cmd == "index":
        collection = Collection("cs276", args.dataset)
        collection.scan_shards()
        collection.scan_documents()
        collection.load_documents()

        collection.load_stop_words_list("./stop_words.json")
        collection.filter_documents()

        collection.lemmatize_documents()

        index = collection.index(args.type)
        index.save(args.output + "index.json")

        stats = collection.compute_stats()
        stats.save(args.output + "stats.json")
    elif args.cmd == "search":
        index = load_index(args.input + "index.json")

        engine: SearchEngine
        if args.engine == EngineType.BINARY_SEARCH:
            engine = BinarySearchEngine(index)
        elif args.engine == EngineType.VECTORIAL_SEARCH:
            stats = load_stats(args.input + "stats.json")
            engine = VectorialSearchEngine(index, stats, 10)

        while True:
            print("beagle>", end=" ")

            user_input = input()
            if user_input == ".exit":
                return
            elif user_input == ".engine":
                print(args.engine)
            else:
                print(engine.query(user_input))
    else:
        raise parser.error(f"invalid command {args.cmd}")


if __name__ == "__main__":
    main()
