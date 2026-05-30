import os
import ccxt
import numpy as np

def check_relative_strength(exchange, symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=100)
        closes = [c[4] for c in ohlcv]
        highs = [c[2] for c in ohlcv]
        lows = [c[3] for c in ohlcv]
        
        curr_price = closes[-1]
        change_24h = ((closes[-1] / closes[-2]) - 1) * 100
        change_7d = ((closes[-1] / closes[-8]) - 1) * 100 if len(closes) >= 8 else 0.0
        change_30d = ((closes[-1] / closes[-31]) - 1) * 100 if len(closes) >= 31 else 0.0
        
        # Simple trend metric: price relative to 50-day EMA
        multiplier = 2 / 51
        ema_50 = closes[0]
        for p in closes[1:]:
            ema_50 = (p - ema_50) * multiplier + ema_50
            
        trend_status = "BULLISH 📈" if curr_price > ema_50 else "BEARISH 📉"
        
        return {
            "symbol": symbol,
            "price": curr_price,
            "change_24h": change_24h,
            "change_7d": change_7d,
            "change_30d": change_30d,
            "trend": trend_status,
            "ema_50": ema_50
        }
    except Exception as e:
        return None

def analyze_theme():
    exchange = ccxt.binanceusdm()
    
    # Selected elite Web3 Cryptographic Co-processors & Privacy-AI Infrastructure coins
    candidates = [
        "ROSE/USDT:USDT",  # Oasis Network (TEE & Privacy EVM, decentralized AI privacy)
        "ARPA/USDT:USDT",  # ARPA Chain (Secure Multi-Party Computation MPC)
        "PHA/USDT:USDT",   # Phala Network (Decentralized TEE Coprocessor for AI)
        "SCRT/USDT:USDT",  # Secret Network (Confidential Computing L1, FHE partnership)
        "DUSK/USDT:USDT",  # Dusk Network (ZK-based Privacy L1)
        "ICP/USDT:USDT",   # Internet Computer (Threshold Cryptography L1)
    ]
    
    print("\n🔍 Running relative strength scan on Cryptographic & Privacy-AI Infrastructure theme...")
    results = []
    for c in candidates:
        res = check_relative_strength(exchange, c)
        if res:
            results.append(res)
            
    # Sort by 7-day change to find the strongest ones (showing RS like ZAMA)
    results = sorted(results, key=lambda x: x["change_7d"], reverse=True)
    
    import json
    os.makedirs("logs", exist_ok=True)
    with open("logs/cryptography_theme_recommendations.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("✅ Analysis completed successfully.")

if __name__ == "__main__":
    analyze_theme()
