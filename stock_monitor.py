import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz

PRODUCT_URL = "https://shop.weverse.io/ko/shop/KRW/artists/155/sales/44783"
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def get_kst_time():
    """한국 시간을 반환하는 함수"""
    return datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')

def check_stock():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(PRODUCT_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text()
        
        if "품절" not in page_text and "sold out" not in page_text.lower():
            return True
        return False
    except Exception as e:
        print(f"체크 중 에러: {e}")
        return False

def send_discord_message(msg):
    if not WEBHOOK_URL:
        print("웹훅 URL이 없습니다!")
        return False
        
    data = {"content": msg}
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 204:
            print("디스코드 알림 전송 완료!")
            return True
        else:
            print(f"알림 전송 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"알림 전송 에러: {e}")
        return False

def main():
    current_time = get_kst_time()  # KST 시간 사용
    print(f"[{current_time}] 재고 확인 시작...")
    
    in_stock = check_stock()
    
    if in_stock:
        success_msg = f"🚨 **재고 알림!** 🚨\n\n" \
                     f"✅ **상품 재고가 풀렸습니다!**\n\n" \
                     f"🔗 **바로 구매하기**: {PRODUCT_URL}\n\n" \
                     f"⏰ 발견 시간: {current_time}\n" \
                     f"🏃‍♂️ **빠르게 구매하세요!**"
        
        send_discord_message(success_msg)
        print("🎉 재고 발견! 알림 전송!")
    else:
        print("⏳ 아직 품절 상태입니다.")

if __name__ == "__main__":
    main()
