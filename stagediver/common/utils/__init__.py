"""
General utility functions used across modules.
Contains:
- Date/time handling
- ID generation (nanoid)
- Data validation helpers
- Common transformations
"""

import json
import os
from typing import Any, Dict, List


def load_json_file(filepath: str) -> Any:
    """Load and parse a JSON file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(data: Any, filepath: str) -> None:
    """Save data to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
