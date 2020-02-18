#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import argparse
from beagle.logging import init_logger
from beagle.collection import Collection
from beagle.index import InvertedIndexTypes


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
        type=InvertedIndexTypes,
        choices=list(InvertedIndexTypes),
        default=InvertedIndexTypes.DOCUMENTS_INDEX,
        help="type of index",
    )
    index_parser.add_argument(
        "-o",
        "--output",
        default="./index/index.json",
        type=str,
        help="path to which save the dataset",
    )

    search_parser = subparsers.add_parser("search", help="to query the collection")

    args = parser.parse_args()
    if args.cmd == "index":
        collection = Collection("cs276", args.dataset)
        collection.scan_shards()
        collection.scan_documents()
        collection.load_documents()

        print(collection)
        for s in collection.shards:
            print(s)

        collection.load_stop_words_list("./stop_words.json")
        collection.filter_documents()

        collection.lemmatize_documents()

        print(len(collection.get_vocabulary()))

        print(len(collection.index().entries))

    elif args.cmd == "search":
        pass
    else:
        raise parser.error(f"invalid command {args.cmd}")


if __name__ == "__main__":
    main()
