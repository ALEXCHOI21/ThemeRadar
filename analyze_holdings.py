import os
import ccxt
import numpy as np
from datetime import datetime

def calculate_ema(prices, period):
    if len(prices) < period:
        return np.mean(prices)
    multiplier = 2 / (period + 1)
    ema = np.mean(prices[:period])
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rsi = np.zeros_like(prices)
    if down == 0:
        return 100.0
    rs = up / down
    rsi = 100. - 100. / (1. + rs)
    
    # Calculate rest
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        if down == 0:
            rs = 100.0
        else:
            rs = up / down
        rsi_val = 100. - 100. / (1. + rs)
    return rsi_val

def analyze_coin(exchange, symbol):
    # Fetch Daily candles for long-term trend
    ohlcv_d = exchange.fetch_ohlcv(symbol, '1d', limit=100)
    closes_d = [c[4] for c in ohlcv_d]
    highs_d = [c[2] for c in ohlcv_d]
    lows_d = [c[3] for c in ohlcv_d]
    volumes_d = [c[5] for c in ohlcv_d]
    
    curr_price = closes_d[-1]
    change_24h = ((closes_d[-1] / closes_d[-2]) - 1) * 100
    
    # Technical Indicators (Daily)
    ema_50 = calculate_ema(closes_d, 50)
    ema_200 = calculate_ema(closes_d, 100) # use 100 if history is short, otherwise 200
    rsi = calculate_rsi(closes_d, 14)
    
    # Support & Resistance levels (Swing highs and lows)
    support = min(lows_d[-20:])
    resistance = max(highs_d[-20:])
    
    # Volume average
    avg_vol = np.mean(volumes_d[-20:])
    vol_spike = volumes_d[-1] / avg_vol if avg_vol > 0 else 1.0
    
    # Market Structure Analysis (Bison Style)
    # Are we in a bullish market structure (above 200 EMA)?
    trend = "BULLISH 📈" if curr_price > ema_200 else "BEARISH 📉"
    
    # Sweep detection
    swept_low = "NO"
    local_min_10 = min(lows_d[-10:-1])
    if lows_d[-1] < local_min_10 and closes_d[-1] > local_min_10:
        swept_low = "YES (Bullish Sweep ⚡)"
        
    return {
        "symbol": symbol,
        "price": curr_price,
        "change_24h": change_24h,
        "ema_50": ema_50,
        "ema_200": ema_200,
        "rsi": rsi,
        "support": support,
        "resistance": resistance,
        "vol_spike": vol_spike,
        "trend": trend,
        "swept_low": swept_low
    }

def run_analysis():
    exchange = ccxt.binanceusdm()
    
    print("\n🔍 Fetching latest market data for ONDO and LINK...")
    try:
        ondo_analysis = analyze_coin(exchange, "ONDO/USDT:USDT")
        link_analysis = analyze_coin(exchange, "LINK/USDT:USDT")
        
        # Save results to a json file in logs
        os.makedirs("logs", exist_ok=True)
        with open("logs/portfolio_market_analysis.json", "w", encoding="utf-8") as f:
            json.dump({
                "ONDO": ondo_analysis,
                "LINK": link_analysis,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
            
        print("✅ Analysis data written successfully.")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    import json
    run_analysis()
