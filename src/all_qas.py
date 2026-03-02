#!/usr/bin/env python
from argparse import ArgumentParser
from enum import Enum


class SearchStrategy(Enum):
    TFQAS = 1
    GAQAS = 2
    QDQAS = 3


def main(search_strategy: SearchStrategy):

    pass


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--strategy", type=SearchStrategy, default=SearchStrategy.QDQAS, help="Search strategy")
    args = parser.parse_args()
    main(args.strategy)
