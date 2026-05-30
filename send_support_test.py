# -*- coding: utf-8 -*-
from telegram_bot import send_telegram_message

def main():
    test_msg = (
        "🛡️ *[ChoiGPT Portfolio Guardian] 실시간 모니터링 활성화*\n"
        "───────────────────\n"
        "💎 *감시 대상 자산 및 실시간 지지선:*\n"
        "  • *ONDO* (온도파이낸스) | 지지라인: `0.3327 USD` (빗썸 약 `490` 원)\n"
        "  • *LINK* (체인링크) | 지지라인: `9.034 USD` (빗썸 약 `13,300` 원)\n\n"
        "📊 *동작 상태:* 24시간 백그라운드 스캔 작동 중\n"
        "🔥 *경보 설정:* 위 지지선 이탈 또는 특이사항(급격한 거래량 동반 폭락) 발생 시 즉시 스마트폰 사이렌 알림 발송\n"
        "───────────────────\n"
        "✅ _Alex님의 빗썸 포트폴리오 감시망 작동을 성공적으로 시작합니다._"
    )
    send_telegram_message(test_msg)

if __name__ == "__main__":
    main()
