from datetime import datetime
from stagediver.models import Festival, Artist
from stagediver.storage import DataStore

# Initialize storage
store = DataStore()

# Create and save a festival
festival = Festival(
    name="Roskilde 2025",
    start_date=datetime(2025, 6, 28),
    end_date=datetime(2025, 7, 5),
    location="Roskilde, Denmark"
)
store.save_festival(festival)

# Create and save an artist
artist = Artist(
    id="artist1",
    name="The Band",
    genre="Rock",
    spotify_id="xyz123"
)
store.save_artist(artist)

# Load data
loaded_festival = store.load_festival()
loaded_artist = store.get_artist("artist1")
