# 🌾 HarvestSmart

> WhatsApp-based smart assistant that helps farmers make better selling decisions using real-time government mandi (market) data.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 Smart Price Analysis | Median price across mandis, converted to ₹/kg |
| 🏆 Best Mandi | Highlights the highest-paying market |
| 🌍 State Comparison | Top 5 states ranked by median price |
| 💵 Profit Calculator | Estimated revenue for your quantity |
| 📈 Sell Advice | SELL NOW / SELL SOON / WAIT based on national distribution |
| 🔒 Blockchain Log | Every query is hash-logged for traceability |
| 🔄 Real-Time Translation Core | Instant understanding across languages |

---

## 🗂️ Project Structure

```
harvestsmart/
├── app.py              # Flask webhook server (Twilio entry point)
├── message_handler.py  # Parses WhatsApp messages, builds responses
├── mandi_api.py        # Fetches live data from data.gov.in (Agmarknet)
├── price_analyzer.py   # Median, best mandi, state comparison, advice
├── blockchain.py       # Lightweight SHA-256 chain logger
├── requirements.txt
├── .env.example
└── harvest_chain.json  # Auto-created on first run
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone <your-repo>
cd harvestsmart
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your Twilio credentials and data.gov.in API key
```

### 3. Run the server

```bash
python app.py
```

### 4. Expose with ngrok

```bash
ngrok http 5000
# Copy the HTTPS URL, e.g. https://abc123.ngrok.io
```

### 5. Configure Twilio Sandbox

1. Go to [Twilio Console → Messaging → Try it Out → WhatsApp](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Set **Webhook URL** → `https://abc123.ngrok.io/webhook`
3. Method: **HTTP POST**
4. Join the sandbox by WhatsApp: `join <your-sandbox-code>`

---

## 💬 How to Use (Farmer Messages)

### Basic query

```
tomato karnataka 1000
```

→ Fetches tomato prices in Karnataka, analyses 1000 kg, gives sell advice.

### Compare all states

```
compare onion
```

→ Shows top 5 states for onion prices nationwide.

### Help

```
help
```

→ Shows usage instructions.

---

## 📡 Data Source

- **API**: [data.gov.in – Agmarknet Daily Prices](https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070)
- **Coverage**: ~3,000+ mandis across India
- **Update frequency**: Daily
- **API Key**: Register free at [data.gov.in](https://data.gov.in)

---

## 🧠 Sell Advice Logic

| Condition | Advice |
|---|---|
| Median ≥ 75th percentile (national) | 📈 SELL NOW |
| Median ≤ 35th percentile (national) | 📉 WAIT |
| Between | ⚖️ SELL SOON |

---

## 🔒 Blockchain Logging

Each query creates a new block with:
- Anonymized sender ID (last 4 digits)
- Commodity, state, quantity
- Median price & advice
- SHA-256 hash linked to previous block

The chain is stored in `harvest_chain.json` and validated on every write.

---

## 🧪 Testing Without WhatsApp

You can test the logic directly:

```python
from message_handler import handle_message

print(handle_message("tomato karnataka 1000", "whatsapp:+91XXXXXXXXXX"))
print(handle_message("compare onion", "whatsapp:+91XXXXXXXXXX"))
```

Or hit the Flask webhook locally with curl:

```bash
curl -X POST http://localhost:5000/webhook \
  -d "Body=tomato karnataka 1000" \
  -d "From=whatsapp:+919999999999"
```

---

## 🏆 Impact

> *HarvestSmart empowers farmers with real-time price intelligence, helping them maximize profits and make smarter selling decisions — directly on WhatsApp, no app needed.*

---

## 📋 Supported Crops

tomato · onion · potato · wheat · rice · maize · cotton · chilli · banana · mango · groundnut · soybean · sugarcane

## 📋 Supported States

Karnataka · Maharashtra · Gujarat · Rajasthan · Punjab · Haryana · Tamil Nadu · Andhra Pradesh · Telangana · Kerala · Bihar · West Bengal · Odisha · Chhattisgarh · Uttar Pradesh · Madhya Pradesh
