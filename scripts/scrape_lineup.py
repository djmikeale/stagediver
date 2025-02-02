"""
Script to fetch and save festival lineup data.
Usage:
    python save_festival_lineup.py --festival roskilde --year 2025 [--sample-size 5]
"""

import argparse
import importlib
from typing import Optional

from stagediver.scraper import run_scraper

def get_scraper_class(festival: str, year: int):
    """
    Dynamically import and return the appropriate scraper class.

    Args:
        festival: Festival name (lowercase)
        year: Festival year

    Returns:
        Scraper class for the specified festival and year
    """
    try:
        # Convert festival name to match folder structure
        module_name = f"{festival}_festival"
        module = importlib.import_module(
            f"stagediver.scraper.{module_name}__{year}.scraper"
        )

        # Convention: ScraperClass is named [FestivalName]Festival[Year]Scraper
        class_name = f"{festival.title()}Festival{year}Scraper"
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        available = [
            "roskilde (2025)",
            # Add more as they become available
        ]
        raise ValueError(
            f"No scraper found for {festival} {year}. "
            f"Available scrapers: {', '.join(available)}\n"
            f"Looking for module: stagediver.scraper.{festival}_festival__{year}.scraper\n"
            f"Looking for class: {festival.title()}Festival{year}Scraper"
        ) from e

def main():
    parser = argparse.ArgumentParser(description="Fetch and save festival lineup data")

    # Required arguments
    parser.add_argument(
        "-f", "--festival",
        type=str,
        required=True,
        help="Festival name (e.g., roskilde)"
    )

    parser.add_argument(
        "-y", "--year",
        type=int,
        required=True,
        help="Festival year (e.g., 2025)"
    )

    # Optional arguments
    parser.add_argument(
        "-s", "--sample-size",
        type=int,
        help="Optional: Limit number of artists to scrape (default: all artists)"
    )

    args = parser.parse_args()

    # Get the appropriate scraper class
    scraper_class = get_scraper_class(args.festival.lower(), args.year)

    # Initialize and run the scraper
    scraper = scraper_class()
    run_scraper(scraper, sample_size=args.sample_size)

if __name__ == "__main__":
    main()
