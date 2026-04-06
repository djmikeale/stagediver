"""
Script to fetch and save festival lineup data.
"""

import argparse
import importlib
import inspect
from typing import Optional

from stagediver.scraper import run_scraper


def get_scraper_class(class_name: str):
    """
    Dynamically import and return the specified scraper class.

    Args:
        class_name: Name of the scraper class to load

    Returns:
        Scraper class with the given name
    """
    module = importlib.import_module("stagediver.scraper.scraper")
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        available = [
            name
            for name, cls in inspect.getmembers(module, inspect.isclass)
            if cls.__module__ == module.__name__ and name != "BaseFestivalScraper"
        ]
        raise ValueError(
            f"No scraper found for class:\n{class_name}\n\n"
            f"Available scrapers: \n{'\n'.join(sorted(available))}"
        ) from e


def main():
    parser = argparse.ArgumentParser(description="Fetch and save festival lineup data")

    # Required arguments
    parser.add_argument(
        "-c",
        "--class-name",
        type=str,
        required=True,
        help="Scraper class name to load (e.g. RoskildeFestival2026Scraper)",
    )

    # Optional arguments
    parser.add_argument(
        "-s",
        "--sample-size",
        type=int,
        help="Optional: Limit number of artists to scrape (default: all artists)",
    )

    args = parser.parse_args()

    try:
        scraper_class = get_scraper_class(args.class_name)
    except ValueError as error:
        print(error)
        raise SystemExit(1)

    scraper = scraper_class()
    run_scraper(scraper, sample_size=args.sample_size)


if __name__ == "__main__":
    main()
