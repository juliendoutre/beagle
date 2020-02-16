#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import argparse
from beagle.logging import init_logger
from beagle.collection import Collection


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
        "-d", "--dataset", default="./dataset", type=str, help="path to the dataset"
    )

    search_parser = subparsers.add_parser("search", help="to query the collection")

    args = parser.parse_args()
    if args.cmd == "index":
        collection = Collection("cs276", args.dataset)
        collection.scan_shards()
        collection.scan_documents()
        collection.load()
        print(collection)
        for s in collection.shards:
            print(s)
        print(collection.term_frequencies().most_common(100))

    elif args.cmd == "search":
        pass
    else:
        raise parser.error(f"invalid command {args.cmd}")


if __name__ == "__main__":
    main()
