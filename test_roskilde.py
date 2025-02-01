from stagediver.scraper.festivals.roskilde.roskilde_2025 import RoskildeFestival2025Scraper
import json

def test_roskilde():
    # Initialize the scraper
    scraper = RoskildeFestival2025Scraper()

    # Fetch just 2 artists
    data = scraper.fetch_lineup(sample_size=2)

    # Print the results
    print(json.dumps(data.raw_content['artists'], indent=2))

if __name__ == "__main__":
    test_roskilde()
