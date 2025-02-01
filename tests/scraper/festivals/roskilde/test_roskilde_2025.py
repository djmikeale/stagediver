"""
Test cases for the Roskilde Festival 2025 scraper.
"""

import pytest
from bs4 import BeautifulSoup
from stagediver.scraper.festivals.roskilde import RoskildeFestival2025Scraper
from stagediver.models import ScrapedData

def test_scraper_initialization():
    """Test that the scraper can be initialized with correct year."""
    scraper = RoskildeFestival2025Scraper()
    assert scraper.year == 2025
    assert scraper.festival_name == "Roskilde Festival"
    assert scraper.program_url == "https://www.roskilde-festival.dk/program"

def test_parse_artist_card():
    """Test parsing of an artist card from the program page."""
    scraper = RoskildeFestival2025Scraper()

    # Sample HTML structure matching the actual website
    html = """
    <div class="line-up-overview-cards_artistCard__WFH6G">
        <a href="/program/olivia-rodrigo">
            <div class="card_content__NCkf_">
                <h2>Olivia Rodrigo</h2>
            </div>
        </a>
    </div>
    """

    soup = BeautifulSoup(html, 'html.parser')
    card = soup.find('div', class_='line-up-overview-cards_artistCard__WFH6G')
    link_element = card.find('a')
    content_div = card.find('div', class_='card_content__NCkf_')

    assert link_element['href'] == "/program/olivia-rodrigo"
    assert content_div.find('h2').text.strip() == "Olivia Rodrigo"

@pytest.mark.integration
def test_fetch_lineup():
    """Test that the scraper can fetch the festival lineup."""
    scraper = RoskildeFestival2025Scraper()
    data = scraper.fetch_lineup()
    assert isinstance(data, ScrapedData)
    assert data.festival_name == "Roskilde Festival"
    assert "artists" in data.raw_content
    assert len(data.raw_content["artists"]) > 0

    # Check structure of first artist entry
    first_artist = data.raw_content["artists"][0]
    assert "name" in first_artist
    assert "url" in first_artist
    assert first_artist["url"].startswith("https://www.roskilde-festival.dk/program/")
