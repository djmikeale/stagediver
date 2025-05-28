"""
Scraper implementation for Roskilde Festival 2025.
"""

import re
from datetime import datetime
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from stagediver.models import ScrapedData


class RoskildeFestival2025Scraper:
    """
    Scraper for Roskilde Festival 2025 lineup and schedule.
    """

    # Mapping of Danish dates to ISO format dates for Roskilde Festival 2025
    DATE_MAPPING = {
        "søndag 29. juni": "2025-06-29",
        "mandag 30. juni": "2025-06-30",
        "tirsdag 1. juli": "2025-07-01",
        "onsdag 2. juli": "2025-07-02",
        "torsdag 3. juli": "2025-07-03",
        "fredag 4. juli": "2025-07-04",
        "lørdag 5. juli": "2025-07-05",
        "onsdag nat 2. juli*": "2025-07-03",
        "torsdag nat 3. juli*": "2025-07-04",
        "fredag nat 4. juli*": "2025-07-05",
        "lørdag nat 5. juli*": "2025-07-06",
    }

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
        artist_cards = soup.find_all("div", class_=re.compile(r"artistCard"))

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

            content_div = card.find("div", class_=lambda c: c and "card_content" in c)
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
        date_element = soup.find("div", class_=lambda c: c and "showTimesDay" in c)
        performance_date = date_element.text.strip() if date_element else None
        if performance_date:
            # Convert to lowercase before mapping
            performance_date = self.DATE_MAPPING.get(performance_date.lower().strip())

        # Get stage name and time
        stage_element = soup.find(
            "div", class_=lambda c: c and "showTimesLocation" in c
        )
        stage_info = stage_element.text.strip() if stage_element else None

        artist_country = soup.find(
            "sup", class_=lambda c: c and "typography_superscript" in c
        )
        artist_country = (
            [country.strip() for country in artist_country.text.split("/")]
            if artist_country
            else None
        )

        # Split stage info into time and stage name
        stage_times = []
        if stage_info:
            # Split by / to handle multiple times
            stage_infos = stage_info.split("/")
            for info in stage_infos:
                # Match time using two capture groups: (HH.MM), (stage_name)
                match = re.match(r".*?(\d{2}\.\d{2}),\s*(.*)", info.strip())
                if match:
                    stage_time, stage_name = match.groups()
                    stage_times.append({"time": stage_time, "stage": stage_name})

        # Combine date and time into datetime
        start_ts = None
        if performance_date and stage_times:
            try:
                # Use first time for now
                time_str = stage_times[0]["time"].replace(".", ":")
                datetime_str = f"{performance_date}T{time_str}:00"
                start_ts = datetime.fromisoformat(datetime_str).isoformat()
            except ValueError as e:
                print(f"Error parsing datetime: {e}")

        # Get short description
        short_desc_element = soup.find(
            "h2", class_=lambda c: c and "headlineSmall" in c
        )
        short_description = (
            short_desc_element.text.strip() if short_desc_element else None
        )

        # Get long description with preserved line breaks
        long_desc_element = soup.find(
            "div", class_=lambda c: c and "rich-text_component" in c
        )
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
            "stage": stage_times[0]["stage"] if stage_times else None,
            "start_ts": start_ts,
            "short_description": short_description,
            "long_description": long_description,
            "spotify_link": spotify_link,
            "country_code": artist_country,
        }
