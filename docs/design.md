# Stagediver Design Document

## 1. Overview
Contains current design specifications and data models for the Stagediver application.

## 2. Data Models

### 2.1 Core Entities

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

### 2.2 Mood Tags
Used to categorize artist performances:

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

## 3. Features

### 3.1 Data Collection
- Artist metadata collection (genres, popularity, similar artists)
- Historical change tracking (e.g., lineup changes)
- Core data management (genres, country, festival details, stages)
- Data quality validation and constraints

### 3.2 Streamlit Application
- Interactive schedule visualization
- Rating summaries and statistics
- Conflict detection and management:
  - Internal conflicts (overlapping performances of interest)
  - External conflicts (group schedule coordination)
- Schedule export functionality (with optional ratings)
