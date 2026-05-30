import os
import ccxt
from dotenv import load_dotenv

def check_bithumb_assets():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("BITHUMB_API_KEY")
    secret_key = os.getenv("BITHUMB_SECRET_KEY")
    
    # Check for placeholder values
    if not api_key or not secret_key or "여기에" in api_key or "입력" in api_key:
        print("\n⚠️  [Bithumb Error] API Key is currently set to PLACEHOLDERS!")
        print("───────────────────────────────────────────────────")
        print("실제 빗썸 계정의 잔고를 확인하기 위해서는 아래 경로의 .env 파일에")
        print("실제 빗썸 Connect Key와 Secret Key를 입력해 주셔야 합니다.")
        print("👉 경로: D:\\CDR_SynologyDrive\\00_AI_AGENT\\00_DEV\\트레이딩뷰 개발\\.env")
        print("───────────────────────────────────────────────────\n")
        return
        
    try:
        # Initialize Bithumb exchange
        bithumb = ccxt.bithumb({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
        })
        
        print("\n🔄 [Bithumb] 빗썸 계정 잔고 조회 중...")
        balance = bithumb.fetch_balance()
        
        print("\n💰 [Bithumb 실시간 현물 자산 보유 현황]")
        print("───────────────────────────────────────────────────")
        
        # Display KRW Balance
        krw_total = balance.get('KRW', {}).get('total', 0.0)
        krw_free = balance.get('KRW', {}).get('free', 0.0)
        print(f"💵 원화 (KRW): {krw_total:,.0f} KRW (주문 가능: {krw_free:,.0f} KRW)")
        print("───────────────────────────────────────────────────")
        
        # Display non-zero crypto assets
        assets_found = False
        for currency, details in balance.items():
            if currency == 'info' or currency == 'free' or currency == 'used' or currency == 'total' or currency == 'KRW':
                continue
                
            total_amount = details.get('total', 0.0)
            if total_amount > 0.0001:  # Filter out tiny dust balances
                assets_found = True
                print(f"🪙 {currency:<6}: {total_amount:.6f} 개")
                
        if not assets_found:
            print("현재 보유 중인 암호화폐 현물 자산이 없습니다 (원화만 보유 중).")
            
        print("───────────────────────────────────────────────────\n")
        
    except Exception as e:
        print(f"\n🚨 [Bithumb API Error] 잔고 조회에 실패했습니다: {str(e)}")
        print("입력하신 API Key와 Secret Key가 유효하고 '조회' 권한이 켜져 있는지 확인해 주세요.\n")

if __name__ == "__main__":
    check_bithumb_assets()
