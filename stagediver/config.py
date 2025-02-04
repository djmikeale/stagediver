"""
Central configuration for the stagediver package.
Contains shared constants and configuration values.
"""

import os

# Data file paths
DATA_DIR = "data"
LINEUPS_FILE = os.path.join(DATA_DIR, "lineups.json")
HISTORICAL_FILE = os.path.join(DATA_DIR, "lineups_historical.json")
