"""
src/canonical_data.py
Authoritative loader and accessor for the canonical simulation results artifact:
outputs/canonical_profile_results.json
"""

import json
import os
from typing import Dict, Any

_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "canonical_profile_results.json")


def get_canonical_results() -> Dict[str, Any]:
    """
    Returns the loaded canonical results JSON dictionary.
    If the file does not exist, automatically generates it first.
    """
    if not os.path.exists(_JSON_PATH):
        from src.generate_canonical_results import save_canonical_results
        save_canonical_results(_JSON_PATH)

    with open(_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
