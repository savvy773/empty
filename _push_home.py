import subprocess
import sys
import socket
import os
from datetime import datetime

# 컴퓨터 이름 or 유저명으로 위치 판별
# 아래 값을 각 PC에 맞게 수정하세요
LOCATION_MAP = {
    "main": "집",           # 집 PC 호스트명
    "Administrator": "집",  # 집 PC 유저명 (호스트명과 겹쳐도 OK)
    # "OFFICE-PC": "회사",  # 회사 PC 호스트명 (추후 추가)
    # "john": "회사",       # 회사 PC 유저명 (추후 추가)
}

def get_location():
    hostname = socket.gethostname()
    username = os.getlogin()
    print(f"  호스트명: {hostname} / 유저: {username}")
    return LOCATION_MAP.get(hostname) or LOCATION_MAP.get(username) or "알 수 없음"

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode

def main():
    location = get_location()
    message = sys.argv[1] if len(sys.argv) > 1 else f"[{location}] {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    print(f"위치: {location}")
    print(f"커밋 메시지: {message}")

    run("git add .")
    code = run(f'git commit -m "{message}"')
    if code != 0:
        print("커밋할 변경사항이 없거나 실패했습니다.")
        return

    code = run("git push origin main")
    if code == 0:
        print("푸쉬 완료!")
    else:
        print("푸쉬 실패. 위 오류를 확인하세요.")

if __name__ == "__main__":
    main()
