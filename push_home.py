import subprocess
import sys
from datetime import datetime

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode

def main():
    message = sys.argv[1] if len(sys.argv) > 1 else f"[집] {datetime.now().strftime('%Y-%m-%d %H:%M')}"

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
