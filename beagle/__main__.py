#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import argparse
from beagle.logging import init_logger


def main() -> None:
    init_logger()

    parser = argparse.ArgumentParser(
        prog="beagle",
        description="A text search-engine over the Stanford CS276 document collection.",
    )
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")

    subparsers = parser.add_subparsers(help="available commands", dest="cmd")
    index_parser = subparsers.add_parser("index", help="to index the collection")
    search_parser = subparsers.add_parser("search", help="to query the collection")

    args = parser.parse_args()
    if args.cmd == "index":
        pass
    elif args.cmd == "search":
        pass
    else:
        raise parser.error(f"invalid command {args.cmd}")


if __name__ == "__main__":
    main()
