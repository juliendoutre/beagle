#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from beagle.logging import init_logger
from beagle.collection import Collection
from beagle.index import InvertedIndexType, load_index, InvertedIndex
from beagle.binary_search_engine import BinarySearchEngine
from beagle.vectorial_search_engine import VectorialSearchEngine
from beagle.search_engines import EngineType, SearchEngine
from beagle.stats import load_stats, Stats


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
        stats = load_stats(args.input + "stats.json")

        engine_name = args.engine
        engine = load_engine(index, stats, engine_name)

        print("welcome, to get instructions type .help")
        while True:
            print("beagle>", end=" ")

            user_input = input()
            if len(user_input) == 0:
                print("no input specified")
                continue
            if user_input[0] == ".":
                # special commands
                cmd_and_margs = user_input[1:].split(" ")
                cmd = cmd_and_margs[0]
                margs = cmd_and_margs[1:]
                if cmd == "exit":
                    return
                elif cmd == "engine":
                    print(engine_name)
                elif cmd == "help":
                    help()
                elif cmd == "set-engine":
                    if len(margs) == 0:
                        print("no new engine specified")
                        continue
                    if margs[0] not in [engine.value for engine in EngineType]:
                        print(f"{margs[0]} is not an available engine: {engines}")
                        continue
                    engine_name = EngineType(margs[0])
                    engine = load_engine(index, stats, engine_name)

                else:
                    print("unknown command")
            else:
                try:
                    print(engine.query(user_input))
                except Exception as e:
                    print(e)

    else:
        raise parser.error(f"invalid command {args.cmd}")


def load_engine(
    index: InvertedIndex, stats: Stats, engine_name: EngineType
) -> SearchEngine:
    engine: SearchEngine
    if engine_name == EngineType.BINARY_SEARCH:
        engine = BinarySearchEngine(index)
    elif engine_name == EngineType.VECTORIAL_SEARCH:
        engine = VectorialSearchEngine(index, stats, 10)
    else:
        raise Exception(f"unknown engine: {engine_name}")

    return engine


def help() -> None:
    cmds = ", ".join(["exit", "engine", "help", "set-engine"])
    print(f"available commands: {cmds}")


if __name__ == "__main__":
    main()
