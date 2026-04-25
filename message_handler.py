"""
message_handler.py - WhatsApp Message Parser & Response Formatter
Multi-language: English, Hindi, Kannada
"""

import re
import logging
from mandi_api import fetch_mandi_data, fetch_all_states_data
from price_analyzer import analyze, get_state_comparison, clean_records
from blockchain import log_query
from lang import detect_language, normalize_input, localize_advice, localize_state, t, currency

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PARSE
# ---------------------------------------------------------------------------

def parse_message(text: str) -> dict | None:
    """
    Works entirely on English-normalised text.
    Called AFTER detect_language + normalize_input, so no script awareness needed here.
    """
    text = text.lower().strip()

    if text in ("help", "hi", "hello", "start", "/start"):
        return {"command": "help"}

    m = re.match(r"compare\s+(\w+)", text)
    if m:
        return {"command": "compare", "commodity": m.group(1)}

    qty_match = re.search(r"(\d+)\s*$", text)
    quantity  = float(qty_match.group(1)) if qty_match else 0
    rest      = text[: qty_match.start()].strip() if qty_match else text

    known_states = [
        "uttar pradesh", "madhya pradesh", "andhra pradesh",
        "west bengal", "tamil nadu", "karnataka", "maharashtra",
        "gujarat", "rajasthan", "punjab", "haryana", "kerala",
        "bihar", "odisha", "chhattisgarh", "telangana",
    ]

    state_found = None
    for s in sorted(known_states, key=len, reverse=True):
        if s in rest:
            state_found = s
            rest = rest.replace(s, "").strip()
            break

    commodity = rest.strip()
    if not commodity:
        return None

    return {"command": "query", "commodity": commodity,
            "state": state_found or "", "quantity": quantity}


# ---------------------------------------------------------------------------
# RESPONSE BUILDERS  (all accept lang parameter)
# ---------------------------------------------------------------------------

def build_query_response(commodity: str, state: str, quantity: float,
                         sender: str, lang: str) -> str:
    records = fetch_mandi_data(commodity, state if state else None)

    if not records:
        state_part = t("state_part_in", lang, state=state) if state else ""
        return t("no_data", lang, commodity=commodity, state_part=state_part)

    result = analyze(records, quantity_kg=quantity)
    if not result:
        return t("invalid_price", lang, commodity=commodity)

    median    = result["median_price"]
    median_kg = result["median_kg"]
    best      = result["best_mandi"]
    advice    = localize_advice(result["advice"], lang)   # translated advice

    all_records = fetch_all_states_data(commodity)
    all_cleaned = clean_records(all_records)
    top_states  = get_state_comparison(all_cleaned, top_n=5) if all_cleaned else []
    best_state_en = top_states[0]["state"] if top_states else (best["state"] if best else "")
    best_state    = localize_state(best_state_en, lang) if best_state_en else t("na", lang)

    try:
        record_id = log_query(sender, commodity, state, quantity, result)[:12]
    except Exception:
        record_id = "N/A"

    # Localize state names in the top-states list
    compare_text = "\n".join(
        f"{localize_state(s['state'], lang)}: {currency(lang)}{s['avg']:.0f}"
        for s in top_states
    )

    best_market = best["market"] if best else t("na", lang)

    return (
        f"📊 {t('crop_price', lang)}: {currency(lang)}{median:.0f}/quintal\n"
        f"💰 ~{currency(lang)}{median_kg:.2f}/{t('per_kg', lang)}\n\n"
        f"📍 {t('best_mandi', lang)}: {best_market}\n\n"
        f"🏆 {t('best_state', lang)}: {best_state}\n\n"
        f"📈 {advice['trend']}\n"
        f"💡 {t('advice', lang)}: {advice['label']}\n\n"
        f"📊 {t('top_states', lang)}:\n{compare_text}\n\n"
        f"🔗 {t('id', lang)}: {record_id}"
    )


def build_compare_response(commodity: str, lang: str) -> str:
    records   = fetch_all_states_data(commodity)
    cleaned   = clean_records(records)

    if not cleaned:
        return t("no_data_compare", lang, commodity=commodity)

    top_states = get_state_comparison(cleaned, top_n=5)
    if not top_states:
        return t("not_enough_compare", lang, commodity=commodity)

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    lines  = [f"🌍 {t('state_comparison', lang)} — {commodity.title()}\n"]
    for i, s in enumerate(top_states):
        # Localize state name to user's language
        lines.append(
            f"{medals[i]} {localize_state(s['state'], lang)}  {currency(lang)}{s['avg']}/qtl  ({s['num_mandis']} {t('mandis', lang)})"
        )
    lines.append(f"\n{t('sell_top_state', lang)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def handle_message(text: str, sender: str, is_voice: bool = False) -> str:
    # 1. Detect language from the raw text
    lang = detect_language(text)

    # 2. If voice input, strip filler words Whisper adds ("price of", "rate", etc.)
    if is_voice:
        text = clean_voice_transcript(text)
        logger.info(f"Voice cleaned transcript: {text!r}")

    # 3. Normalise native-script words to English so parser works unchanged
    normalised = normalize_input(text, lang)

    # 4. Parse the normalised text
    parsed = parse_message(normalised)

    if parsed is None:
        return t("didnt_understand", lang)

    cmd = parsed["command"]

    if cmd == "help":
        return t("help", lang)

    if cmd == "compare":
        return build_compare_response(parsed["commodity"], lang)

    if cmd == "query":
        return build_query_response(
            parsed["commodity"], parsed["state"],
            parsed["quantity"], sender, lang
        )

    return t("unknown_cmd", lang)