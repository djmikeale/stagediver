# Stagediver Design Document

## 1. Data Collection & Processing

### 1.1 Web Scraping
- Web scraping module for festival websites
- Regular update mechanism for lineup changes
- Support for multiple festival formats/layouts

### 1.2 Data Enrichment
- Artist metadata collection (genres, popularity, similar artists)
- Track historical changes (e.g. lineup changes)
- Data quality checks and validation
- Core data enrichment (genres, country, etc.)

## 2. Data Models

### 2.1 Scraping Data Model
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
| country_code   | string   | n        | Artist's origin country (ISO 3166-1)          |
| scrape_url     | string   | n        | URL where data was scraped from               |
| scrape_ts      | datetime | n        | When the record was last modified             |
| other_data     | map      | n        | Misc. data for later enrichment               |

### 2.2 Core Data Models

- Artist metadata collection (genres, popularity, similar artists)
- keep track of historical changes, e.g. lineup changes
- core data, e.g. genres, country, festival name + stages, etc.
- data quality checks, e.g. key constraints, when has data been updated, etc.

#### Festival
| Field      | Type     | Required | Description               |
| ---------- | -------- | -------- | ------------------------- |
| id         | nanoid   | y        | Primary key               |
| name       | string   | y        | Festival name             |
| location   | string   | y        | City, Country             |
| website    | string   | y        | Official festival website |
| start_date | date     | y        | Festival start date       |
| end_date   | date     | y        | Festival end date         |
| created_at | datetime | y        | Record creation timestamp |
| updated_at | datetime | y        | Last update timestamp     |

#### Stage
| Field       | Type     | Required | Description                          |
| ----------- | -------- | -------- | ------------------------------------ |
| id          | nanoid   | y        | Primary key                          |
| festival_id | nanoid   | y        | Reference to festival                |
| name        | string   | y        | Stage name                           |
| capacity    | int      | n        | Maximum audience capacity            |
| location    | string   | n        | GPS coordinates or relative location |
| created_at  | datetime | y        | Record creation timestamp            |
| updated_at  | datetime | y        | Last update timestamp                |

#### Artist
| Field        | Type     | Required | Description                         |
| ------------ | -------- | -------- | ----------------------------------- |
| id           | nanoid   | y        | Primary key                         |
| name         | string   | y        | Artist/band name                    |
| genres       | string[] | n        | Musical genres                      |
| mood_tags    | string[] | n        | List of mood tags                   |
| similar_to   | string[] | n        | List of similar artists            |
| country_code | string   | n        | ISO 3166-1 country code            |
| social_links | map      | n        | Platform to URL mapping            |
| bio_short    | string   | n        | Brief description                  |
| bio_long     | string   | n        | Full biography                     |
| created_at   | datetime | y        | Record creation timestamp          |
| updated_at   | datetime | y        | Last update timestamp              |

#### Performance
| Field              | Type     | Required | Description                       |
| ------------------ | -------- | -------- | --------------------------------- |
| id                 | nanoid   | y        | Primary key                       |
| festival_id        | nanoid   | y        | Reference to festival             |
| artist_id          | nanoid   | y        | Reference to artist               |
| stage_id           | nanoid   | y        | Reference to stage                |
| start_ts           | datetime | y        | Performance start time            |
| end_ts             | datetime | y        | Performance end time              |
| valid_from         | datetime | y        | When this version becomes valid   |
| valid_to           | datetime | n        | When this version becomes invalid |
| is_cancelled       | boolean  | y        | Whether performance is cancelled  |
| created_at         | datetime | y        | Record creation timestamp         |
| scraper_version_id | nanoid   | y        | Reference to scraper version      |

#### Rating
| Field        | Type     | Required | Description                  |
| ------------ | -------- | -------- | ---------------------------- |
| id           | nanoid   | y        | Primary key                  |
| user_id      | nanoid   | y        | Reference to user            |
| artist_id    | nanoid   | y        | Reference to artist          |
| festival_id  | nanoid   | y        | Reference to festival        |
| score        | int      | y        | Rating score (1-10)          |
| notes        | string   | n        | User notes about artist      |
| created_at   | datetime | y        | Record creation timestamp    |
| updated_at   | datetime | y        | Last update timestamp        |

### 2.3 Implementation Notes
- Using [nanoid](https://github.com/puyuan/py-nanoid) for IDs instead of UUID
- Initially using hash of artist name as ID, later handle misspellings/aliases

## 3. User Rating System

### 3.1 Google Sheets Integration
- Export artists to Google Sheets for rating
- Import rated artists from Google Sheets
- Data validation and completion tracking
- Structured sheets:
  - Artists Sheet (ID, Name)
  - Ratings Sheet (ID, Name, per-user ratings column)
  - Export Sheet (flattened data for processing)

### 3.2 Mood Tags
- 🌅 Hangover - Chill, relaxed vibes
- 💪 Fistpump - High energy dance
- 🤘 Moshpit - Heavy, intense
- 🌿 Zen - Ambient, atmospheric
- 🎭 Emotional - Deep, moving
- 🕺 Groovy - Funky, rhythmic
- 🌙 Late Night - Dark, electronic
- 🎪 Party - Fun, upbeat
- 🌊 Wave - Dreamy, floating
- 🔥 Hype - Energetic, exciting

## 4. Visualization
- Streamlit app for schedule visualization
- Interactive conflict resolution
- Rating summaries and statistics
- Conflict types:
  - Internal (user wants to see overlapping performances)
  - External (friend group schedule conflicts)
  - Overbooked time periods

### 5 Calendar Export
- Export ratings: ❤️,🟢,🟡,🟤,🚫
- Configurable export options:
  - Per-user filtering
  - Include stage information
  - Start/end times
  - Custom fields
  - Full schedule export without ratings
