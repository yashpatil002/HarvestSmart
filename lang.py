"""
lang.py - Multi-language support for HarvestSmart
Supports: English (en), Hindi (hi), Kannada (kn)

Responsibilities:
  1. detect_language(text) -> "en" | "hi" | "kn"
  2. normalize_input(text, lang) -> English commodity + state names
     so the rest of the pipeline never needs to change.
  3. t(key, lang, **kwargs) -> translated string
"""

import re

# ---------------------------------------------------------------------------
# 1. LANGUAGE DETECTION
# ---------------------------------------------------------------------------

# Unicode ranges
_DEVANAGARI = re.compile(r'[\u0900-\u097F]')   # Hindi
_KANNADA    = re.compile(r'[\u0C80-\u0CFF]')   # Kannada

def detect_language(text: str) -> str:
    """Return 'hi', 'kn', or 'en' based on script detection."""
    if _KANNADA.search(text):
        return "kn"
    if _DEVANAGARI.search(text):
        return "hi"
    return "en"


# ---------------------------------------------------------------------------
# 2. COMMODITY NAME MAPS  (native script -> English API name)
# ---------------------------------------------------------------------------

COMMODITY_MAP: dict[str, str] = {
    # --- Hindi ---
    "टमाटर":      "tomato",
    "प्याज":      "onion",
    "आलू":        "potato",
    "गेहूं":      "wheat",
    "चावल":       "rice",
    "मक्का":      "maize",
    "सरसों":      "mustard",
    "मिर्च":      "chilli",
    "लहसुन":      "garlic",
    "अदरक":       "ginger",
    "बैंगन":      "brinjal",
    "भिंडी":      "ladyfinger",
    "गोभी":       "cauliflower",
    "पत्तागोभी":  "cabbage",
    "मूंग":       "moong",
    "उड़द":       "urad",
    "चना":        "gram",
    "सोयाबीन":    "soyabean",
    "कपास":       "cotton",
    "गन्ना":      "sugarcane",

    # --- Kannada ---
    "ಟೊಮೆಟೊ":     "tomato",
    "ಈರುಳ್ಳಿ":    "onion",
    "ಆಲೂಗಡ್ಡೆ":  "potato",
    "ಗೋಧಿ":       "wheat",
    "ಅಕ್ಕಿ":      "rice",
    "ಮೆಕ್ಕೆಜೋಳ": "maize",
    "ಸಾಸಿವೆ":     "mustard",
    "ಮೆಣಸಿನಕಾಯಿ": "chilli",
    "ಬೆಳ್ಳುಳ್ಳಿ": "garlic",
    "ಶುಂಠಿ":      "ginger",
    "ಬದನೆಕಾಯಿ":  "brinjal",
    "ಬೆಂಡೆಕಾಯಿ":  "ladyfinger",
    "ಹೂಕೋಸು":    "cauliflower",
    "ಎಲೆಕೋಸು":   "cabbage",
    "ಹೆಸರುಕಾಳು":  "moong",
    "ಉದ್ದಿನಕಾಳು": "urad",
    "ಕಡಲೆ":       "gram",
    "ಸೋಯಾಬೀನ್":  "soyabean",
    "ಹತ್ತಿ":      "cotton",
    "ಕಬ್ಬು":      "sugarcane",
}

# ---------------------------------------------------------------------------
# 3. STATE NAME MAPS  (native script -> English API name)
# ---------------------------------------------------------------------------

STATE_MAP: dict[str, str] = {
    # --- Hindi ---
    "कर्नाटक":        "karnataka",
    "महाराष्ट्र":     "maharashtra",
    "उत्तर प्रदेश":   "uttar pradesh",
    "मध्य प्रदेश":    "madhya pradesh",
    "आंध्र प्रदेश":   "andhra pradesh",
    "पश्चिम बंगाल":   "west bengal",
    "तमिल नाडु":      "tamil nadu",
    "गुजरात":         "gujarat",
    "राजस्थान":       "rajasthan",
    "पंजाब":          "punjab",
    "हरियाणा":        "haryana",
    "केरल":           "kerala",
    "बिहार":          "bihar",
    "ओडिशा":          "odisha",
    "छत्तीसगढ़":      "chhattisgarh",
    "तेलंगाना":       "telangana",
    "नागालैंड":       "nagaland",

    # --- Kannada ---
    "ಕರ್ನಾಟಕ":       "karnataka",
    "ಮಹಾರಾಷ್ಟ್ರ":    "maharashtra",
    "ಉತ್ತರ ಪ್ರದೇಶ":  "uttar pradesh",
    "ಮಧ್ಯ ಪ್ರದೇಶ":   "madhya pradesh",
    "ಆಂಧ್ರ ಪ್ರದೇಶ":  "andhra pradesh",
    "ಪಶ್ಚಿಮ ಬಂಗಾಳ":  "west bengal",
    "ತಮಿಳು ನಾಡು":    "tamil nadu",
    "ಗುಜರಾತ್":       "gujarat",
    "ರಾಜಸ್ಥಾನ":      "rajasthan",
    "ಪಂಜಾಬ್":        "punjab",
    "ಹರಿಯಾಣ":        "haryana",
    "ಕೇರಳ":          "kerala",
    "ಬಿಹಾರ":         "bihar",
    "ಒಡಿಶಾ":         "odisha",
    "ಛತ್ತೀಸ್‌ಗಢ":    "chhattisgarh",
    "ತೆಲಂಗಾಣ":       "telangana",
    "ನಾಗಾಲ್ಯಾಂಡ್":  "nagaland",
}

# ---------------------------------------------------------------------------
# 3b. REVERSE STATE MAP  (English API name -> native script per language)
#     Built automatically from STATE_MAP above.
# ---------------------------------------------------------------------------

# Group native names by their English key, separated by language
_STATE_NATIVE: dict[str, dict[str, str]] = {}
for _native, _english in STATE_MAP.items():
    # Detect script of native name to assign language
    _lang = "kn" if _KANNADA.search(_native) else "hi"
    _STATE_NATIVE.setdefault(_english, {})["_any"] = _native   # last-write fallback
    _STATE_NATIVE[_english][_lang] = _native

# ---------------------------------------------------------------------------
# 3c. LOCALIZE NAMES  (English -> native for the user's language)
# ---------------------------------------------------------------------------

def localize_state(english_name: str, lang: str) -> str:
    """
    Translate an English state name returned by the API into the user's
    language.  Falls back to the original English string if no translation
    is found.
    """
    if lang == "en":
        return english_name
    key = english_name.strip().lower()
    entry = _STATE_NATIVE.get(key, {})
    return entry.get(lang) or entry.get("_any") or english_name


def localize_mandi(english_name: str, lang: str) -> str:
    """
    Mandi names are proper nouns — we keep them in English regardless of
    language, which is standard practice.  This function exists as a hook
    so callers are explicit about the decision.
    """
    return english_name   # mandi proper-noun names are not translated


# ---------------------------------------------------------------------------
# 4. COMMAND KEYWORD MAPS  (native -> English)
# ---------------------------------------------------------------------------

COMMAND_MAP: dict[str, str] = {
    # Hindi
    "मदद":    "help",
    "सहायता": "help",
    "नमस्ते": "help",
    "हेलो":   "help",
    "शुरू":   "help",
    "तुलना":  "compare",
    "compare": "compare",   # keep English passthrough

    # Kannada
    "ಸಹಾಯ":   "help",
    "ಹಲೋ":    "help",
    "ನಮಸ್ಕಾರ": "help",
    "ಪ್ರಾರಂಭ": "help",
    "ಹೋಲಿಕೆ": "compare",
}

# ---------------------------------------------------------------------------
# 5. NORMALIZE INPUT  ->  returns English text for the existing parser
# ---------------------------------------------------------------------------

def normalize_input(text: str, lang: str) -> str:
    """
    Replace native-script commodity names, state names, and command keywords
    with their English equivalents so parse_message() works unchanged.
    Sorting by length (longest first) avoids partial-match bugs.
    """
    if lang == "en":
        return text   # nothing to do

    normalized = text

    # Replace states (longest first to avoid partial matches)
    for native, english in sorted(STATE_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        normalized = normalized.replace(native, english)

    # Replace commodities
    for native, english in sorted(COMMODITY_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        normalized = normalized.replace(native, english)

    # Replace command keywords
    for native, english in sorted(COMMAND_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        # whole-word replacement (handles mixed scripts gracefully)
        normalized = re.sub(re.escape(native), english, normalized, flags=re.IGNORECASE)

    return normalized


# ---------------------------------------------------------------------------
# 6. TRANSLATIONS  — all UI strings
# ---------------------------------------------------------------------------

_T: dict[str, dict[str, str]] = {

    # ── HELP ────────────────────────────────────────────────────────────────
    "help": {
        "en": (
            "🌾 *HarvestSmart* — Your Farm Price Assistant\n\n"
            "*How to use:*\n"
            "`crop state quantity`\n\n"
            "*Examples:*\n"
            "• tomato karnataka 1000\n"
            "• onion maharashtra 500\n"
            "• wheat punjab 2000\n\n"
            "*Commands:*\n"
            "• help — Show this message\n"
            "• compare tomato — Compare across states\n\n"
            "_Prices from Govt of India (Agmarknet)_"
        ),
        "hi": (
            "🌾 *HarvestSmart* — आपका फसल मूल्य सहायक\n\n"
            "*उपयोग कैसे करें:*\n"
            "`फसल राज्य मात्रा`\n\n"
            "*उदाहरण:*\n"
            "• टमाटर कर्नाटक 1000\n"
            "• प्याज महाराष्ट्र 500\n"
            "• गेहूं पंजाब 2000\n\n"
            "*कमांड:*\n"
            "• मदद — यह संदेश दिखाएं\n"
            "• तुलना टमाटर — राज्यों में तुलना करें\n\n"
            "_भारत सरकार (Agmarknet) से कीमतें_"
        ),
        "kn": (
            "🌾 *HarvestSmart* — ನಿಮ್ಮ ಬೆಳೆ ಬೆಲೆ ಸಹಾಯಕ\n\n"
            "*ಹೇಗೆ ಬಳಸುವುದು:*\n"
            "`ಬೆಳೆ ರಾಜ್ಯ ಪ್ರಮಾಣ`\n\n"
            "*ಉದಾಹರಣೆಗಳು:*\n"
            "• ಟೊಮೆಟೊ ಕರ್ನಾಟಕ 1000\n"
            "• ಈರುಳ್ಳಿ ಮಹಾರಾಷ್ಟ್ರ 500\n"
            "• ಗೋಧಿ ಪಂಜಾಬ್ 2000\n\n"
            "*ಆದೇಶಗಳು:*\n"
            "• ಸಹಾಯ — ಈ ಸಂದೇಶ ತೋರಿಸು\n"
            "• ಹೋಲಿಕೆ ಟೊಮೆಟೊ — ರಾಜ್ಯಗಳ ನಡುವೆ ಹೋಲಿಕೆ\n\n"
            "_ಭಾರತ ಸರ್ಕಾರ (Agmarknet) ಬೆಲೆಗಳು_"
        ),
    },

    # ── QUERY RESPONSE LABELS ───────────────────────────────────────────────
    "crop_price":  {"en": "Crop Price",     "hi": "फसल मूल्य",       "kn": "ಬೆಳೆ ಬೆಲೆ"},
    "per_kg":      {"en": "per kg",         "hi": "प्रति किलो",      "kn": "ಪ್ರತಿ ಕೆಜಿ"},
    "best_mandi":  {"en": "Best Mandi",     "hi": "सर्वश्रेष्ठ मंडी","kn": "ಅತ್ಯುತ್ತಮ ಮಂಡಿ"},
    "best_state":  {"en": "Best State",     "hi": "सर्वश्रेष्ठ राज्य","kn": "ಅತ್ಯುತ್ತಮ ರಾಜ್ಯ"},
    "advice":      {"en": "Advice",         "hi": "सलाह",             "kn": "ಸಲಹೆ"},
    "top_states":  {"en": "Top States",     "hi": "शीर्ष राज्य",     "kn": "ಉತ್ತಮ ರಾಜ್ಯಗಳು"},
    "id":          {"en": "ID",             "hi": "ID",               "kn": "ID"},
    "na":          {"en": "N/A",            "hi": "उपलब्ध नहीं",     "kn": "ಲಭ್ಯವಿಲ್ಲ"},

    # ── ADVICE LABELS ───────────────────────────────────────────────────────
    "sell_now":    {"en": "SELL NOW",         "hi": "अभी बेचें",          "kn": "ಈಗಲೇ ಮಾರಿ"},
    "sell_soon":   {"en": "SELL IN 1-2 DAYS", "hi": "1-2 दिन में बेचें",  "kn": "1-2 ದಿನದಲ್ಲಿ ಮಾರಿ"},
    "wait":        {"en": "WAIT",             "hi": "प्रतीक्षा करें",     "kn": "ಕಾಯಿರಿ"},

    # ── ADVICE TRENDS ───────────────────────────────────────────────────────
    "prices_high": {"en": "Prices are high",     "hi": "कीमतें ऊँची हैं",       "kn": "ಬೆಲೆಗಳು ಹೆಚ್ಚಾಗಿವೆ"},
    "prices_mod":  {"en": "Prices are moderate", "hi": "कीमतें मध्यम हैं",      "kn": "ಬೆಲೆಗಳು ಮಧ್ಯಮ ಮಟ್ಟದಲ್ಲಿವೆ"},
    "prices_low":  {"en": "Prices are low",      "hi": "कीमतें कम हैं",         "kn": "ಬೆಲೆಗಳು ಕಡಿಮೆ ಇವೆ"},

    # ── COMPARE RESPONSE ────────────────────────────────────────────────────
    "state_comparison": {
        "en": "State Comparison",
        "hi": "राज्य तुलना",
        "kn": "ರಾಜ್ಯ ಹೋಲಿಕೆ",
    },
    "mandis":      {"en": "mandis", "hi": "मंडियाँ", "kn": "ಮಂಡಿಗಳು"},
    "sell_top_state": {
        "en": "_Sell in the top state for best returns!_",
        "hi": "_सबसे अच्छे दाम के लिए शीर्ष राज्य में बेचें!_",
        "kn": "_ಉತ್ತಮ ಆದಾಯಕ್ಕಾಗಿ ಮೊದಲ ರಾಜ್ಯದಲ್ಲಿ ಮಾರಿ!_",
    },

    # ── ERRORS ──────────────────────────────────────────────────────────────
    "no_data": {
        "en": "❌ No data found for {commodity}{state_part}.\n\nCheck spelling or try: tomato karnataka 1000",
        "hi": "❌ {commodity}{state_part} का कोई डेटा नहीं मिला।\n\nवर्तनी जाँचें या आज़माएं: टमाटर कर्नाटक 1000",
        "kn": "❌ {commodity}{state_part} ಗಾಗಿ ಯಾವುದೇ ಮಾಹಿತಿ ಸಿಗಲಿಲ್ಲ.\n\nಕ್ಕಾಗಿ ಪ್ರಯತ್ನಿಸಿ: ಟೊಮೆಟೊ ಕರ್ನಾಟಕ 1000",
    },
    "state_part_in": {
        "en": " in {state}",
        "hi": " में {state}",
        "kn": " ನಲ್ಲಿ {state}",
    },
    "invalid_price": {
        "en": "❌ Prices out of valid range for {commodity}.",
        "hi": "❌ {commodity} की कीमतें मान्य सीमा से बाहर हैं।",
        "kn": "❌ {commodity} ಬೆಲೆಗಳು ಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯ ಹೊರಗಿವೆ.",
    },
    "no_data_compare": {
        "en": "❌ No data found for {commodity}.",
        "hi": "❌ {commodity} का कोई डेटा नहीं मिला।",
        "kn": "❌ {commodity} ಗಾಗಿ ಯಾವುದೇ ಮಾಹಿತಿ ಸಿಗಲಿಲ್ಲ.",
    },
    "not_enough_compare": {
        "en": "❌ Not enough data to compare states for {commodity}.",
        "hi": "❌ {commodity} के लिए राज्यों की तुलना करने हेतु पर्याप्त डेटा नहीं है।",
        "kn": "❌ {commodity} ಗಾಗಿ ರಾಜ್ಯಗಳನ್ನು ಹೋಲಿಸಲು ಸಾಕಷ್ಟು ಮಾಹಿತಿ ಇಲ್ಲ.",
    },
    "didnt_understand": {
        "en": "🤔 Didn't understand that.\n\nTry: tomato karnataka 1000\nOr type: help",
        "hi": "🤔 समझ नहीं आया।\n\nयह आज़माएं: टमाटर कर्नाटक 1000\nया लिखें: मदद",
        "kn": "🤔 ಅರ್ಥವಾಗಲಿಲ್ಲ.\n\nಪ್ರಯತ್ನಿಸಿ: ಟೊಮೆಟೊ ಕರ್ನಾಟಕ 1000\nಅಥವಾ ಟೈಪ್ ಮಾಡಿ: ಸಹಾಯ",
    },
    "unknown_cmd": {
        "en": "❓ Unknown command. Type help.",
        "hi": "❓ अज्ञात कमांड। मदद लिखें।",
        "kn": "❓ ತಿಳಿಯದ ಆದೇಶ. ಸಹಾಯ ಎಂದು ಟೈಪ್ ಮಾಡಿ.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """
    Return translated string for key in lang ('en'|'hi'|'kn').
    Falls back to English if lang or key is missing.
    Supports {placeholder} substitution via kwargs.
    """
    lang = lang if lang in ("en", "hi", "kn") else "en"
    entry = _T.get(key, {})
    text  = entry.get(lang) or entry.get("en", f"[{key}]")
    return text.format(**kwargs) if kwargs else text


def localize_advice(advice: dict, lang: str) -> dict:
    """
    Translate the advice dict (label + trend) that price_analyzer returns
    into the user's language, leaving the structure intact.
    """
    label_key = {
        "SELL NOW":         "sell_now",
        "SELL IN 1-2 DAYS": "sell_soon",
        "WAIT":             "wait",
    }.get(advice["label"], "wait")

    trend_key = {
        "Prices are high":     "prices_high",
        "Prices are moderate": "prices_mod",
        "Prices are low":      "prices_low",
    }.get(advice["trend"], "prices_low")

    return {
        "label": t(label_key, lang),
        "trend": t(trend_key, lang),
        "emoji": advice["emoji"],
    }

# ---------------------------------------------------------------------------
# CURRENCY SYMBOL HELPER
# ---------------------------------------------------------------------------

def currency(lang: str) -> str:
    """
    Return the currency symbol appropriate for the user's language/region.
    English output uses the ₹ Unicode symbol (modern standard).
    Hindi and Kannada also use ₹ but 'Rs.' is kept for legacy SMS compat —
    override here if you want uniform ₹ everywhere.
    """
    return "₹"   # uniform ₹ across all languages (matches expected output)