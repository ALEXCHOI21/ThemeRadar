import os
import sys
import json
import time
import uuid
import requests
import hashlib
import urllib.parse
from dotenv import load_dotenv

# Try importing PyJWT
try:
    import jwt
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "PyJWT"], stdout=subprocess.DEVNULL)
    import jwt

def get_secret(key: str, default: str = None) -> str:
    # Check Vault path if available
    VAULT_PATH = r"D:\CDR_SynologyDrive\10_업무\Internal_Library"
    if VAULT_PATH not in sys.path:
        sys.path.insert(0, VAULT_PATH)
    try:
        from backend.security.vault import SecretVault
        vault = SecretVault()
        val = vault.get(key)
        if val and val not in ("여기에_빗썸_Connect_Key_입력", "여기에_빗썸_Secret_Key_입력"):
            return val
    except Exception:
        pass
    return os.environ.get(key) or default or ""

def _headers_get(api_key, api_secret) -> dict:
    token = jwt.encode({
        "access_key": api_key,
        "nonce"     : str(uuid.uuid4()),
        "timestamp" : int(time.time() * 1000)
    }, api_secret, algorithm="HS256")
    return {"Authorization": "Bearer " + token}

def check_valuation():
    load_dotenv()
    
    api_key = get_secret("BITHUMB_API_KEY", os.getenv("BITHUMB_API_KEY"))
    api_secret = get_secret("BITHUMB_SECRET_KEY", os.getenv("BITHUMB_SECRET_KEY"))
    
    if not api_key or not api_secret:
        print("❌ Bithumb API keys not found in vault or .env!")
        return

    # 1. Fetch Accounts Info via OpenAPI v1
    try:
        headers = _headers_get(api_key, api_secret)
        r = requests.get("https://api.bithumb.com/v1/accounts", headers=headers, timeout=10)
        accounts = r.json()
        if isinstance(accounts, dict) and "error" in accounts:
            print(f"❌ API Error: {accounts['error']}")
            return
    except Exception as e:
        print(f"❌ Failed to fetch accounts: {e}")
        return

    # 2. Fetch Public Tickers to get current prices
    try:
        ticker_data = requests.get("https://api.bithumb.com/public/ticker/ALL_KRW", timeout=10).json()
        tickers = ticker_data.get("data", {}) if ticker_data.get("status") == "0000" else {}
    except Exception as e:
        print(f"⚠️ Failed to fetch current prices: {e}")
        tickers = {}

    print("\n💎 [ChoiGPT Bithumb Real-Time Spot Asset Valuation]")
    print("=" * 70)
    print(f"{'Asset':<8} | {'Amount':<18} | {'Current Price':<14} | {'Valuation (KRW)':<18}")
    print("-" * 70)

    total_krw_valuation = 0.0
    krw_balance = 0.0

    # Display KRW first if it exists
    for acc in accounts:
        currency = acc.get("currency")
        balance = float(acc.get("balance", 0.0))
        if currency == "KRW":
            krw_balance = balance
            total_krw_valuation += balance
            print(f"💵 KRW    | {balance:>18,.2f} | {'1.00 KRW':<14} | {balance:>18,.0f} KRW")

    # Display crypto assets
    for acc in accounts:
        currency = acc.get("currency")
        if currency == "KRW":
            continue
            
        balance = float(acc.get("balance", 0.0))
        if balance < 1e-6: # ignore trace dust
            continue
            
        # Get current price
        price = 0.0
        if currency in tickers:
            price = float(tickers[currency].get("closing_price", 0.0))
        elif currency == "USDT":
            # standard USD rate if USDT ticker fails
            price = 1477.0
            
        valuation = balance * price
        
        # Format and skip tiny valuations (less than 10 KRW) to keep it clean, except major holdings
        if valuation < 10.0 and balance < 0.1:
            continue
            
        total_krw_valuation += valuation
        
        price_str = f"{price:,.2f} KRW" if price > 0 else "N/A"
        val_str = f"{valuation:,.0f} KRW" if price > 0 else "N/A"
        
        print(f"🪙 {currency:<7} | {balance:>18.6f} | {price_str:<14} | {val_str:>18}")

    print("=" * 70)
    print(f"💰 총 평가 자산 (Total Assets Valuation): {total_krw_valuation:,.0f} KRW")
    print(f"💳 보유 현금 (KRW Balance)           : {krw_balance:,.0f} KRW")
    print(f"📈 주식/코인 평가액 (Crypto Valuation) : {(total_krw_valuation - krw_balance):,.0f} KRW")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    check_valuation()
