import os
import httpx
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str) -> bool:
    """
    Sends a styled HTML message to the Telegram bot channel.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Token or Chat ID is missing in configuration.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        if response.status_code == 200:
            print("[Telegram] Notification sent successfully.")
            return True
        else:
            print(f"[Telegram] Failed to send: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Error occurred: {str(e)}")
        return False

def send_telegram_photo(image_path: str, caption: str = "") -> bool:
    """
    Sends a card image with HTML caption to the Telegram bot channel.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Token or Chat ID is missing in configuration.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    try:
        if not os.path.exists(image_path):
            print(f"[Telegram] Photo file not found: {image_path}")
            return False
            
        with open(image_path, "rb") as f:
            files = {"photo": f}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            }
            response = httpx.post(url, data=data, files=files, timeout=25.0)
            
        if response.status_code == 200:
            print("[Telegram] Photo sent successfully.")
            return True
        else:
            print(f"[Telegram] Failed to send photo: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Error occurred while sending photo: {str(e)}")
        return False


# Self-test block
if __name__ == "__main__":
    test_msg = (
        "🔔 *[ChoiGPT Corp.] Bison Bot Online*\n"
        "───────────────────\n"
        "⚡ *Status:* Operational\n"
        "💎 *Engine:* Python FastAPI + CCXT\n"
        "🌐 *Target:* Binance Futures & Bithumb\n"
        "───────────────────\n"
        "✅ _Successfully connected to your private channel._"
    )
    send_telegram_message(test_msg)
