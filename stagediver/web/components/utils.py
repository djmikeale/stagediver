def get_artists_for_festival_year(data_list, festival, year):
    """Get all artists for a specific festival and year"""
    for data in data_list:
        if data.get("festival_name") == festival and data.get("festival_year") == year:
            return data["artists"]
    return []


def get_data_for_festival_year(data_list, festival, year):
    """Get the data dict for a specific festival and year"""
    for data in data_list:
        if data.get("festival_name") == festival and data.get("festival_year") == year:
            return data
    return None
