"""
Scraper implementation for Roskilde Festival 2025.
"""

from datetime import datetime
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from stagediver.models import ScrapedData


class RoskildeFestival2025Scraper:
    """
    Scraper for Roskilde Festival 2025 lineup and schedule.
    """

    def __init__(self):
        self.festival_name = "Roskilde Festival"
        self.festival_year = 2025
        self.base_url = "https://www.roskilde-festival.dk"
        self.program_url = f"{self.base_url}/program"
        self.session = requests.Session()
        self._setup_cookies()

    def _setup_cookies(self):
        """Setup cookies to accept all cookie categories."""
        cookies = {
            "CookieInformationConsent": '{"consents_approved":["cookie_cat_necessary","cookie_cat_functional","cookie_cat_statistic","cookie_cat_marketing"],"consents_denied":[]}',
            "CookieInformationConsent_marketing": "true",
        }
        self.session.cookies.update(cookies)

        # Make an initial request to set cookies
        self.session.get(self.base_url)

    def fetch_lineup(self, sample_size=None) -> ScrapedData:
        """
        Fetch the festival lineup from the website.

        Args:
            sample_size: Maximum number of artists to fetch. If None, fetches all artists.

        Returns:
            ScrapedData: Raw scraped data including artist links and basic info
        """
        print("Fetching program page...")
        response = self.session.get(self.program_url)
        soup = BeautifulSoup(response.text, "html.parser")

        artists_data = []
        artist_cards = soup.find_all(
            "div", class_="line-up-overview-cards_artistCard__WFH6G"
        )

        # Limit the number of cards if specified
        if sample_size:
            artist_cards = artist_cards[:sample_size]

        total_artists = len(artist_cards)
        print(f"Processing {total_artists} artists")

        for i, card in enumerate(artist_cards, 1):
            link_element = card.find("a")
            if not link_element:
                continue

            href = link_element.get("href", "")
            full_url = self.base_url + href if href else ""

            content_div = card.find("div", class_="card_content__NCkf_")
            name = (
                content_div.find("h2").text.strip()
                if content_div and content_div.find("h2")
                else ""
            )

            if name and full_url:
                print(f"Fetching details for {name} ({i}/{total_artists})...")
                artist_data = {
                    "name": name,
                    "url": full_url,
                    **self._fetch_artist_details(full_url),
                }
                artists_data.append(artist_data)

        return ScrapedData(
            source_url=self.program_url,
            raw_content={"artists": artists_data},
            festival_name=self.festival_name,
        )

    def _fetch_artist_details(self, url: str) -> Dict:
        """Fetch detailed information from artist's page."""
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Get performance date
        date_element = soup.find("div", class_="appearance-details_showTimesDay__5QRgW")
        performance_date = date_element.text.strip() if date_element else None

        # Check if the artist has been cancelled
        cancelled_element = soup.find(
            "div", class_="typography_cancelled__abc123"
        )  # Update this class name
        is_current = not bool(cancelled_element)

        # Get stage name
        stage_element = soup.find(
            "div", class_="appearance-details_showTimesLocation__j5Y_x"
        )
        stage = stage_element.text.strip() if stage_element else None

        # Get short description
        short_desc_element = soup.find("h2", class_="typography_headlineSmall__Xlw_0")
        short_description = (
            short_desc_element.text.strip() if short_desc_element else None
        )

        # Get long description with preserved line breaks
        long_desc_element = soup.find("div", class_="rich-text_component__c_7l6")
        long_description = None
        if long_desc_element:
            # Replace <br> and </p> tags with newlines before getting text
            for br in long_desc_element.find_all("br"):
                br.replace_with("\n")
            for p in long_desc_element.find_all("p"):
                p.append("\n")
            long_description = long_desc_element.get_text().strip()

        # Find Spotify artist link (not the footer playlist link)
        spotify_link = None
        spotify_links = soup.find_all(
            "a", href=lambda x: x and "open.spotify.com/artist" in x
        )
        if spotify_links:
            # Remove tracking parameters from Spotify URL
            spotify_link = spotify_links[0]["href"].split("?")[0]

        return {
            "performance_date": performance_date,
            "stage": stage,
            "short_description": short_description,
            "long_description": long_description,
            "spotify_link": spotify_link,
            "_is_current": is_current,
        }
