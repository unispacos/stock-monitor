import requests
import os
from datetime import datetime
import pytz

WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')
KST = pytz.timezone('Asia/Seoul')

def get_kst_time_str():
    return datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')

def test_webhook():
    print(f"현재 시간: {get_kst_time_str()}")
    print(f"웹훅 URL 존재 여부: {'있음' if WEBHOOK_URL else '없음'}")
    
    if not WEBHOOK_URL:
        print("❌ 웹훅 URL이 설정되지 않았습니다!")
        print("GitHub Secrets에 DISCORD_WEBHOOK를 확인하세요.")
        return False
    
    # 웹훅 URL 일부만 출력 (보안)
    masked_url = WEBHOOK_URL[:50] + "..." + WEBHOOK_URL[-10:] if len(WEBHOOK_URL) > 60 else WEBHOOK_URL
    print(f"웹훅 URL (일부): {masked_url}")
    
    test_msg = f"🧪 **GitHub Actions 웹훅 테스트**\n\n" \
               f"⏰ 테스트 시간: {get_kst_time_str()}\n" \
               f"✅ GitHub Actions에서 디스코드 연결 성공!\n" \
               f"🤖 자동 재고 모니터링 준비 완료!"
    
    try:
        response = requests.post(WEBHOOK_URL, json={"content": test_msg}, timeout=10)
        
        if response.status_code == 204:
            print("✅ 디스코드 알림 전송 성공!")
            return True
        else:
            print(f"❌ 디스코드 알림 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 웹훅 전송 에러: {e}")
        return False

if __name__ == "__main__":
    print("=== GitHub Actions 웹훅 테스트 ===")
    test_webhook()
