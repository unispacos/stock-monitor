import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime, timedelta, timezone

PRODUCT_URL = "https://shop.weverse.io/ko/shop/KRW/artists/155/sales/44783"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")  # GitHub Secrets에서 불러옴

KST = timezone(timedelta(hours=9))  # KST 기준
OPER_START = 9   # 오전 9시 운영 시작
OPER_END = 23    # 오후 11시 운영 종료

def check_stock():
    try:
        response = requests.get(PRODUCT_URL, timeout=20)
        response.raise_for_status()
    except Exception as e:
        send_discord_message(f"⚠️ [에러] 페이지 요청 실패: {e}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    return "품절" not in soup.get_text()

def send_discord_message(msg):
    if not WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK 환경변수가 설정되지 않았습니다.")
        return
    try:
        data = {"content": msg}
        r = requests.post(WEBHOOK_URL, json=data, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ 알림 전송 실패: {e}")

if __name__ == "__main__":
    # 최초 실행 알림
    send_discord_message("📢 [알림] 모니터링 프로그램을 시작합니다. (KST 기준)")

    last_status = None
    last_oper_day = None
    last_heartbeat = datetime.now(KST)

    while True:
        now = datetime.now(KST)
        hour = now.hour
        in_oper = OPER_START <= hour < OPER_END

        # 운영 시작 알림
        if in_oper and last_oper_day != now.date():
            send_discord_message(f"✅ [운영시작] {now.strftime('%Y-%m-%d %H:%M')} 모니터링 시작합니다.")
            last_oper_day = now.date()
            last_heartbeat = now

        # 운영 종료 알림
        if not in_oper and last_oper_day == now.date():
            send_discord_message(f"🛑 [운영종료] {now.strftime('%Y-%m-%d %H:%M')} 모니터링 종료합니다.")
            last_oper_day = None

        # 운영시간 내 모니터링
        if in_oper:
            in_stock = check_stock()
            if in_stock is None:
                pass  # 요청 실패 시 스킵
            elif in_stock and last_status != "in_stock":
                send_discord_message("🚨 상품 재고가 풀렸습니다! 👉 " + PRODUCT_URL)
                last_status = "in_stock"
            elif not in_stock:
                last_status = "sold_out"

            # 2시간마다 heartbeat 알림
            if now - last_heartbeat >= timedelta(hours=2):
                send_discord_message(f"⏰ [정상작동중] {now.strftime('%H:%M')} - 모니터링 정상 진행 중입니다.")
                last_heartbeat = now

        time.sleep(60)  # 1분 간격으로 체크
