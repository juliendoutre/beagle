#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from beagle.logging import init_logger


def main() -> None:
    init_logger()
    logging.info("Hello world")


if __name__ == "__main__":
    main()
