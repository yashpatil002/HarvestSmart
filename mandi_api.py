"""
mandi_api.py - Government Agmarknet Data API Integration
Fetches live mandi (market) prices from data.gov.in
"""

import requests
import os
import logging

logger = logging.getLogger(__name__)

BASE_URL = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY  = os.getenv("DATA_GOV_API_KEY", "579b464db66ec23bdd000001400f7172681c428b787794fd080690a8")


def fetch_mandi_data(commodity: str, state: str | None = None, limit: int = 500) -> list[dict]:
    """
    Fetch records from data.gov.in and filter locally.
    (The API's filter params are unreliable — we filter in Python.)
    """
    url = f"{BASE_URL}?api-key={API_KEY}&format=json&limit={limit}"

    try:
        logger.info(f"Fetching mandi data (commodity={commodity}, state={state})")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        records = response.json().get("records", [])
        logger.info(f"Total records fetched: {len(records)}")
    except Exception as e:
        logger.error(f"API fetch failed: {e}")
        return []

    # Filter locally — same approach as working code
    filtered = [
        r for r in records
        if r.get("commodity", "").lower() == commodity.lower()
        and (state is None or r.get("state", "").lower() == state.lower())
    ]

    logger.info(f"After filter: {len(filtered)} records")
    return filtered


def fetch_all_states_data(commodity: str, limit: int = 500) -> list[dict]:
    """Fetch records for a crop across all states."""
    return fetch_mandi_data(commodity, state=None, limit=limit)