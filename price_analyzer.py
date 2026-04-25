"""
price_analyzer.py - Price Analysis & Decision Engine
Analyzes mandi data to give farmers actionable insights.
Note: modal_price from data.gov.in API is already an integer (₹/quintal).
"""

import statistics
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Valid price range per quintal (same as working code)
MIN_VALID_PRICE = 500
MAX_VALID_PRICE = 10000


def to_int_price(value) -> int | None:
    """Parse modal_price — API returns int but guard against strings."""
    try:
        p = int(float(str(value).replace(",", "")))
        if MIN_VALID_PRICE <= p <= MAX_VALID_PRICE:
            return p
    except (ValueError, TypeError):
        pass
    return None


def quintal_to_kg(price_per_quintal: float) -> float:
    return round(price_per_quintal / 100, 2)


def clean_records(records: list[dict]) -> list[dict]:
    """Keep only records with valid modal prices; deduplicate by mandi (keep highest)."""
    mandi_best: dict[str, dict] = {}

    for r in records:
        price = to_int_price(r.get("modal_price"))
        if price is None:
            continue
        market = r.get("market", "Unknown")
        if market not in mandi_best or price > mandi_best[market]["_modal"]:
            r["_modal"] = price
            mandi_best[market] = r

    cleaned = list(mandi_best.values())
    logger.info(f"Cleaned: {len(cleaned)} unique mandis from {len(records)} records")
    return cleaned


def get_median_price(records: list[dict]) -> float | None:
    prices = [r["_modal"] for r in records]
    return round(statistics.median(prices), 2) if prices else None


def get_best_mandi(records: list[dict]) -> dict | None:
    if not records:
        return None
    median = get_median_price(records)
    # Best mandi = closest to median (same logic as working code)
    best = min(records, key=lambda r: abs(r["_modal"] - median))
    return {
        "market":   best.get("market", "N/A"),
        "district": best.get("district", "N/A"),
        "state":    best.get("state", "N/A"),
        "price":    best["_modal"],
        "price_kg": quintal_to_kg(best["_modal"]),
    }


def get_state_comparison(records: list[dict], top_n: int = 5) -> list[dict]:
    """Average price per state, top N.
    Accepts both raw records (has modal_price) and cleaned records (has _modal).
    """
    state_prices: dict[str, list[int]] = defaultdict(list)
    for r in records:
        # Prefer _modal (set by clean_records) — fall back to raw modal_price
        if "_modal" in r:
            price = r["_modal"]
        else:
            price = to_int_price(r.get("modal_price"))
        if price is not None:
            state_prices[r.get("state", "Unknown")].append(price)

    state_avgs = [
        {
            "state":      state,
            "avg":        int(sum(p) / len(p)),
            "avg_kg":     quintal_to_kg(int(sum(p) / len(p))),
            "num_mandis": len(p),
        }
        for state, p in state_prices.items() if p
    ]
    state_avgs.sort(key=lambda x: x["avg"], reverse=True)
    return state_avgs[:top_n]


def get_sell_advice(median_price: float) -> dict:
    """Fixed thresholds matching the original working logic."""
    if median_price > 3000:
        return {"label": "SELL NOW",         "emoji": "📈", "trend": "Prices are high"}
    elif median_price >= 2000:
        return {"label": "SELL IN 1-2 DAYS", "emoji": "⚖️", "trend": "Prices are moderate"}
    else:
        return {"label": "WAIT",             "emoji": "📉", "trend": "Prices are low"}


def calculate_revenue(price_per_quintal: float, quantity_kg: float) -> dict:
    price_per_kg  = quintal_to_kg(price_per_quintal)
    total_revenue = round(price_per_kg * quantity_kg, 2)
    return {
        "price_per_kg":  price_per_kg,
        "quantity_kg":   quantity_kg,
        "total_revenue": total_revenue,
    }


def analyze(records: list[dict], quantity_kg: float = 0) -> dict | None:
    cleaned = clean_records(records)
    if not cleaned:
        return None

    median = get_median_price(cleaned)
    return {
        "num_records":  len(cleaned),
        "median_price": median,
        "median_kg":    quintal_to_kg(median),
        "best_mandi":   get_best_mandi(cleaned),
        "advice":       get_sell_advice(median),
        "revenue":      calculate_revenue(median, quantity_kg) if quantity_kg > 0 else None,
    }