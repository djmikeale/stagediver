"""
Script to fetch and save the complete Roskilde Festival 2025 lineup.
"""

from stagediver.scraper import run_scraper
from stagediver.scraper.roskilde_festival__2025.scraper import RoskildeFestival2025Scraper

def main():
    scraper = RoskildeFestival2025Scraper()
    run_scraper(scraper, sample_size=5)

if __name__ == "__main__":
    main()
