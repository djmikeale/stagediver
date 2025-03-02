from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

from stagediver.common.utils import load_json_file, save_json_file

from .models import Artist, Festival, Performance, Stage


class DataStore:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Define file paths
        self.festival_file = self.data_dir / "festival.json"
        self.artists_file = self.data_dir / "artists.json"
        self.stages_file = self.data_dir / "stages.json"
        self.schedule_file = self.data_dir / "schedule.json"

    def _json_encoder(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def save_festival(self, festival: Festival):
        save_json_file(festival.model_dump(), str(self.festival_file))

    def load_festival(self) -> Optional[Festival]:
        try:
            data = load_json_file(str(self.festival_file))
            return Festival.model_validate(data) if data else None
        except FileNotFoundError:
            return None

    def save_artist(self, artist: Artist):
        artists = self.load_artists()
        artists[artist.id] = artist.model_dump()
        save_json_file(artists, str(self.artists_file))

    def load_artists(self) -> Dict:
        try:
            return load_json_file(str(self.artists_file))
        except FileNotFoundError:
            return {}

    def get_artist(self, artist_id: str) -> Optional[Artist]:
        artists = self.load_artists()
        if artist_id in artists:
            return Artist.model_validate(artists[artist_id])
        return None
