"""
Scraper implementation for Roskilde Festival 2025.
"""

from datetime import datetime
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from stagediver.models import ScrapedData

class RoskildeFestival2025Scraper:
    """
    Scraper for Roskilde Festival 2025 lineup and schedule.
    """

    def __init__(self):
        self.year = 2025
        self.festival_name = "Roskilde Festival"
        self.base_url = "https://www.roskilde-festival.dk"
        self.program_url = f"{self.base_url}/program"

    def fetch_lineup(self) -> ScrapedData:
        """
        Fetch the festival lineup from the website.

        Returns:
            ScrapedData: Raw scraped data including artist links and basic info
        """
        response = requests.get(self.program_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        artists_data = []
        # Find all artist card divs
        artist_cards = soup.find_all('div', class_='line-up-overview-cards_artistCard__WFH6G')

        for card in artist_cards:
            # Find the anchor tag within the card
            link_element = card.find('a')
            if not link_element:
                continue

            # Get the href attribute
            href = link_element.get('href', '')
            full_url = self.base_url + href if href else ''

            # Find the h2 element within the card_content div
            content_div = card.find('div', class_='card_content__NCkf_')
            name = content_div.find('h2').text.strip() if content_div and content_div.find('h2') else ''

            if name and full_url:
                artists_data.append({
                    'name': name,
                    'url': full_url
                })

        return ScrapedData(
            source_url=self.program_url,
            raw_content={
                "artists": artists_data
            },
            festival_name=self.festival_name
        )
