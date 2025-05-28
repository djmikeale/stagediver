def get_artists_for_festival_year(data, festival, year):
    """Get all artists for a specific festival and year"""
    # Check if the data matches the requested festival and year
    if data["festival_name"] == festival and data["festival_year"] == year:
        return [artist for artist in data["artists"]]
    return []
