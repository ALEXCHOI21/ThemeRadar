import os
import ccxt
import base64
from dotenv import load_dotenv

def test():
    load_dotenv()
    api_key = os.getenv("BITHUMB_API_KEY")
    secret_key = os.getenv("BITHUMB_SECRET_KEY")
    
    # Try decoding the base64 secret key
    try:
        decoded_secret = base64.b64decode(secret_key).decode('utf-8')
        print(f"Decoded Secret Key: {decoded_secret}")
    except Exception as e:
        print(f"Failed to decode secret key as base64 utf-8: {e}")
        decoded_secret = secret_key

    # Initialize CCXT with decoded secret
    print("\n1. Testing with Decoded Secret...")
    try:
        bithumb = ccxt.bithumb({
            'apiKey': api_key,
            'secret': decoded_secret,
            'enableRateLimit': True,
        })
        balance = bithumb.fetch_balance()
        print("✅ SUCCESS with Decoded Secret!")
        print(f"KRW Balance: {balance.get('KRW', {}).get('total', 0.0)}")
        return
    except Exception as e:
        print(f"❌ FAILED with Decoded Secret: {e}")

    # Initialize CCXT with raw secret
    print("\n2. Testing with Raw Secret (from .env)...")
    try:
        bithumb = ccxt.bithumb({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
        })
        balance = bithumb.fetch_balance()
        print("✅ SUCCESS with Raw Secret!")
        print(f"KRW Balance: {balance.get('KRW', {}).get('total', 0.0)}")
        return
    except Exception as e:
        print(f"❌ FAILED with Raw Secret: {e}")

if __name__ == "__main__":
    test()
