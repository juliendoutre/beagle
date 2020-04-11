#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from beagle.logging import init_logger
from beagle.collection import Collection
from beagle.index import InvertedIndexType, load_index, InvertedIndex, load_doc_index
from beagle.binary_search_engine import BinarySearchEngine
from beagle.vectorial_search_engine import VectorialSearchEngine
from beagle.search_engines import EngineType, SearchEngine
from beagle.stats import load_stats, Stats
from typing import List
from enum import Enum

DOCUMENTS_LIST_LIMIT = 10
DOCUMENTS_LIST_OVERFLOW_SAVE_FILE_PATH = "./beagle_documents_list.txt"


def main() -> None:
    init_logger()

    parser = argparse.ArgumentParser(
        prog="beagle",
        description="A text search-engine over the Stanford CS276 document collection.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")

    subparsers = parser.add_subparsers(help="available commands", dest="cmd")

    index_parser = subparsers.add_parser("index", help="to index the collection")
    index_parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
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
    search_parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    search_parser.add_argument(
        "-x",
        "--index",
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
    search_parser.add_argument(
        "query",
        type=str,
        default=None,
        nargs="?",
        help="A query expression. An empty value will start the interactive console.",
    )
    search_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="to save the results of a direct query to a file",
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

        doc_index = collection.get_doc_index()
        doc_index.save(args.output + "doc_index.json")
    elif args.cmd == "search":
        index = load_index(args.index + "index.json")
        stats = load_stats(args.index + "stats.json")
        doc_index = load_doc_index(args.index + "doc_index.json")

        engine_name = args.engine
        engine = load_engine(index, stats, engine_name)

        if args.query is not None:
            # Direct query
            try:
                results = engine.query(args.query)
                formatted_results = doc_index.format_results(results)

                print(
                    f"{TextStyle.OKGREEN}Beagle found {len(results)} relevant documents!{TextStyle.ENDC}"
                )
                if args.output is not None:
                    with open(args.output, "w") as f:
                        f.write("\n".join(formatted_results))
                        print(
                            f"{TextStyle.OKGREEN}The documents list was saved in {args.output}{TextStyle.ENDC}"
                        )
                else:
                    for line in formatted_results[
                        : min(DOCUMENTS_LIST_LIMIT, len(formatted_results))
                    ]:
                        print(line)
                    if len(formatted_results) > DOCUMENTS_LIST_LIMIT:
                        print(
                            f"{TextStyle.WARNING}There are too many results to display them all! Beagle saved the complete list in {DOCUMENTS_LIST_OVERFLOW_SAVE_FILE_PATH}{TextStyle.ENDC}"
                        )
                        with open(DOCUMENTS_LIST_OVERFLOW_SAVE_FILE_PATH, "w") as f:
                            f.write("\n".join(formatted_results))

            except Exception as e:
                print(f"{TextStyle.FAIL}{e}{TextStyle.ENDC}")
        else:
            # Interactive console
            formatted_results = None
            print(
                f"{TextStyle.OKGREEN}{TextStyle.BOLD}Welcome! Type .help to get instructions{TextStyle.ENDC}"
            )
            while True:
                print("beagle>", end=" ")

                user_input = input()
                if len(user_input) == 0:
                    print(f"{TextStyle.WARNING}No input was specified{TextStyle.ENDC}")
                    continue
                if user_input[0] == ".":
                    # special commands
                    cmd_and_margs = user_input[1:].split(" ")
                    cmd = cmd_and_margs[0]
                    margs = cmd_and_margs[1:]
                    if cmd == "exit":
                        return
                    elif cmd == "engine":
                        print(f"Current engine: {engine_name}")
                    elif cmd == "help":
                        help()
                    elif cmd == "set-engine":
                        if len(margs) == 0:
                            print(
                                f"{TextStyle.WARNING}No new engine specified{TextStyle.ENDC}"
                            )
                            continue
                        if margs[0] not in [engine.value for engine in EngineType]:
                            print(
                                f"{TextStyle.WARNING}{margs[0]} is not an available engine: {engines}{TextStyle.ENDC}"
                            )
                            continue
                        engine_name = EngineType(margs[0])
                        engine = load_engine(index, stats, engine_name)
                        print(
                            f"{TextStyle.OKGREEN}Engine set to {engine_name}{TextStyle.ENDC}"
                        )
                    elif cmd == "save":
                        if len(margs) == 0:
                            print(
                                f"{TextStyle.WARNING}No path was provided{TextStyle.ENDC}"
                            )
                        else:
                            if formatted_results is not None:
                                try:
                                    with open(margs[0], "w") as f:
                                        f.write("\n".join(formatted_results))
                                        print(
                                            f"{TextStyle.OKGREEN}Results saved in {margs[0]}{TextStyle.ENDC}"
                                        )
                                except Exception as e:
                                    print(
                                        f"{TextStyle.FAIL}Could not save results in {margs[0]}: {e}{TextStyle.ENDC}"
                                    )
                            else:
                                print(
                                    f"{TextStyle.WARNING}Nothing to save{TextStyle.ENDC}"
                                )

                    else:
                        print(
                            f"{TextStyle.WARNING}Unknown command: {cmd}{TextStyle.ENDC}"
                        )
                else:
                    try:
                        results = engine.query(user_input)
                        formatted_results = doc_index.format_results(results)

                        print(
                            f"{TextStyle.OKGREEN}Beagle found {len(results)} relevant documents!{TextStyle.ENDC}"
                        )
                        for line in formatted_results[
                            : min(DOCUMENTS_LIST_LIMIT, len(formatted_results))
                        ]:
                            print(line)
                        if len(formatted_results) > DOCUMENTS_LIST_LIMIT:
                            print(
                                f"{TextStyle.WARNING}There are too many results to display them all! You can save the complete result list using the `.save <PATH>` command{TextStyle.ENDC}"
                            )

                    except Exception as e:
                        print(f"{TextStyle.FAIL}{e}{TextStyle.ENDC}")

    else:
        raise parser.error(f"Invalid command {args.cmd}")


def load_engine(
    index: InvertedIndex, stats: Stats, engine_name: EngineType
) -> SearchEngine:
    engine: SearchEngine
    if engine_name == EngineType.BINARY_SEARCH:
        engine = BinarySearchEngine(index)
    elif engine_name == EngineType.VECTORIAL_SEARCH:
        engine = VectorialSearchEngine(index, stats, DOCUMENTS_LIST_LIMIT)
    else:
        raise Exception(f"unknown engine: {engine_name}")

    return engine


def help() -> None:
    cmds = ", ".join(["exit", "engine", "help", "set-engine", "save"])
    print(f"The available commands are: [{cmds}]")
    print("\t.exit\t\t\texit the console")
    print("\t.engine\t\t\tdisplay the current engine")
    print("\t.help\t\t\tdisplay this message")
    print("\t.set-engine <ENGINE>\tchange of engine (vectorial or binary)")
    print("\t.save <PATH>\t\tsave the previous request results to a file")


class TextStyle(Enum):
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"

    def __str__(self) -> str:
        return self.value


if __name__ == "__main__":
    main()
