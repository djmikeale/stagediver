# Stagediver Design Document

# Core components
- Web scraping module for festival websites
- Standardized festival data format:
- Support for multiple festival formats/layouts
- Regular update mechanism for lineup changes

| Field          | Type     | Required | Description                                    |
| -------------- | -------- | -------- | ---------------------------------------------- |
| festival_name  | string   | y        | Reference to parent festival                   |
| artist_name    | string   | y        | Official artist/band name                      |
| stage_name     | string   | y        | Performance location                           |
| start_ts       | datetime | y        | Performance start (ISO 8601)                   |
| end_ts         | datetime | y        | Performance end (ISO 8601)                     |
| social_links   | map      | n        | Map of platform name to profile URL            |
| bio_short      | string   | n        | 1-2 sentence description                       |
| bio_long       | string   | n        | Full artist biography                          |
| country_code   | string   | n        | Artist's origin country (ISO 3166-1)           |
| scrape_url     | string   | n        | URL where data was scraped from                |
| scrape_ts      | datetime | n        | When the record was last modified              |
| other_data     | map      | n        | misc. data, e.g. used for later llm enrichment |

### 2. Transformations + enrichment
- Artist metadata collection (genres, popularity, similar artists)
- keep track of historical changes, e.g. lineup changes
- core data, e.g. genres, country, festival name + stages, etc.



### 3. user ratings
- easy way to export artists to google sheets
- easy way to listen and rate artists
- easy way to import artists from google sheets

<details closed>
<summary>google sheet design</summary>

## Festival Rating System in Google Sheets

### 1. Artists Sheet
Stores the list of artists with unique IDs.

| Artist ID | Artist Name  |
|-----------|-------------|
| 1         | Band A      |
| 2         | Band B      |
| 3         | Band C      |

### 2. Ratings Sheet
Users rate artists on a scale (e.g., 1-10). Each user gets a column.

| Artist ID | Artist Name | User 1 | User 2 | User 3 |
|-----------|------------|--------|--------|--------|
| 1         | Band A     | 7      | 8      | 6      |
| 2         | Band B     | 9      | 6      | 7      |
| 3         | Band C     | 5      | 7      | 8      |

### 5. CSV Export Sheet
Formats data for easy CSV export and Python processing.

| Artist ID | Artist Name | User  | Score |
|-----------|------------|------|------|
| 1         | Band A     | User 1 | 7 |
| 1         | Band A     | User 2 | 8 |
| 2         | Band B     | User 1 | 9 |

Using `FLATTEN()`:
```excel
=FLATTEN(Ratings!A2:A & "|" & Ratings!B2:B & "|" & Ratings!C1:E1 & "|" & Ratings!C2:E)
```

### Design Summary
- **Artists Sheet**: Stores artists with unique IDs.
- **Ratings Sheet**: Users rate artists in a structured format.
- **CSV Export Sheet**: Flattens data for export and Python processing.
- **Ease of Use**: Allows dynamic user additions and simple data exports.

Data can be exported via **File > Download > CSV** for further analysis in Python.

</details>

### 4. Schedule alerts
- internal conflict (user wanna see 2 different artists playing at same time)
- external conflict (your friends want to see some other artist at this time)
- too many artists to see during the day


### 5. Calendar export

- Calendar export functionality
