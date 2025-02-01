"""
Script to run the Roskilde Festival 2025 scraper and print results.
"""

import time
from stagediver.scraper.festivals.roskilde.roskilde_2025 import RoskildeFestival2025Scraper

def main():
    # Initialize scraper
    scraper = RoskildeFestival2025Scraper()

    print("Starting Roskilde Festival 2025 scraper...")

    # Fetch lineup data
    data = scraper.fetch_lineup()

    # Get first 10 artists
    artists = data.raw_content['artists'][:10]

    # Print results
    print(f"\nShowing first 10 of {len(data.raw_content['artists'])} artists:")
    print("-" * 50)

    for artist in artists:
        print(f"Artist: {artist['name']}")
        print(f"URL: {artist['url']}")
        print("-" * 50)
        time.sleep(0.5)  # Half second delay between printing each artist

if __name__ == "__main__":
    main()
