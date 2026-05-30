import os
import ccxt
from dotenv import load_dotenv

def test_binance():
    # 1. Test keys from 트레이딩뷰 개발\.env
    load_dotenv(override=True)
    binance_key_1 = os.getenv("BINANCE_API_KEY")
    binance_secret_1 = os.getenv("BINANCE_SECRET_KEY")
    
    print("🧪 Testing Binance Keys Set 1 (from 트레이딩뷰 개발\\.env):")
    print(f"Key: {binance_key_1[:8]}...")
    try:
        exchange = ccxt.binanceusdm({
            'apiKey': binance_key_1,
            'secret': binance_secret_1,
            'enableRateLimit': True,
        })
        balance = exchange.fetch_balance()
        print("✅ SUCCESS with Set 1!")
        print(f"USDT Balance: {balance.get('USDT', {}).get('total', 0.0)}")
    except Exception as e:
        print(f"❌ FAILED with Set 1: {e}")

    # 2. Test keys from 빗썸 자동매매\.env
    print("\n🧪 Testing Binance Keys Set 2 (from 빗썸 자동매매\\.env):")
    load_dotenv(dotenv_path=r"D:\CDR_SynologyDrive\00_AI_AGENT\00_DEV\빗썸 자동매매\..env" if not os.path.exists(r"D:\CDR_SynologyDrive\00_AI_AGENT\00_DEV\빗썸 자동매매\.env") else r"D:\CDR_SynologyDrive\00_AI_AGENT\00_DEV\빗썸 자동매매\.env", override=True)
    binance_key_2 = os.getenv("BINANCE_API_KEY")
    binance_secret_2 = os.getenv("BINANCE_API_SECRET")
    print(f"Key: {binance_key_2[:8]}...")
    try:
        exchange = ccxt.binanceusdm({
            'apiKey': binance_key_2,
            'secret': binance_secret_2,
            'enableRateLimit': True,
            'options': {
                'adjustForTimeDifference': True,
                'recvWindow': 60000,
            }
        })
        balance = exchange.fetch_balance()
        print("✅ SUCCESS with Set 2!")
        print(f"USDT Balance: {balance.get('USDT', {}).get('total', 0.0)}")
    except Exception as e:
        print(f"❌ FAILED with Set 2: {e}")

if __name__ == "__main__":
    test_binance()
