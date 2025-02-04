"""
Configuration management.
Contains:
- Configuration loading
- Environment variable handling
- Default settings
"""

import os

# Data file paths
DATA_DIR = "data"
LINEUPS_FILE = os.path.join(DATA_DIR, "lineups.json")
HISTORICAL_FILE = os.path.join(DATA_DIR, "lineups_historical.json")
