"""
HarvestSmart - WhatsApp Smart Assistant for Farmers
Main Flask Application
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from message_handler import handle_message
from dotenv import load_dotenv
import logging

load_dotenv()  # ← Load .env BEFORE anything else reads env vars

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    """Twilio WhatsApp webhook endpoint."""
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    logger.info(f"Message from {sender}: {incoming_msg}")

    try:
        response_text = handle_message(incoming_msg, sender)
    except Exception as e:
        logger.exception(f"Error handling message: {e}")
        response_text = "⚠️ Something went wrong on our end. Please try again in a moment."

    logger.info(f"Response: {response_text[:100]}...")

    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "HarvestSmart"}, 200


@app.route("/test", methods=["GET"])
def test():
    """Quick test: /test?msg=tomato+karnataka+1000"""
    msg = request.args.get("msg", "help")
    result = handle_message(msg, "test_user")
    return {"input": msg, "response": result}, 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
