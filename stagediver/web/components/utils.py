def get_artists_for_festival_year(data, festival, year):
    """Get all artists for a specific festival and year"""
    return [
        artist
        for artist in data
        if artist["festival_name"] == festival
        and artist["festival_year"] == year
        and artist.get("_is_current", False)  # Only show current artists
    ]
