"""
Core data models and data validation.
Contains Pydantic models for:
- Festival
- Stage
- Artist
- Performance
"""
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional

class Artist(BaseModel):
    id: str
    name: str
    genre: Optional[str] = None
    spotify_id: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)

class Stage(BaseModel):
    id: str
    name: str
    location: Optional[str] = None

class Performance(BaseModel):
    artist_id: str
    stage_id: str
    start_time: datetime
    end_time: datetime

class Festival(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    location: str
    stages: List[Stage] = []
    performances: List[Performance] = []

class ScrapedData(BaseModel):
    """Raw data scraped from festival websites"""
    source_url: str
    scrape_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_content: dict
    festival_name: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

# Export the models
__all__ = ['Festival', 'Stage', 'Artist', 'Performance', 'ScrapedData']
