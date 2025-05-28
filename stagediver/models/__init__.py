"""
Core data models and data validation.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class ScrapedData(BaseModel):
    """Raw data scraped from festival websites"""

    source_url: str
    scrape_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    raw_content: dict
    festival_name: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


__all__ = ["ScrapedData"]
