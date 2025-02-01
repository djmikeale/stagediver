from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .models import Festival, Artist, Stage, Performance

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

    def _save_json(self, data: Dict, file_path: Path):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=self._json_encoder)

    def _load_json(self, file_path: Path) -> Dict:
        if not file_path.exists():
            return {}
        with open(file_path, 'r') as f:
            return json.load(f)

    def save_festival(self, festival: Festival):
        self._save_json(festival.model_dump(), self.festival_file)

    def load_festival(self) -> Optional[Festival]:
        data = self._load_json(self.festival_file)
        return Festival.model_validate(data) if data else None

    def save_artist(self, artist: Artist):
        artists = self._load_json(self.artists_file)
        artists[artist.id] = artist.model_dump()
        self._save_json(artists, self.artists_file)

    def get_artist(self, artist_id: str) -> Optional[Artist]:
        artists = self._load_json(self.artists_file)
        if artist_id in artists:
            return Artist.model_validate(artists[artist_id])
        return None
