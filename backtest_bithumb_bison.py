import os
import requests
import numpy as np
import pandas as pd
from datetime import datetime

def calculate_ema(prices, period=200):
    if len(prices) < period:
        return [np.mean(prices)] * len(prices)
    ema = [np.mean(prices[:period])] * period
    multiplier = 2 / (period + 1)
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema

def calculate_sma(values, period=20):
    if len(values) < period:
        return [np.mean(values)] * len(values)
    sma = [np.mean(values[:period])] * period
    for i in range(period, len(values)):
        sma.append(np.mean(values[i-period+1:i+1]))
    return sma

def fetch_bithumb_ohlcv(symbol, interval="1h", limit=1000):
    """
    Fetches historical candles from Bithumb public API.
    Bithumb returns: [Time, Open, Close, High, Low, Volume]
    """
    try:
        url = f"https://api.bithumb.com/public/candlestick/{symbol}_KRW/{interval}"
        r = requests.get(url, timeout=10).json()
        if r.get("status") != "0000":
            return None
        
        # Bithumb returns up to 2500 candles. Slice to get the latest 'limit'
        data = r["data"][-limit:]
        
        df = pd.DataFrame(data, columns=["timestamp", "open", "close", "high", "low", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
        for col in ["open", "close", "high", "low", "volume"]:
            df[col] = df[col].astype(float)
            
        return df
    except Exception as e:
        print(f"Error fetching {symbol} from Bithumb: {e}")
        return None

def run_bison_backtest(df, symbol, initial_capital=42885978):
    if df is None or len(df) < 250:
        return None
        
    closes = df["close"].tolist()
    highs = df["high"].tolist()
    lows = df["low"].tolist()
    volumes = df["volume"].tolist()
    times = df["timestamp"].tolist()
    
    # 1. Technical Indicators
    ema_200 = calculate_ema(closes, 200)
    vol_sma_20 = calculate_sma(volumes, 20)
    
    capital = initial_capital
    position = 0
    trades = []
    
    pos_ratio = 0.15  # Use 15% of equity per trade
    sl_pct = 0.015    # 1.5% Stop Loss
    rr_ratio = 2.0    # 1:2.0 Risk-to-Reward
    tp_pct = sl_pct * rr_ratio # 3.0% Take Profit
    
    in_trade = False
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    trade_size_krw = 0.0
    trade_volume = 0.0
    entry_time = None
    
    for i in range(200, len(df)):
        # If in trade, check for SL or TP
        if in_trade:
            curr_low = lows[i]
            curr_high = highs[i]
            curr_close = closes[i]
            
            # Check Stop Loss
            if curr_low <= sl_price:
                # Sell at SL price
                exit_price = sl_price
                pnl_krw = trade_volume * (exit_price - entry_price)
                capital += pnl_krw
                trades.append({
                    "type": "SELL (SL)",
                    "entry_time": entry_time,
                    "exit_time": times[i],
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl_krw": pnl_krw,
                    "pnl_pct": -sl_pct * 100,
                    "capital_after": capital
                })
                in_trade = False
                continue
                
            # Check Take Profit
            elif curr_high >= tp_price:
                # Sell at TP price
                exit_price = tp_price
                pnl_krw = trade_volume * (exit_price - entry_price)
                capital += pnl_krw
                trades.append({
                    "type": "SELL (TP)",
                    "entry_time": entry_time,
                    "exit_time": times[i],
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl_krw": pnl_krw,
                    "pnl_pct": tp_pct * 100,
                    "capital_after": capital
                })
                in_trade = False
                continue
                
            # Optional Time Cut (48 hours)
            elif (times[i] - entry_time).total_seconds() / 3600 >= 48:
                exit_price = curr_close
                pnl_krw = trade_volume * (exit_price - entry_price)
                capital += pnl_krw
                trades.append({
                    "type": "SELL (TimeCut)",
                    "entry_time": entry_time,
                    "exit_time": times[i],
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl_krw": pnl_krw,
                    "pnl_pct": ((exit_price / entry_price) - 1) * 100,
                    "capital_after": capital
                })
                in_trade = False
                continue
                
        # If not in trade, look for Bison entry signal
        else:
            curr_close = closes[i]
            curr_low = lows[i]
            curr_high = highs[i]
            curr_vol = volumes[i]
            
            # A. Trend Filter: Above 200 EMA
            is_bullish = curr_close > ema_200[i]
            
            # B. Institutional Volume Filter: Volume > 20 SMA Volume
            vol_ok = curr_vol > vol_sma_20[i]
            
            # C. Bullish Sweep Filter:
            # Low swept the minimum low of the past 10 candles, but closed above it
            past_10_lows = lows[i-10:i]
            local_support = min(past_10_lows)
            
            is_sweep = curr_low < local_support and curr_close > local_support
            
            if is_bullish and vol_ok and is_sweep:
                in_trade = True
                entry_price = curr_close
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                
                trade_size_krw = capital * pos_ratio
                trade_volume = trade_size_krw / entry_price
                entry_time = times[i]
                
    # Summary Metrics
    total_trades = len(trades)
    win_trades = [t for t in trades if t["pnl_krw"] > 0]
    loss_trades = [t for t in trades if t["pnl_krw"] <= 0]
    
    win_count = len(win_trades)
    loss_count = len(loss_trades)
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
    
    total_pnl_krw = capital - initial_capital
    roi_pct = (total_pnl_krw / initial_capital) * 100
    
    # Calculate Profit Factor
    gross_profits = sum([t["pnl_krw"] for t in win_trades])
    gross_losses = abs(sum([t["pnl_krw"] for t in loss_trades]))
    profit_factor = gross_profits / gross_losses if gross_losses > 0 else float('inf')
    
    return {
        "symbol": symbol,
        "total_trades": total_trades,
        "win_count": win_count,
        "loss_count": loss_count,
        "win_rate": win_rate,
        "initial_capital": initial_capital,
        "final_capital": capital,
        "net_profit_krw": total_pnl_krw,
        "roi_pct": roi_pct,
        "profit_factor": profit_factor,
        "trades": trades
    }

def main():
    print("🔋 Starting Bithumb Bison v6.2 Strategy Backtest...")
    initial_cap = 42885978 # Alex's actual capital!
    
    # 1. Fetch data for ONDO and LINK
    print("📥 Downloading OHLCV data from Bithumb (1-hour candles)...")
    ondo_df = fetch_bithumb_ohlcv("ONDO", "1h", limit=1500)
    link_df = fetch_bithumb_ohlcv("LINK", "1h", limit=1500)
    
    # 2. Run Backtests
    print("📈 Running Backtest simulations...")
    ondo_res = run_bison_backtest(ondo_df, "ONDO/KRW", initial_cap)
    link_res = run_bison_backtest(link_df, "LINK/KRW", initial_cap)
    
    # Write report
    report_file = "logs/bithumb_bison_backtest_report.md"
    os.makedirs("logs", exist_ok=True)
    
    report_md = (
        f"# 📒 Bithumb Bison v6.2 백테스트 정량 분석 보고서\n\n"
        f"본 보고서는 **ChoiGPT Corp. 수석 전략가 Alex**의 실제 보유 원화 예수금인 **42,885,978 KRW**을 기준 원금으로 설정하고, "
        f"빗썸의 최신 1,500개 1시간봉(1h) 데이터를 기반으로 **Bison v6.2 알고리즘**을 모의 시뮬레이션한 결과입니다.\n\n"
        f"---\n\n"
        f"## 🛠️ 백테스트 기준 매매 규칙 (Bison Rules)\n"
        f"*   **추세 필터 (Trend Filter)**: 일봉/4시간 200 EMA 상단에 안착한 상승 국면\n"
        f"*   **타점 트리거 (Trigger)**: 직전 10개 캔들의 저점을 하방 이탈 후 종가 기준으로 다시 지지선 위로 회복한 스윕 (Bullish Sweep)\n"
        f"*   **기관 거래량 필터**: 20일 거래량 이동평균선 상방 돌파 (`Volume > Volume SMA 20`)\n"
        f"*   **자금 관리 (Money Management)**: 가용 예수금의 **15%** 고정 비중 투입 (`POS_RATIO = 0.15`)\n"
        f"*   **손익비 관리 (R:R Ratio)**: **1.5% 고정 손절 (SL)** 대 **3.0% 익절 목표 (TP)** (수수료 슬리피지 배제, 1:2 손익비)\n"
        f"*   **시간 컷 (Time Cut)**: 진입 후 **48시간** 동안 청산이 안 될 경우 종가 기준 타임컷 강제 청산\n\n"
        f"---\n\n"
    )
    
    for res in [ondo_res, link_res]:
        if not res:
            continue
            
        report_md += (
            f"## 📊 {res['symbol']} 백테스트 요약 결과\n"
            f"*   **시작 원금 (Initial Capital)**: `{res['initial_capital']:,.0f} KRW`\n"
            f"*   **최종 평가금 (Final Capital)**: `{res['final_capital']:,.0f} KRW`\n"
            f"*   **총 누적 수익 (Net Profit)**: **`{res['net_profit_krw']:+,.0f} KRW`**\n"
            f"*   **수익률 (ROI)**: **`{res['roi_pct']:+.2f}%`**\n"
            f"*   **총 거래 횟수 (Total Trades)**: `{res['total_trades']}회`\n"
            f"*   **승률 (Win Rate)**: **`{res['win_rate']:.1f}%`** ({res['win_count']}승 / {res['loss_count']}패)\n"
            f"*   **프로핏 팩터 (Profit Factor)**: `{res['profit_factor']:.2f}`\n\n"
            f"### 📝 최근 체결 거래 내역 (Latest Trades)\n"
            f"| 구분 | 진입 시각 | 청산 시각 | 진입가 | 청산가 | 손익률 | 평가 잔액 (KRW) |\n"
            f"|---|---|---|---|---|---|---|\n"
        )
        
        # Display latest 10 trades
        for t in res["trades"][-10:]:
            emoji = "🟢" if "TP" in t["type"] else ("🔴" if "SL" in t["type"] else "⚪")
            report_md += (
                f"| {emoji} {t['type']} | {t['entry_time'].strftime('%m-%d %H:%M')} | "
                f"{t['exit_time'].strftime('%m-%d %H:%M')} | {t['entry_price']:,.2f} | "
                f"{t['exit_price']:,.2f} | {t['pnl_pct']:+.2f}% | {t['capital_after']:,.0f} |\n"
            )
            
        report_md += "\n---\n\n"
        
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"✅ Backtest completed. Full report saved to {report_file}")
    
    # Also output summary to console
    for res in [ondo_res, link_res]:
        if res:
            print(f"\n📈 Summary for {res['symbol']}:")
            print(f"  • Net Profit: {res['net_profit_krw']:+,.0f} KRW ({res['roi_pct']:+.2f}%)")
            print(f"  • Win Rate: {res['win_rate']:.1f}% ({res['win_count']}W / {res['loss_count']}L)")
            print(f"  • Profit Factor: {res['profit_factor']:.2f}")

if __name__ == "__main__":
    main()
