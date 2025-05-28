"""
Scraper implementation for Roskilde Festival 2025.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

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

    def _find_element(
        self, soup: BeautifulSoup, class_pattern: str
    ) -> Optional[BeautifulSoup]:
        """Helper method to find elements by class pattern."""
        return soup.find("div", class_=lambda c: c and class_pattern in c)

    def _get_text(self, element: Optional[BeautifulSoup]) -> Optional[str]:
        """Helper method to safely get text from an element."""
        return element.text.strip() if element else None

    def _parse_stage_info(self, stage_info: str) -> List[Dict[str, str]]:
        """Parse stage information into time and stage name pairs."""
        if not stage_info:
            return []

        stage_times = []
        for info in stage_info.split("/"):
            if match := re.match(r".*?(\d{2}\.\d{2}),\s*(.*)", info.strip()):
                time, stage = match.groups()
                stage_times.append({"time": time, "stage": stage})
        return stage_times

    def _get_start_timestamp(
        self, date: str, stage_times: List[Dict[str, str]]
    ) -> Optional[str]:
        """Convert date and time to ISO timestamp."""
        if not (date and stage_times):
            return None

        try:
            time_str = stage_times[0]["time"].replace(".", ":")
            return datetime.fromisoformat(f"{date}T{time_str}:00").isoformat()
        except ValueError:
            return None

    def fetch_lineup(self, sample_size=None) -> ScrapedData:
        """
        Fetch the festival lineup from the website.

        Args:
            sample_size: Maximum number of artists to fetch. If None, fetches all artists.

        Returns:
            ScrapedData: Raw scraped data including artist links and basic info
        """
        print("Fetching program page...")
        soup = BeautifulSoup(self.session.get(self.program_url).text, "html.parser")
        artist_cards = (
            soup.find_all("div", class_=re.compile(r"artistCard"))[:sample_size]
            if sample_size
            else soup.find_all("div", class_=re.compile(r"artistCard"))
        )

        print(f"Processing {len(artist_cards)} artists")
        artists_data = []

        for i, card in enumerate(artist_cards, 1):
            if link_element := card.find("a"):
                href = link_element.get("href", "")
                full_url = self.base_url + href if href else ""

                if content_div := card.find(
                    "div", class_=lambda c: c and "card_content" in c
                ):
                    if name := self._get_text(content_div.find("h2")):
                        print(
                            f"Fetching details for {name} ({i}/{len(artist_cards)})..."
                        )
                        artists_data.append(
                            {
                                "name": name,
                                "url": full_url,
                                **self._fetch_artist_details(full_url),
                            }
                        )

        return ScrapedData(
            source_url=self.program_url,
            raw_content={"artists": artists_data},
            festival_name=self.festival_name,
        )

    def _fetch_artist_details(self, url: str) -> Dict:
        """Fetch detailed information from artist's page."""
        soup = BeautifulSoup(self.session.get(url).text, "html.parser")

        # Get performance date and stage info
        performance_date = self.DATE_MAPPING.get(
            self._get_text(self._find_element(soup, "showTimesDay")).lower().strip()
        )
        stage_info = self._get_text(self._find_element(soup, "showTimesLocation"))
        stage_times = self._parse_stage_info(stage_info)

        # Get country codes
        country_element = soup.find(
            "sup", class_=lambda c: c and "typography_superscript" in c
        )
        country_codes = (
            [c.strip() for c in country_element.text.split("/")]
            if country_element
            else None
        )

        # Get descriptions
        short_desc = self._get_text(
            soup.find("h2", class_=lambda c: c and "headlineSmall" in c)
        )

        long_desc_element = self._find_element(soup, "rich-text_component")
        if long_desc_element:
            for br in long_desc_element.find_all("br"):
                br.replace_with("\n")
            for p in long_desc_element.find_all("p"):
                p.append("\n")
            long_desc = long_desc_element.get_text().strip()
        else:
            long_desc = None

        # Get Spotify link
        spotify_links = soup.find_all(
            "a", href=lambda x: x and "open.spotify.com/artist" in x
        )
        spotify_link = spotify_links[0]["href"].split("?")[0] if spotify_links else None

        return {
            "performance_date": performance_date,
            "stage": stage_times[0]["stage"] if stage_times else None,
            "start_ts": self._get_start_timestamp(performance_date, stage_times),
            "short_description": short_desc,
            "long_description": long_desc,
            "spotify_link": spotify_link,
            "country_code": country_codes,
        }
